"""
=============================================================================
UNIT TEST: TRUST SCORE WIRING IN SERVER AGGREGATION
Test: tests/test_trust_wiring.py
-----------------------------------------------------------------------------
Asserts that setting one client's trust score to 0 changes the aggregated model,
proving that trust scores are genuinely wired into model weight updates.
=============================================================================
"""

import copy
import unittest
import torch
from layer2_detection.tcn_attention import LightweightTCNAttention
from layer2_detection.scaffold_fl import SCAFFOLDServer


class TestTrustWiring(unittest.TestCase):

    def setUp(self):
        torch.manual_seed(42)
        self.input_dim = 26
        self.global_model = LightweightTCNAttention(input_dim=self.input_dim)

        # Create two distinct client weight sets
        self.client_weights_0 = copy.deepcopy(self.global_model.state_dict())
        self.client_weights_1 = copy.deepcopy(self.global_model.state_dict())

        # Perturb client 0 and client 1 weights in opposite directions for floating point tensors
        for k in self.client_weights_0.keys():
            if self.client_weights_0[k].is_floating_point():
                self.client_weights_0[k] = self.client_weights_0[k] + 0.5 * torch.ones_like(self.client_weights_0[k])
                self.client_weights_1[k] = self.client_weights_1[k] - 0.5 * torch.ones_like(self.client_weights_1[k])

        self.delta_c = [{k: torch.zeros_like(v) for k, v in self.client_weights_0.items()} for _ in range(2)]
        self.sample_counts = [100, 100]

    def test_trust_zero_changes_aggregation(self):
        # 1. Aggregate with full trust for both clients [1.0, 1.0]
        server_balanced = SCAFFOLDServer(self.global_model)
        w_balanced = server_balanced.aggregate(
            client_weights=[self.client_weights_0, self.client_weights_1],
            client_delta_c=self.delta_c,
            sample_counts=self.sample_counts,
            trust_weights=[1.0, 1.0]
        )

        # 2. Aggregate with client 1 untrusted [1.0, 0.0]
        server_filtered = SCAFFOLDServer(self.global_model)
        w_filtered = server_filtered.aggregate(
            client_weights=[self.client_weights_0, self.client_weights_1],
            client_delta_c=self.delta_c,
            sample_counts=self.sample_counts,
            trust_weights=[1.0, 0.0]
        )

        # Assert models are different
        diff_norm = 0.0
        for k in w_balanced.keys():
            diff_norm += torch.norm(w_balanced[k].float() - w_filtered[k].float()).item()

        self.assertGreater(
            diff_norm,
            1e-3,
            f"Trust weights are NOT wired into aggregation! Difference norm = {diff_norm}"
        )
        print(f"\n[TestTrustWiring] Weight difference norm when client trust is zeroed: {diff_norm:.4f}")

        # Assert filtered model matches client 0 exclusively (since client 1 has 0 trust)
        client_0_diff = 0.0
        for k in w_filtered.keys():
            client_0_diff += torch.norm(w_filtered[k].float() - self.client_weights_0[k].float()).item()
        self.assertAlmostEqual(client_0_diff, 0.0, places=4, msg="Untrusted client weights were not completely zeroed out!")


if __name__ == "__main__":
    unittest.main()
