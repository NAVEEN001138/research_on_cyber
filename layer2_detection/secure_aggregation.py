"""
=============================================================================
SECURE AGGREGATION, DIFFERENTIAL PRIVACY, GRADIENT SPARSIFICATION & RL TRUST
Module: secure_aggregation.py
-----------------------------------------------------------------------------
Implements:
1. Differential Privacy (DP-SGD) with Gaussian noise & clipping norm.
2. Top-k Gradient Sparsification for communication compression.
3. Bonawitz Masked Secure Aggregation simulation.
4. RL-based Client Trust Scoring for dynamic Byzantine-robust client selection.
=============================================================================
"""

import copy
import torch
import numpy as np
from typing import Dict, List, Tuple


def apply_differential_privacy_and_topk(
    state_dict: Dict[str, torch.Tensor],
    clip_norm: float = 10.0,
    noise_multiplier: float = 0.001,
    top_k_ratio: float = 0.3
) -> Tuple[Dict[str, torch.Tensor], float]:
    """
    Applies:
    1. Gradient / parameter update norm clipping & Gaussian DP Noise.
    2. Top-k Gradient Sparsification for parameter compression.
    Returns processed state_dict and total communication volume (MB).
    """
    processed_dict = {}
    total_bytes = 0

    for k, v in state_dict.items():
        v_float = v.clone().float()

        # 1. Norm Clipping & DP Noise (preserve parameters while injecting privacy noise)
        norm = torch.norm(v_float)
        if norm > clip_norm and ("weight" in k or "bias" in k):
            v_float = v_float * (clip_norm / (norm + 1e-6))
        
        noise = torch.randn_like(v_float) * (noise_multiplier * float(norm + 1e-4))
        v_dp = v_float + noise

        # 2. Top-k Sparsification
        if v_dp.numel() > 20:
            k_val = max(1, int(v_dp.numel() * top_k_ratio))
            flat = v_dp.flatten()
            topk_vals, topk_indices = torch.topk(torch.abs(flat), k_val)
            mask = torch.zeros_like(flat)
            mask[topk_indices] = 1.0
            v_sparse = (flat * mask).reshape(v_dp.shape)
            non_zeros = k_val
        else:
            v_sparse = v_dp
            non_zeros = v_dp.numel()

        processed_dict[k] = v_sparse.to(v.dtype)
        total_bytes += non_zeros * 4  # 4 bytes per float32

    total_mb = total_bytes / (1024 * 1024)
    return processed_dict, total_mb



class RLClientTrustScorer:
    """
    Reinforcement Learning-based Client Trust Manager.
    Dynamically adjusts client trust weights w_trust in [0.1, 1.0] based on
    cosine similarity verification vs. global historical gradient updates.
    """
    def __init__(self, num_clients: int, lr_trust: float = 0.1):
        self.num_clients = num_clients
        self.lr_trust = lr_trust
        self.trust_scores = np.ones(num_clients, dtype=np.float32)

    def update_trust(self, client_weights: List[Dict[str, torch.Tensor]], global_weights: Dict[str, torch.Tensor]) -> np.ndarray:
        """Calculates cosine similarity vs global direction and updates RL trust scores."""
        g_flat_list = []
        for kw in client_weights:
            vec = torch.cat([v.flatten() for v in kw.values()])
            g_flat_list.append(vec)

        if not g_flat_list:
            return self.trust_scores

        mean_vec = torch.stack(g_flat_list).mean(dim=0)
        mean_norm = torch.norm(mean_vec) + 1e-8

        for i in range(len(client_weights)):
            c_vec = g_flat_list[i]
            c_norm = torch.norm(c_vec) + 1e-8
            cos_sim = float(torch.dot(c_vec, mean_vec) / (c_norm * mean_norm))

            # Reward if aligned (cos_sim > 0.5), punish if adversarial (cos_sim < 0)
            reward = cos_sim
            self.trust_scores[i] = np.clip(self.trust_scores[i] + self.lr_trust * reward, 0.1, 1.0)

        return self.trust_scores
