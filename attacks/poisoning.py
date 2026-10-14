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


def apply_alie_attack(
    benign_updates: List[Dict[str, torch.Tensor]],
    num_total_clients: int,
    num_malicious: int
) -> Dict[str, torch.Tensor]:
    """
    A Little Is Enough (ALIE) attack (Baruch et al., NeurIPS 2019).
    Calculates coordinate-wise mean and std of benign updates and perturbs
    by -z_max * std, staying stealthy under coordinate-wise robust rules.
    """
    import scipy.stats as st
    n = num_total_clients
    m = num_malicious
    s = max(1, int(np.floor(n / 2.0 + 1) - m))
    p = (n - m - s) / float(max(1, n - m))
    p = float(np.clip(p, 0.51, 0.99))
    z_max = float(st.norm.ppf(p))

    alie_update = {}
    for k in benign_updates[0].keys():
        if "running_" in k or "num_batches" in k:
            alie_update[k] = benign_updates[0][k].clone()
        else:
            stacked = torch.stack([u[k].float() for u in benign_updates], dim=0)
            mean = torch.mean(stacked, dim=0)
            std = torch.std(stacked, dim=0, unbiased=True)
            alie_update[k] = mean - z_max * std
    return alie_update


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
    trust_scorer: Optional[CosineTrustScorer] = None,
    client_indices: Optional[List[int]] = None
) -> Tuple[Dict[str, torch.Tensor], np.ndarray]:
    """
    Norm-Bounded FLTrust-Style Cosine Trust Aggregation (without server data).
    1. Reference r = coordinate-wise median of participating clients' updates (floating-point keys).
    2. Per-round weight w_i = ReLU(cos(Δw_i, r)). Persistent trust T_i <- 0.5*T_i + 0.5*w_i used as weight.
    3. Norm-bound every update: Δw_i <- Δw_i * (||r|| / ||Δw_i||). Neutralises malicious update amplification.
    4. Aggregate sum(w_i * Δw_i) / sum(w_i); if sum(w_i) == 0, fall back to coordinate median r.
    5. Leaves non-floating-point keys untouched.
    """
    num_clients = len(client_updates)
    if num_clients == 0:
        return {}, np.array([])

    float_keys = [k for k in client_updates[0].keys() if client_updates[0][k].is_floating_point()]
    indices = client_indices if client_indices is not None else list(range(num_clients))

    # Flatten each client's floating-point updates into a 1D vector
    flat_updates = []
    for u in client_updates:
        flat = torch.cat([u[k].flatten().float() for k in float_keys])
        flat_updates.append(flat)

    stacked = torch.stack(flat_updates)  # [num_clients, total_dim]

    # 1. Coordinate-wise median reference vector r
    r = torch.median(stacked, dim=0).values
    norm_r = torch.norm(r)
    eps = 1e-12

    # 2 & 3. Per-round weights w_i and norm-bounding
    weights = []
    norm_bounded_flat = []

    for i in range(num_clients):
        v_i = flat_updates[i]
        norm_v_i = torch.norm(v_i)

        # Cosine similarity with reference r
        denom = (norm_v_i * norm_r).clamp(min=eps)
        cos_sim = float(torch.dot(v_i, r) / denom)
        w_i = max(0.0, cos_sim)  # ReLU

        # Persistent trust score update: T_i <- 0.5*T_i + 0.5*w_i
        if trust_scorer is not None and i < len(indices):
            cid = indices[i]
            trust_scorer.trust_scores[cid] = float(0.5 * trust_scorer.trust_scores[cid] + 0.5 * w_i)
            effective_w = float(trust_scorer.trust_scores[cid])
        else:
            effective_w = w_i

        weights.append(effective_w)

        # Norm-bound: Δw_i <- Δw_i * (||r|| / ||Δw_i||)
        if norm_v_i > eps and norm_r > eps:
            scale = float(norm_r / norm_v_i)
            norm_bounded_flat.append(v_i * scale)
        else:
            norm_bounded_flat.append(v_i)

    # 4. Aggregation: sum(w_i * Δw_i) / sum(w_i); fallback to r if all weights 0
    total_w = sum(weights)
    if total_w > 0:
        norm_stacked = torch.stack(norm_bounded_flat)
        weight_tensor = torch.tensor(weights, dtype=torch.float32).unsqueeze(1)
        agg_flat = (norm_stacked * weight_tensor).sum(dim=0) / total_w
    else:
        agg_flat = r

    # 5. Reconstruct update dict matching client_updates[0]
    aggregated = {}
    offset = 0
    for k in client_updates[0].keys():
        if k in float_keys:
            numel = client_updates[0][k].numel()
            shape = client_updates[0][k].shape
            chunk = agg_flat[offset : offset + numel].reshape(shape)
            aggregated[k] = chunk.to(client_updates[0][k].dtype)
            offset += numel
        else:
            aggregated[k] = client_updates[0][k].clone()

    trust_scores = trust_scorer.trust_scores if trust_scorer is not None else np.array(weights)
    return aggregated, trust_scores


# Backward compatibility and canonical aliases
aggregate_cosine_trust_normbounded = aggregate_cosine_trust
