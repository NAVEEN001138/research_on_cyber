**Table 4.** Federated detection performance on Edge-IIoTset — *provenance: measured; K = 20 clients, C = 0.5, Dirichlet α = 0.5, 30 rounds, 1 local epochs, batch 64, lr 0.05, 15,000 samples, 19 features, 5 seeds*

| Split | Algorithm | Accuracy | Macro-F1 | ROC-AUC | ROC-AUC 95% CI | Payload / client / round (KB) | Median round time (s) |
|---|---|---:|---:|---:|---:|---:|---:|
| random | FedAvg (Adam) | 0.8788 ± 0.0067 | 0.6607 ± 0.0407 | 0.8743 ± 0.0128 | [0.8584, 0.8901] | 122.63 | 6.24 |
| random | FedAvg (SGD) | 0.8709 ± 0.0039 | 0.6174 ± 0.0186 | 0.7928 ± 0.0169 | [0.7718, 0.8138] | 117.66 | 5.67 |
| random | FedProx (SGD) | 0.8709 ± 0.0039 | 0.6174 ± 0.0186 | 0.7927 ± 0.0168 | [0.7718, 0.8136] | 117.66 | 5.98 |
| random | SCAFFOLD (SGD) | 0.8619 ± 0.0113 | 0.5693 ± 0.0628 | 0.7542 ± 0.0682 | [0.6695, 0.8388] | 295.23 | 6.05 |
| random | FedAvg (Class-Weighted) | 0.7457 ± 0.0975 | 0.6427 ± 0.0490 | 0.8636 ± 0.0218 | [0.8366, 0.8907] | 122.63 | 6.18 |
| random | *Centralized bound (10 epochs)* | 0.8929 ± 0.0001 | 0.7407 ± 0.0002 | 0.8806 ± 0.0034 | [0.8763, 0.8848] | — | — |
| random | SCAFFOLD (SGD) − FedAvg (SGD) (accuracy) | mean diff -0.0090 | paired t p = 0.2062 | Wilcoxon p = 0.2500 | | | |
| random | SCAFFOLD (SGD) − FedAvg (SGD) (ROC-AUC) | mean diff -0.0387 | paired t p = 0.2404 | Wilcoxon p = 0.3125 | | | |
| random | SCAFFOLD (SGD) − FedAvg (Adam) (accuracy) | mean diff -0.0169 | paired t p = 0.0238 | Wilcoxon p = 0.0625 | | | |
| random | SCAFFOLD (SGD) − FedAvg (Adam) (ROC-AUC) | mean diff -0.1201 | paired t p = 0.0171 | Wilcoxon p = 0.0625 | | | |
| session-disjoint | FedAvg (Adam) | 0.8764 ± 0.0403 | 0.6543 ± 0.0489 | 0.8559 ± 0.0570 | [0.8323, 0.8794] | 122.63 | 6.74 |
| session-disjoint | FedAvg (SGD) | 0.8590 ± 0.0550 | 0.6180 ± 0.0438 | 0.7931 ± 0.0264 | [0.7822, 0.8040] | 117.66 | 5.59 |
| session-disjoint | FedProx (SGD) | 0.8590 ± 0.0550 | 0.6180 ± 0.0438 | 0.7928 ± 0.0264 | [0.7819, 0.8037] | 117.66 | 6.13 |
| session-disjoint | SCAFFOLD (SGD) | 0.8658 ± 0.0392 | 0.6013 ± 0.0645 | 0.7712 ± 0.0739 | [0.7408, 0.8018] | 295.23 | 6.38 |
| session-disjoint | FedAvg (Class-Weighted) | 0.7273 ± 0.0708 | 0.6483 ± 0.0521 | 0.8437 ± 0.0532 | [0.8217, 0.8656] | 122.63 | 7.36 |
| session-disjoint | *Centralized bound (10 epochs)* | 0.8803 ± 0.0374 | 0.7029 ± 0.0461 | 0.8564 ± 0.0617 | [0.8309, 0.8818] | — | — |
| session-disjoint | SCAFFOLD (SGD) − FedAvg (SGD) (accuracy) | mean diff 0.0068 | paired t p = 0.4754 | Wilcoxon p = 0.9679 | | | |
| session-disjoint | SCAFFOLD (SGD) − FedAvg (SGD) (ROC-AUC) | mean diff -0.0218 | paired t p = 0.1012 | Wilcoxon p = 0.2411 | | | |
| session-disjoint | SCAFFOLD (SGD) − FedAvg (Adam) (accuracy) | mean diff -0.0106 | paired t p = 0.0001 | Wilcoxon p = 0.0001 | | | |
| session-disjoint | SCAFFOLD (SGD) − FedAvg (Adam) (ROC-AUC) | mean diff -0.0846 | paired t p = 0.0001 | Wilcoxon p = 0.0001 | | | |

*Session-disjoint robustness across 5 group splits × 5 training seeds (25 runs total):*

| Split Index | Train Samples | Test Samples | Train Attack Rate (%) | Test Attack Rate (%) |
|---:|---:|---:|---:|---:|
| 0 | 11,863 | 3,137 | 83.36 | 87.73 |
| 1 | 12,317 | 2,683 | 84.14 | 84.87 |
| 2 | 12,132 | 2,868 | 83.75 | 86.47 |
| 3 | 12,162 | 2,838 | 83.85 | 86.08 |
| 4 | 12,198 | 2,802 | 86.14 | 76.16 |

Top-k (30 %) update payload: FedAvg / FedProx = 117.66 KB (30.17 % reduction vs 168.51 KB raw float32 parameters). SCAFFOLD transmits sparse Δw + dense control variates Δc = 295.23 KB total uplink per round.
