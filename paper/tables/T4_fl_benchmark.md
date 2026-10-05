**Table 4.** Federated detection performance on Edge-IIoTset — *provenance: measured; K = 20 clients, C = 0.5, Dirichlet α = 0.5, 2 rounds, 2 local epochs, batch 64, lr 0.003, 2,000 samples, 19 features, 5 seeds*

| Split | Algorithm | Accuracy | Macro-F1 | ROC-AUC | ROC-AUC 95% CI | Payload / client / round (KB) | Median round time (s) |
|---|---|---:|---:|---:|---:|---:|---:|
| random | FedAvg | 0.8350 ± 0.0000 | 0.4550 ± 0.0000 | 0.5330 ± 0.0730 | [0.4424, 0.6236] | 117.66 | 1.67 |
| random | FedProx | 0.8350 ± 0.0000 | 0.4550 ± 0.0000 | 0.5182 ± 0.0932 | [0.4025, 0.6339] | 117.66 | 2.00 |
| random | SCAFFOLD | 0.8350 ± 0.0000 | 0.4550 ± 0.0000 | 0.5693 ± 0.0890 | [0.4588, 0.6798] | 117.66 | 2.04 |
| random | *Centralized bound (10 epochs)* | 0.8865 ± 0.0070 | 0.7360 ± 0.0431 | 0.8572 ± 0.0098 | [0.8451, 0.8693] | — | — |
| random | SCAFFOLD − FedAvg (accuracy) | mean diff 0.0000 | paired t p = n/a (zero variance) | Wilcoxon p = n/a | | | |
| temporal | FedAvg | 0.8150 ± 0.0000 | 0.4490 ± 0.0000 | 0.5026 ± 0.0406 | [0.4521, 0.5530] | 117.66 | 1.61 |
| temporal | FedProx | 0.8150 ± 0.0000 | 0.4490 ± 0.0000 | 0.5080 ± 0.0504 | [0.4454, 0.5706] | 117.66 | 1.90 |
| temporal | SCAFFOLD | 0.8150 ± 0.0000 | 0.4490 ± 0.0000 | 0.5258 ± 0.0762 | [0.4311, 0.6204] | 117.66 | 1.79 |
| temporal | *Centralized bound (10 epochs)* | 0.8775 ± 0.0068 | 0.7367 ± 0.0286 | 0.8685 ± 0.0069 | [0.8599, 0.8771] | — | — |
| temporal | SCAFFOLD − FedAvg (accuracy) | mean diff 0.0000 | paired t p = n/a (zero variance) | Wilcoxon p = n/a | | | |

Top-k (30 %) update payload including int32 indices and dense BatchNorm buffers = 117.66 KB versus 168.51 KB raw float32 parameters: 30.17 % reduction.
Test-set attack share: random 0.8350, temporal 0.8150. Per-seed values and per-round learning curves are stored under `fl_benchmarks.splits.<split>.algorithms.<algo>.seed_trials` in RESULTS.json.
