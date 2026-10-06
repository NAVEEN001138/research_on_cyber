**Table 5.** Component ablation — *provenance: measured; 10 clients, 20 rounds, 15,000 samples, 5 seeds; Stage 8 has 20% label-flip + sign-flip clients*

| Stage | Configuration | Parameters | Accuracy | Macro-F1 | ROC-AUC |
|---|---|---:|---:|---:|---:|
| 1 | MLP Baseline | 3,426 | 0.8776 ± 0.0061 | 0.6518 ± 0.0355 | 0.8750 ± 0.0095 |
| 2 | 1-D CNN Baseline | 8,674 | 0.8710 ± 0.0058 | 0.6175 ± 0.0297 | 0.8794 ± 0.0010 |
| 3 | TCN Backbone (No Attn) | 26,498 | 0.8768 ± 0.0063 | 0.6477 ± 0.0366 | 0.8807 ± 0.0031 |
| 4 | + Multi-Head Self-Attention | 43,138 | 0.8768 ± 0.0063 | 0.6477 ± 0.0366 | 0.8837 ± 0.0034 |
| 5 | + Parameter Perturbation (Noise) | 43,138 | 0.8740 ± 0.0000 | 0.6313 ± 0.0000 | 0.8767 ± 0.0056 |
| 6 | + Top-k Update Compression (k=0.3) | 43,138 | 0.8740 ± 0.0000 | 0.6313 ± 0.0000 | 0.8726 ± 0.0219 |
| 6b | FedAvg (SGD, GroupNorm, K=20 steps) | 43,138 | 0.8556 ± 0.0131 | 0.5400 ± 0.0759 | 0.7378 ± 0.0439 |
| 7 | + SCAFFOLD Drift Correction | 43,138 | 0.8619 ± 0.0111 | 0.5693 ± 0.0627 | 0.7430 ± 0.0648 |
| 8 | + Cosine Trust Scorer (20% Poisoned) | 43,138 | 0.8363 ± 0.0352 | 0.5374 ± 0.0640 | 0.6511 ± 0.0297 |
