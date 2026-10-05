**Table 4.** Federated detection performance on Edge-IIoTset — *provenance: measured; K = 20 clients, C = 0.5, Dirichlet α = 0.5, 30 rounds, 1 local epochs, batch 64, lr 0.05, 15,000 samples, 19 features, 5 seeds*

| Split | Algorithm | Accuracy | Macro-F1 | ROC-AUC | ROC-AUC 95% CI | Payload / client / round (KB) | Median round time (s) |
|---|---|---:|---:|---:|---:|---:|---:|
| random | FedAvg | 0.8694 ± 0.0038 | 0.6105 ± 0.0185 | 0.7932 ± 0.0114 | [0.7791, 0.8073] | 117.66 | 5.02 |
| random | FedProx | 0.8693 ± 0.0037 | 0.6104 ± 0.0183 | 0.7931 ± 0.0113 | [0.7791, 0.8071] | 117.66 | 6.64 |
| random | SCAFFOLD | 0.8711 ± 0.0038 | 0.6176 ± 0.0185 | 0.8093 ± 0.0338 | [0.7673, 0.8513] | 117.66 | 5.52 |
| random | *Centralized bound (10 epochs)* | 0.8909 ± 0.0035 | 0.7409 ± 0.0029 | 0.8822 ± 0.0042 | [0.8770, 0.8874] | — | — |
| random | SCAFFOLD − FedAvg (accuracy) | mean diff 0.0017 | paired t p = 0.2588 | Wilcoxon p = 0.0625 | | | |
| temporal | FedAvg | 0.7771 ± 0.1412 | 0.5960 ± 0.0442 | 0.7951 ± 0.0175 | [0.7733, 0.8169] | 117.66 | 5.16 |
| temporal | FedProx | 0.7769 ± 0.1415 | 0.5959 ± 0.0443 | 0.7950 ± 0.0177 | [0.7731, 0.8169] | 117.66 | 6.59 |
| temporal | SCAFFOLD | 0.8808 ± 0.0044 | 0.6288 ± 0.0219 | 0.7552 ± 0.0791 | [0.6571, 0.8534] | 117.66 | 5.22 |
| temporal | *Centralized bound (10 epochs)* | 0.8957 ± 0.0034 | 0.7342 ± 0.0205 | 0.8766 ± 0.0003 | [0.8763, 0.8769] | — | — |
| temporal | SCAFFOLD − FedAvg (accuracy) | mean diff 0.1037 | paired t p = 0.1692 | Wilcoxon p = 0.1875 | | | |

Top-k (30 %) update payload including int32 indices and dense BatchNorm buffers = 117.66 KB versus 168.51 KB raw float32 parameters: 30.17 % reduction.
Test-set attack share: random 0.8427, temporal 0.8523. Per-seed values and per-round learning curves are stored under `fl_benchmarks.splits.<split>.algorithms.<algo>.seed_trials` in RESULTS.json.
