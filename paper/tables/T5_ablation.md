**Table 5.** Component ablation — *provenance: measured; 10 clients, 20 rounds, 15,000 samples, 5 seeds; Stage 8 has 20% label-flip + sign-flip clients*

| Stage | Configuration | Parameters | Accuracy | Macro-F1 | ROC-AUC |
|---|---|---:|---:|---:|---:|
| 1 | MLP Baseline | 3,426 | 0.8776 ± 0.0061 | 0.6518 ± 0.0355 | 0.8750 ± 0.0095 |
| 2 | 1-D CNN Baseline | 8,674 | 0.8755 ± 0.0118 | 0.6423 ± 0.0641 | 0.8742 ± 0.0060 |
| 3 | TCN Backbone (No Attn) | 26,498 | 0.8789 ± 0.0068 | 0.6610 ± 0.0411 | 0.8760 ± 0.0084 |
| 4 | + Multi-Head Self-Attention | 43,138 | 0.8760 ± 0.0045 | 0.6443 ± 0.0292 | 0.8760 ± 0.0063 |
| 5 | + Parameter Perturbation (Noise) | 43,138 | 0.8787 ± 0.0065 | 0.6607 ± 0.0407 | 0.8747 ± 0.0027 |
| 6 | + Top-k Update Compression (k=0.3) | 43,138 | 0.8760 ± 0.0045 | 0.6443 ± 0.0292 | 0.8709 ± 0.0097 |
| 7 | + SCAFFOLD Drift Correction | 43,138 | 0.8619 ± 0.0111 | 0.5693 ± 0.0627 | 0.7430 ± 0.0648 |
| 8 | + Cosine Trust Scorer (20% Poisoned) | 43,138 | 0.8363 ± 0.0352 | 0.5374 ± 0.0640 | 0.6511 ± 0.0297 |
