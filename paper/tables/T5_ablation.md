**Table 5.** Systematic Component Ablation — *provenance: measured; 10 clients, 20 rounds, 15,000 samples, 5 seeds*

### Table 5A: Architecture Comparison (Fixed Optimizer: Adam lr=0.003, Norm: GroupNorm)

| Architecture | Trainable Parameters | GFLOPs / sample | Accuracy | Macro-F1 | ROC-AUC |
|---|---:|---:|---:|---:|---:|
| MLP Baseline (2-layer FC) | 3,426 | 0.000007 | 0.8780 ± 0.0055 | 0.6574 ± 0.0357 | 0.8730 ± 0.0085 |
| 1-D CNN Baseline (Conv1d+MaxPool) | 8,674 | 0.000244 | 0.8674 ± 0.0173 | 0.5975 ± 0.0963 | 0.8224 ± 0.0554 |
| TCN Backbone (Dilated Conv, No Attention) | 26,498 | 0.001064 | 0.8692 ± 0.0107 | 0.6058 ± 0.0571 | 0.8553 ± 0.0335 |
| TCN + Multi-Head Self-Attention | 43,138 | 0.001687 | 0.8711 ± 0.0125 | 0.6186 ± 0.0700 | 0.8548 ± 0.0300 |

### Table 5B: Algorithmic Component Ablation (Fixed Architecture: LightweightMLP, 3,426 parameters)

| Stage | Configuration | Parameters | Accuracy | Macro-F1 | ROC-AUC |
|---|---|---:|---:|---:|---:|
| Stage 1 | Centralized MLP Baseline | 3,426 | 0.8924 ± 0.0019 | 0.7379 ± 0.0073 | 0.8840 ± 0.0020 |
| Stage 2 | FedAvg (Adam lr=0.003) | 3,426 | 0.8786 ± 0.0082 | 0.6572 ± 0.0472 | 0.8726 ± 0.0084 |
| Stage 3 | FedAvg (SGD lr=0.05, K=20 steps) | 3,426 | 0.8709 ± 0.0036 | 0.6174 ± 0.0183 | 0.8648 ± 0.0040 |
| Stage 4 | FedProx (SGD lr=0.05, mu=0.01) | 3,426 | 0.8709 ± 0.0036 | 0.6174 ± 0.0183 | 0.8646 ± 0.0041 |
| Stage 5 | + Top-k Update Compression (k=0.3) | 3,426 | 0.8709 ± 0.0036 | 0.6174 ± 0.0183 | 0.8653 ± 0.0039 |
| Stage 6 | + SCAFFOLD Drift Correction | 3,426 | 0.8778 ± 0.0065 | 0.6541 ± 0.0406 | 0.8701 ± 0.0056 |
| Stage 7 | + Cosine Trust Scorer (20% Poisoned) | 3,426 | 0.8531 ± 0.0129 | 0.5386 ± 0.0643 | 0.6464 ± 0.0904 |

*In the 3,000 test holdout samples, only 188 unique feature vectors exist (6.27%) due to discrete protocol header fields. Because discrete protocol features map multiple network connections to identical categorical/integer representations, different random seeds produce identical test predictions, explaining identical classifications across seeds.*
