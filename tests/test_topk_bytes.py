"""
=============================================================================
UNIT TEST: TOP-K SERIALIZED PAYLOAD BYTES HONESTY
Test: tests/test_topk_bytes.py
-----------------------------------------------------------------------------
Asserts that reported payload bytes equal len(torch.save(...)) of the actual
sparse payload including indices and metadata, with no synthetic estimation.
=============================================================================
"""

import io
import unittest
import torch
from layer2_detection.secure_aggregation import (
    apply_topk_sparsification,
    serialize_payload_bytes
)


class TestTopKSparsificationBytes(unittest.TestCase):

    def setUp(self):
        torch.manual_seed(42)
        # Create representative parameter update dictionary
        self.delta_w = {
            "conv1.weight": torch.randn(32, 1, 3),
            "conv1.bias": torch.randn(32),
            "conv2.weight": torch.randn(64, 32, 3),
            "conv2.bias": torch.randn(64),
            "linear1.weight": torch.randn(32, 64),
            "linear1.bias": torch.randn(32),
            "classifier.weight": torch.randn(2, 32),
            "classifier.bias": torch.randn(2),
        }

    def test_payload_bytes_equal_exact_torch_save(self):
        decompressed, sparse_payload, residual, sparse_bytes, dense_bytes = apply_topk_sparsification(
            self.delta_w,
            top_k_ratio=0.3
        )

        # Directly serialize sparse_payload with torch.save to BytesIO
        buf = io.BytesIO()
        torch.save(sparse_payload, buf)
        actual_bytes = len(buf.getvalue())

        # Assert reported bytes exactly equals actual serialized bytes
        self.assertEqual(
            sparse_bytes,
            actual_bytes,
            f"Reported bytes {sparse_bytes} != actual torch.save bytes {actual_bytes}"
        )

        # Dense serialization check
        dense_buf = io.BytesIO()
        torch.save(self.delta_w, dense_buf)
        actual_dense = len(dense_buf.getvalue())
        self.assertEqual(
            dense_bytes,
            actual_dense,
            f"Reported dense bytes {dense_bytes} != actual torch.save dense {actual_dense}"
        )

        # Assert compression savings is honest (< 60% savings for 30% keep due to indices)
        savings = (1.0 - sparse_bytes / dense_bytes) * 100.0
        print(f"\n[TestTopK] Dense bytes: {dense_bytes} B | Sparse bytes: {sparse_bytes} B | Savings: {savings:.2f}%")
        self.assertTrue(0.0 < savings < 65.0, f"Unrealistic compression savings reported: {savings}%")

    def test_indices_are_int32(self):
        _, sparse_payload, _, _, _ = apply_topk_sparsification(self.delta_w, top_k_ratio=0.3)
        for layer_name, tensor_data in sparse_payload.items():
            if tensor_data["indices"] is not None:
                self.assertEqual(
                    tensor_data["indices"].dtype,
                    torch.int32,
                    f"Indices in {layer_name} are not int32!"
                )

    def test_error_feedback_accumulation(self):
        # Round 1
        _, _, res1, _, _ = apply_topk_sparsification(self.delta_w, residual=None, top_k_ratio=0.3)
        self.assertIsNotNone(res1)
        res_norm = sum(torch.norm(r).item() for r in res1.values())
        self.assertGreater(res_norm, 0.0, "Residual should be non-zero after sparsification")

        # Round 2 with accumulated residual
        _, _, res2, _, _ = apply_topk_sparsification(self.delta_w, residual=res1, top_k_ratio=0.3)
        self.assertIsNotNone(res2)

    def test_batchnorm_buffers_included_dense_in_payload(self):
        delta_with_bn = dict(self.delta_w)
        delta_with_bn["bn1.running_mean"] = torch.zeros(32)
        delta_with_bn["bn1.running_var"] = torch.ones(32)
        delta_with_bn["bn1.num_batches_tracked"] = torch.tensor(10, dtype=torch.long)

        decomp, sparse_payload, _, sparse_bytes, dense_bytes = apply_topk_sparsification(
            delta_with_bn, top_k_ratio=0.3
        )
        self.assertIn("bn1.running_mean", sparse_payload)
        self.assertIn("dense", sparse_payload["bn1.running_mean"])
        self.assertIn("bn1.num_batches_tracked", sparse_payload)
        self.assertIn("dense", sparse_payload["bn1.num_batches_tracked"])


if __name__ == "__main__":
    unittest.main()
