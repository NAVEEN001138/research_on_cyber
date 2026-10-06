"""
Tests for Norm-Bounded FLTrust-Style Cosine Trust Aggregation
Validates that with 10 honest updates ~ N(mu, sigma) and 2 updates = -5*mu,
the aggregate's cosine similarity with mu is > 0.9.
"""

import torch
import numpy as np
import pytest
from attacks.poisoning import aggregate_cosine_trust
from layer2_detection.secure_aggregation import CosineTrustScorer


def test_cosine_trust_norm_bounded_robustness():
    torch.manual_seed(42)
    np.random.seed(42)

    dim = 200
    mu = torch.randn(dim)
    mu = mu / torch.norm(mu)  # unit vector mu
    sigma = 0.05

    # 10 honest updates ~ N(mu, sigma)
    honest_updates = []
    for _ in range(10):
        noise = torch.randn(dim) * sigma
        h = mu + noise
        honest_updates.append({"layer1.weight": h.reshape(20, 10)})

    # 2 malicious updates = -5 * mu
    malicious_updates = []
    for _ in range(2):
        m = -5.0 * mu
        malicious_updates.append({"layer1.weight": m.reshape(20, 10)})

    all_updates = honest_updates + malicious_updates  # 12 clients

    trust_scorer = CosineTrustScorer(num_clients=12, lr_trust=0.5)
    aggregated, trust_scores = aggregate_cosine_trust(
        all_updates, trust_scorer=trust_scorer, client_indices=list(range(12))
    )

    agg_vec = aggregated["layer1.weight"].flatten().float()
    cos_sim = float(torch.dot(agg_vec, mu) / (torch.norm(agg_vec) * torch.norm(mu)))

    print(f"Cosine similarity with mu: {cos_sim:.4f}")
    assert cos_sim > 0.9, f"Expected cosine similarity > 0.9, got {cos_sim:.4f}"
