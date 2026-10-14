**Table 4.** Federated detection performance on Edge-IIoTset — *provenance: measured; K = 20 clients, C = 0.5, Dirichlet α = 0.5, 30 rounds, 1 local epochs, batch 64, lr 0.05, 15,000 samples, 19 features, 5 seeds*

| Split | Algorithm | Accuracy | Macro-F1 | ROC-AUC | ROC-AUC 95% CI | Payload / client / round (KB) | Median round time (s) |
|---|---|---:|---:|---:|---:|---:|---:|
| random | FedAvg (Adam) | 0.8807 ± 0.0093 | 0.6697 ± 0.0535 | 0.8738 ± 0.0145 | [0.8558, 0.8918] | 122.63 | 7.24 |
| random | FedAvg (SGD) | 0.8694 ± 0.0038 | 0.6105 ± 0.0185 | 0.7932 ± 0.0114 | [0.7791, 0.8073] | 117.66 | 4.92 |
| random | FedProx (SGD) | 0.8693 ± 0.0037 | 0.6104 ± 0.0183 | 0.7931 ± 0.0113 | [0.7791, 0.8071] | 117.66 | 6.30 |
| random | SCAFFOLD (SGD) | 0.8711 ± 0.0038 | 0.6176 ± 0.0185 | 0.8093 ± 0.0338 | [0.7673, 0.8513] | 295.23 | 3.84 |
| random | *Centralized bound (10 epochs)* | 0.8909 ± 0.0035 | 0.7409 ± 0.0029 | 0.8822 ± 0.0042 | [0.8770, 0.8874] | — | — |
| random | SCAFFOLD (SGD) − FedAvg (SGD) (accuracy) | mean diff 0.0017 | paired t p = 0.2588 | Wilcoxon p = 0.0625 | | | |
| random | SCAFFOLD (SGD) − FedAvg (SGD) (ROC-AUC) | mean diff 0.0161 | paired t p = 0.2784 | Wilcoxon p = 0.8125 | | | |
| random | SCAFFOLD (SGD) − FedAvg (Adam) (accuracy) | mean diff -0.0095 | paired t p = 0.0433 | Wilcoxon p = 0.0625 | | | |
| random | SCAFFOLD (SGD) − FedAvg (Adam) (ROC-AUC) | mean diff -0.0644 | paired t p = 0.0155 | Wilcoxon p = 0.0625 | | | |
| session-disjoint | FedAvg (Adam) | 0.8861 ± 0.0009 | 0.6611 ± 0.0188 | 0.8718 ± 0.0041 | [0.8667, 0.8770] | 122.63 | 4.14 |
| session-disjoint | FedAvg (SGD) | 0.7771 ± 0.1412 | 0.5960 ± 0.0442 | 0.7951 ± 0.0175 | [0.7733, 0.8169] | 117.66 | 3.82 |
| session-disjoint | FedProx (SGD) | 0.7769 ± 0.1415 | 0.5959 ± 0.0443 | 0.7950 ± 0.0177 | [0.7731, 0.8169] | 117.66 | 7.12 |
| session-disjoint | SCAFFOLD (SGD) | 0.8808 ± 0.0044 | 0.6288 ± 0.0219 | 0.7552 ± 0.0791 | [0.6571, 0.8534] | 295.23 | 5.63 |
| session-disjoint | *Centralized bound (10 epochs)* | 0.8957 ± 0.0034 | 0.7342 ± 0.0205 | 0.8766 ± 0.0003 | [0.8763, 0.8769] | — | — |
| session-disjoint | SCAFFOLD (SGD) − FedAvg (SGD) (accuracy) | mean diff 0.1037 | paired t p = 0.1692 | Wilcoxon p = 0.1875 | | | |
| session-disjoint | SCAFFOLD (SGD) − FedAvg (SGD) (ROC-AUC) | mean diff -0.0399 | paired t p = 0.2688 | Wilcoxon p = 0.3125 | | | |
| session-disjoint | SCAFFOLD (SGD) − FedAvg (Adam) (accuracy) | mean diff -0.0053 | paired t p = 0.0728 | Wilcoxon p = 0.2500 | | | |
| session-disjoint | SCAFFOLD (SGD) − FedAvg (Adam) (ROC-AUC) | mean diff -0.1166 | paired t p = 0.0296 | Wilcoxon p = 0.0625 | | | |

Top-k (30 %) update payload: FedAvg / FedProx = 117.66 KB (30.17 % reduction vs 168.51 KB raw float32 parameters). SCAFFOLD transmits sparse Δw + dense control variates Δc = 295.23 KB total uplink per round.
