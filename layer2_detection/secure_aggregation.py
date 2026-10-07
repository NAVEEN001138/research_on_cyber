"""
=============================================================================
PARAMETER PERTURBATION, TOP-K SPARSIFICATION, ERROR FEEDBACK & TRUST SCORING
Module: layer2_detection/secure_aggregation.py
-----------------------------------------------------------------------------
Implements:
1. Honest Top-k Sparsification on client parameter updates (Δw = w_local - w_global)
   with client-side error feedback (residual accumulation).
2. Honest byte measurement via PyTorch serialization of sparse values & int32 indices.
3. Gaussian parameter perturbation (no formal differential privacy guarantee).
4. Cosine-similarity adaptive client trust scoring (no reinforcement learning).
=============================================================================
"""

import io
import copy
from typing import Dict, List, Tuple, Optional
import torch
import numpy as np


def compute_dense_update(
    w_local: Dict[str, torch.Tensor],
    w_global: Dict[str, torch.Tensor]
) -> Dict[str, torch.Tensor]:
    """Computes dense update Δw = w_local - w_global."""
    delta_w = {}
    for k in w_local.keys():
        delta_w[k] = (w_local[k].float() - w_global[k].float())
    return delta_w


def serialize_payload_bytes(payload: dict) -> int:
    """Returns exact serialized byte length via torch.save."""
    buf = io.BytesIO()
    torch.save(payload, buf)
    return len(buf.getvalue())


def apply_topk_sparsification(
    delta_w: Dict[str, torch.Tensor],
    residual: Optional[Dict[str, torch.Tensor]] = None,
    top_k_ratio: float = 0.3
) -> Tuple[Dict[str, torch.Tensor], Dict[str, dict], Dict[str, torch.Tensor], int, int]:
    """
    Applies Top-k sparsification to parameter update Δw with error feedback.
    
    Args:
        delta_w: Parameter update dict (w_local - w_global)
        residual: Client-side accumulated residual buffer from previous round (or None)
        top_k_ratio: Fraction of top absolute gradient/update elements to retain (e.g. 0.3)
        
    Returns:
        decompressed_delta: Dense tensor reconstructed from sparse update for aggregation
        sparse_payload: Transmitted dictionary with values, int32 indices, and shapes
        new_residual: Updated error feedback buffer for next round
        sparse_bytes: Exact measured serialized size of sparse payload in bytes
        dense_bytes: Exact measured serialized size of dense update in bytes
    """
    new_residual = {}
    decompressed_delta = {}
    sparse_payload = {}

    for k, v in delta_w.items():
        # Non-trainable BatchNorm buffers should NOT be sparsified with Top-k
        if "running_" in k or "num_batches" in k:
            decompressed_delta[k] = v.clone()
            sparse_payload[k] = {"dense": v.clone()}
            continue

        # Incorporate previous residual (error feedback)
        if residual is not None and k in residual:
            v_acc = v + residual[k]
        else:
            v_acc = v.clone()

        shape = list(v.shape)
        flat = v_acc.flatten()
        numel = flat.numel()

        if numel > 16 and top_k_ratio < 1.0:
            k_val = max(1, int(numel * top_k_ratio))
            topk_vals, topk_indices = torch.topk(torch.abs(flat), k_val)
            selected_vals = flat[topk_indices]
            
            # Error feedback: calculate uncommunicated residual
            reconstructed_flat = torch.zeros_like(flat)
            reconstructed_flat[topk_indices] = selected_vals
            new_residual[k] = (flat - reconstructed_flat).reshape(shape)

            sparse_payload[k] = {
                "values": selected_vals.to(torch.float32),
                "indices": topk_indices.to(torch.int32),
                "shape": shape
            }
            decompressed_delta[k] = reconstructed_flat.reshape(shape)
        else:
            new_residual[k] = torch.zeros_like(v_acc)
            sparse_payload[k] = {
                "values": flat.to(torch.float32),
                "indices": None,
                "shape": shape
            }
            decompressed_delta[k] = v_acc.clone()

    sparse_bytes = serialize_payload_bytes(sparse_payload)
    dense_bytes = serialize_payload_bytes(delta_w)

    return decompressed_delta, sparse_payload, new_residual, sparse_bytes, dense_bytes


def apply_perturbation_and_topk(
    delta_w: Dict[str, torch.Tensor],
    residual: Optional[Dict[str, torch.Tensor]] = None,
    clip_norm: float = 5.0,
    noise_multiplier: float = 0.001,
    top_k_ratio: float = 0.3
) -> Tuple[Dict[str, torch.Tensor], Dict[str, dict], Dict[str, torch.Tensor], int, int]:
    """
    Applies Gaussian parameter perturbation and Top-k sparsification with error feedback.
    Note: Parameter perturbation is a heuristic noise addition and does not carry a formal DP guarantee.
    """
    perturbed_delta = {}
    for k, v in delta_w.items():
        v_float = v.clone().float()
        if "running_" in k or "num_batches" in k:
            perturbed_delta[k] = v_float
            continue
        norm = torch.norm(v_float)
        if norm > clip_norm and ("weight" in k or "bias" in k):
            v_float = v_float * (clip_norm / (norm + 1e-6))
        
        noise = torch.randn_like(v_float) * (noise_multiplier * float(norm + 1e-4))
        perturbed_delta[k] = v_float + noise

    return apply_topk_sparsification(perturbed_delta, residual=residual, top_k_ratio=top_k_ratio)


class CosineTrustScorer:
    """
    Cosine-Similarity Adaptive Client Trust Scorer.
    Dynamically weights client updates based on cosine similarity
    against a robust reference update vector (trust-weighted median).
    Terminology note: This is a geometric heuristic, not reinforcement learning.
    """
    def __init__(self, num_clients: int, lr_trust: float = 0.1):
        self.num_clients = num_clients
        self.lr_trust = lr_trust
        self.trust_scores = np.ones(num_clients, dtype=np.float32)

    def update_trust(
        self,
        client_updates: List[Dict[str, torch.Tensor]],
        participating_indices: Optional[List[int]] = None
    ) -> np.ndarray:
        """
        Calculates cosine similarity of each client's update Δw against a robust reference
        vector and updates trust scores.
        """
        if not client_updates:
            return self.trust_scores

        indices = participating_indices if participating_indices is not None else list(range(len(client_updates)))

        # Flatten updates into single 1D vectors
        flat_vectors = []
        for update in client_updates:
            vec = torch.cat([v.flatten().float() for v in update.values()])
            flat_vectors.append(vec)

        stacked = torch.stack(flat_vectors)  # [num_part, param_dim]

        # Compute robust reference vector: coordinate-wise median
        reference_vec = torch.median(stacked, dim=0).values
        ref_norm = torch.norm(reference_vec) + 1e-8

        for local_idx, client_id in enumerate(indices):
            c_vec = flat_vectors[local_idx]
            c_norm = torch.norm(c_vec) + 1e-8
            cos_sim = float(torch.dot(c_vec, reference_vec) / (c_norm * ref_norm))

            # Reward alignment (cos_sim > 0.3), penalize divergence (cos_sim < 0)
            reward = cos_sim
            self.trust_scores[client_id] = float(np.clip(
                self.trust_scores[client_id] + self.lr_trust * reward,
                0.0,
                1.0
            ))

        return self.trust_scores
