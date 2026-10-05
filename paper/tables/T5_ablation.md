**Table 5.** Component ablation — *provenance: measured; 10 clients, 20 rounds, 15,000 samples, 5 seeds; Stage 8 has 20% label-flip + sign-flip clients*

| Stage | Configuration | Parameters | Accuracy | Macro-F1 | ROC-AUC |
|---|---|---:|---:|---:|---:|
| 1 | MLP Baseline | 3,426 | 0.8776 ± 0.0061 | 0.6518 ± 0.0355 | 0.8750 ± 0.0095 |
| 2 | 1-D CNN Baseline | 8,674 | 0.8710 ± 0.0058 | 0.6175 ± 0.0297 | 0.8794 ± 0.0010 |
| 3 | TCN Backbone (No Attn) | 26,498 | 0.8768 ± 0.0063 | 0.6477 ± 0.0366 | 0.8807 ± 0.0031 |
| 4 | + Multi-Head Self-Attention | 43,138 | 0.8768 ± 0.0063 | 0.6477 ± 0.0366 | 0.8837 ± 0.0034 |
| 5 | + Parameter Perturbation (Noise) | 43,138 | 0.8740 ± 0.0000 | 0.6313 ± 0.0000 | 0.8767 ± 0.0056 |
| 6 | + Top-k Update Compression (k=0.3) | 43,138 | 0.8740 ± 0.0000 | 0.6313 ± 0.0000 | 0.8726 ± 0.0219 |
| 7 | + SCAFFOLD Drift Correction | 43,138 | 0.6864 ± 0.3166 | 0.5561 ± 0.2432 | 0.8485 ± 0.0415 |
| 8 | + Cosine Trust Scorer (20% Poisoned) | 43,138 | 0.2990 ± 0.3168 | 0.2331 ± 0.2173 | 0.5338 ± 0.1998 |
