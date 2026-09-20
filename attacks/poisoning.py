"""
=============================================================================
ADVERSARIAL POISONING ATTACKS & ROBUST AGGREGATION BASELINES
Module: attacks/poisoning.py
-----------------------------------------------------------------------------
Implements:
1. Label-flipping attack on local client telemetry.
2. Sign-flip / scaled model replacement attack (Δw_mal = -λ * Δw).
3. Robust Aggregation Baselines:
   - Undefended FedAvg
   - Coordinate-wise Median (Yin et al. 2018)
   - Trimmed Mean (β = 0.2, Yin et al. 2018)
   - Multi-Krum (Blanchard et al. 2017)
   - Cosine-Similarity Adaptive Trust Scorer (wired into aggregation)
=============================================================================
"""

import copy
from typing import Dict, List, Tuple, Optional
import numpy as np
import torch
from layer2_detection.secure_aggregation import CosineTrustScorer


def apply_label_flip(y: np.ndarray) -> np.ndarray:
    """Inverts binary classification labels (0 -> 1, 1 -> 0)."""
    return 1 - y


def apply_sign_flip_scaled(delta_w: Dict[str, torch.Tensor], scale: float = 5.0) -> Dict[str, torch.Tensor]:
    """Generates an adversarial scaled model replacement update: Δw_mal = -λ * Δw."""
    poisoned = {}
    for k, v in delta_w.items():
        if "running_" in k or "num_batches" in k:
            poisoned[k] = v.clone()
        else:
            poisoned[k] = -scale * v.clone().float()
    return poisoned


def aggregate_fedavg(client_updates: List[Dict[str, torch.Tensor]], weights: Optional[List[float]] = None) -> Dict[str, torch.Tensor]:
    """Standard (undefended) FedAvg parameter update aggregation."""
    n = len(client_updates)
    if n == 0:
        return {}
    if weights is None:
        weights = [1.0 / n] * n
    else:
        total_w = sum(weights)
        weights = [w / total_w for w in weights]

    aggregated = {}
    for k in client_updates[0].keys():
        accum = torch.zeros_like(client_updates[0][k], dtype=torch.float32)
        for i in range(n):
            accum += weights[i] * client_updates[i][k].float()
        aggregated[k] = accum
    return aggregated


def aggregate_coordinate_median(client_updates: List[Dict[str, torch.Tensor]]) -> Dict[str, torch.Tensor]:
    """Coordinate-wise median robust aggregation (Yin et al., ICML 2018)."""
    aggregated = {}
    for k in client_updates[0].keys():
        stacked = torch.stack([u[k].float() for u in client_updates], dim=0)
        aggregated[k] = torch.median(stacked, dim=0).values
    return aggregated


def aggregate_trimmed_mean(client_updates: List[Dict[str, torch.Tensor]], beta: float = 0.2) -> Dict[str, torch.Tensor]:
    """Trimmed mean robust aggregation trimming top and bottom beta fraction (Yin et al., 2018)."""
    n = len(client_updates)
    k_trim = int(n * beta)
    aggregated = {}

    for k in client_updates[0].keys():
        stacked = torch.stack([u[k].float() for u in client_updates], dim=0)
        # Sort along client dimension
        sorted_tensors, _ = torch.sort(stacked, dim=0)
        if 2 * k_trim < n:
            trimmed = sorted_tensors[k_trim : n - k_trim]
            aggregated[k] = torch.mean(trimmed, dim=0)
        else:
            aggregated[k] = torch.median(sorted_tensors, dim=0).values

    return aggregated


def aggregate_multi_krum(
    client_updates: List[Dict[str, torch.Tensor]],
    num_malicious: int = 2,
    m: int = 1
) -> Dict[str, torch.Tensor]:
    """
    Multi-Krum Byzantine-resilient aggregation (Blanchard et al., NeurIPS 2017).
    Selects updates minimizing the sum of squared Euclidean distances to the closest
    n - f - 2 neighbors.
    """
    n = len(client_updates)
    if n <= 2:
        return aggregate_fedavg(client_updates)

    # Flatten updates to 1D vectors
    vectors = [torch.cat([u[k].flatten().float() for k in u.keys()]) for u in client_updates]
    stacked = torch.stack(vectors, dim=0)  # [n, D]

    # Distance matrix
    dists = torch.cdist(stacked, stacked, p=2) ** 2  # [n, n]

    # For each client, sum distances to n - f - 2 closest neighbors
    nb_neighbors = max(1, n - num_malicious - 2)
    krum_scores = []
    for i in range(n):
        sorted_dists, _ = torch.sort(dists[i])
        # Skip distance to self (0.0 at index 0)
        score = sorted_dists[1 : nb_neighbors + 1].sum().item()
        krum_scores.append((score, i))

    # Pick top m candidates with lowest score
    krum_scores.sort(key=lambda x: x[0])
    selected_indices = [idx for _, idx in krum_scores[:m]]

    selected_updates = [client_updates[i] for i in selected_indices]
    return aggregate_fedavg(selected_updates)


def aggregate_cosine_trust(
    client_updates: List[Dict[str, torch.Tensor]],
    trust_scorer: CosineTrustScorer,
    client_indices: List[int]
) -> Tuple[Dict[str, torch.Tensor], np.ndarray]:
    """
    Cosine-Similarity Adaptive Trust Aggregation.
    Updates trust weights dynamically and aggregates updates using trust-weighted averaging.
    """
    trust_scores = trust_scorer.update_trust(client_updates, participating_indices=client_indices)
    participating_trust = [trust_scores[cid] for cid in client_indices]

    aggregated = aggregate_fedavg(client_updates, weights=participating_trust)
    return aggregated, trust_scores
