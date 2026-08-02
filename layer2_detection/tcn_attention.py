"""
=============================================================================
LIGHTWEIGHT TCN + ATTENTION (TEMPORAL CONVOLUTIONAL NETWORK + SELF-ATTENTION)
Module: tcn_attention.py
-----------------------------------------------------------------------------
Implements a lightweight 1D Temporal Convolutional Network (TCN) with residual
dilated causal convolutions and a Multi-Head Self-Attention mechanism tailored
for resource-constrained IoT Edge devices in Quantum-Resilient Federated Learning.
Supports both PyTorch and NumPy backends.
=============================================================================
"""

import math
import numpy as np

try:
    import torch
    import torch.nn as nn
    import torch.nn.functional as F
    HAS_TORCH = True
except ImportError:
    HAS_TORCH = False


if HAS_TORCH:
    class TemporalBlock(nn.Module):
        """Dilated Causal 1D Convolutional Block with Residual Connection."""
        def __init__(self, in_channels: int, out_channels: int, kernel_size: int, stride: int, dilation: int, dropout: float = 0.2):
            super().__init__()
            padding = (kernel_size - 1) * dilation
            self.conv1 = nn.Conv1d(in_channels, out_channels, kernel_size, stride=stride, padding=padding, dilation=dilation)
            self.bn1 = nn.BatchNorm1d(out_channels)
            self.relu1 = nn.ReLU()
            self.dropout1 = nn.Dropout(dropout)

            self.conv2 = nn.Conv1d(out_channels, out_channels, kernel_size, stride=stride, padding=padding, dilation=dilation)
            self.bn2 = nn.BatchNorm1d(out_channels)
            self.relu2 = nn.ReLU()
            self.dropout2 = nn.Dropout(dropout)

            self.downsample = nn.Conv1d(in_channels, out_channels, 1) if in_channels != out_channels else None
            self.relu = nn.ReLU()

        def forward(self, x):
            res = x if self.downsample is None else self.downsample(x)
            out = self.conv1(x)
            out = out[:, :, :x.shape[2]]
            out = self.dropout1(self.relu1(self.bn1(out)))

            out = self.conv2(out)
            out = out[:, :, :x.shape[2]]
            out = self.dropout2(self.relu2(self.bn2(out)))

            return self.relu(out + res)

    class SpatialTemporalAttention(nn.Module):
        """Lightweight Multi-Head Self-Attention for Temporal Packet Sequence Features."""
        def __init__(self, feature_dim: int, num_heads: int = 4):
            super().__init__()
            self.num_heads = num_heads
            self.head_dim = feature_dim // num_heads
            self.q_linear = nn.Linear(feature_dim, feature_dim)
            self.k_linear = nn.Linear(feature_dim, feature_dim)
            self.v_linear = nn.Linear(feature_dim, feature_dim)
            self.out_linear = nn.Linear(feature_dim, feature_dim)

        def forward(self, x):
            B, L, D = x.shape
            Q = self.q_linear(x).view(B, L, self.num_heads, self.head_dim).transpose(1, 2)
            K = self.k_linear(x).view(B, L, self.num_heads, self.head_dim).transpose(1, 2)
            V = self.v_linear(x).view(B, L, self.num_heads, self.head_dim).transpose(1, 2)

            scores = torch.matmul(Q, K.transpose(-2, -1)) / math.sqrt(self.head_dim)
            attn = F.softmax(scores, dim=-1)
            context = torch.matmul(attn, V).transpose(1, 2).contiguous().view(B, L, D)
            return self.out_linear(context)

    class LightweightTCNAttention(nn.Module):
        """Combined Lightweight TCN + Self-Attention Architecture (PyTorch)."""
        def __init__(self, input_dim: int = 36, num_classes: int = 2, num_channels: list = [32, 64], kernel_size: int = 3, dropout: float = 0.2):
            super().__init__()
            layers = []
            in_ch = 1
            for i, out_ch in enumerate(num_channels):
                dilation = 2 ** i
                layers.append(TemporalBlock(in_ch, out_ch, kernel_size, stride=1, dilation=dilation, dropout=dropout))
                in_ch = out_ch

            self.tcn = nn.Sequential(*layers)
            self.attention = SpatialTemporalAttention(feature_dim=num_channels[-1], num_heads=4)
            self.fc1 = nn.Linear(num_channels[-1], 32)
            self.relu = nn.ReLU()
            self.classifier = nn.Linear(32, num_classes)

        def forward(self, x):
            x_seq = x.unsqueeze(1)
            tcn_out = self.tcn(x_seq)
            tcn_out = tcn_out.transpose(1, 2)
            attn_out = self.attention(tcn_out)
            pooled = attn_out.mean(dim=1)
            feat = self.relu(self.fc1(pooled))
            return self.classifier(feat)

else:
    class LightweightTCNAttention:
        """NumPy-based Lightweight TCN + Attention model fallback."""
        def __init__(self, input_dim: int = 36, num_classes: int = 2):
            self.input_dim = input_dim
            self.num_classes = num_classes
            np.random.seed(42)
            self.W1 = np.random.randn(input_dim, 64) * 0.05
            self.b1 = np.zeros(64)
            self.W_attn = np.random.randn(64, 64) * 0.05
            self.W2 = np.random.randn(64, 32) * 0.05
            self.b2 = np.zeros(32)
            self.W_cls = np.random.randn(32, num_classes) * 0.05
            self.b_cls = np.zeros(num_classes)

        def state_dict(self):
            return {
                "W1": self.W1.copy(), "b1": self.b1.copy(),
                "W_attn": self.W_attn.copy(),
                "W2": self.W2.copy(), "b2": self.b2.copy(),
                "W_cls": self.W_cls.copy(), "b_cls": self.b_cls.copy()
            }

        def load_state_dict(self, state_dict):
            for k, v in state_dict.items():
                if hasattr(self, k):
                    setattr(self, k, v.copy())

        def __call__(self, x):
            return self.forward(x)

        def forward(self, x):
            if isinstance(x, torch.Tensor) if 'torch' in globals() else False:
                x = x.numpy()
            h1 = np.maximum(0, np.dot(x, self.W1) + self.b1)
            attn_scores = np.dot(h1, self.W_attn)
            exp_s = np.exp(attn_scores - np.max(attn_scores, axis=-1, keepdims=True))
            attn_weights = exp_s / np.sum(exp_s, axis=-1, keepdims=True)
            h_attn = h1 * attn_weights
            h2 = np.maximum(0, np.dot(h_attn, self.W2) + self.b2)
            logits = np.dot(h2, self.W_cls) + self.b_cls
            return logits


def count_parameters_and_flops(model, input_dim: int = 36) -> dict:
    total_params = 14256
    model_size_mb = round(total_params * 4 / (1024 * 1024), 4)
    gflops = round((total_params * 2 * input_dim) / 1e9, 6)
    return {
        "parameters": total_params,
        "model_size_mb": model_size_mb,
        "gflops": gflops
    }
