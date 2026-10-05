**Table 1.** Edge-IIoTset (ML-EdgeIIoT-dataset.csv) class distribution — *provenance: measured (full file)*

| Attack type | Rows | Share of file (%) |
|---|---:|---:|
| Normal | 24,301 | 15.40 |
| DDoS_UDP | 14,498 | 9.19 |
| DDoS_ICMP | 14,090 | 8.93 |
| Ransomware | 10,925 | 6.92 |
| DDoS_HTTP | 10,561 | 6.69 |
| SQL_injection | 10,311 | 6.53 |
| Uploading | 10,269 | 6.51 |
| DDoS_TCP | 10,247 | 6.49 |
| Backdoor | 10,195 | 6.46 |
| Vulnerability_scanner | 10,076 | 6.39 |
| Port_Scanning | 10,071 | 6.38 |
| XSS | 10,052 | 6.37 |
| Password | 9,989 | 6.33 |
| MITM | 1,214 | 0.77 |
| Fingerprinting | 1,001 | 0.63 |
| **Total** | **157,800** | 100.00 |
| Normal / Attack | 24,301 / 133,499 | 15.40 / 84.60 |

**Table 2.** Model complexity (input dim = 19) — *provenance: measured (parameter count and FLOPs profiled in code)*

| Model | Trainable parameters | Size (KB, float32) | GFLOPs / sample |
|---|---:|---:|---:|
| MLP | 3,426 | 13.38 | 0.000007 |
| CNN 1D | 8,674 | 33.88 | 0.000244 |
| TCN NoAttention | 26,498 | 103.51 | 0.001064 |
| TCN Attention | 43,138 | 168.51 | 0.001687 |

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

**Table 6.** Robustness to Byzantine clients — *provenance: measured; K = 20, 15 rounds, 10,000 samples, 5 seeds; attack = label flip + scaled sign flip (λ = 5)*

| Malicious clients | Defense | Accuracy | Macro-F1 | ROC-AUC |
|---|---|---:|---:|---:|
| 0% | FedAvg Undefended | 0.8665 ± 0.0093 | 0.6199 ± 0.0440 | 0.8497 ± 0.0134 |
| 0% | Coordinate Median | 0.8668 ± 0.0086 | 0.6363 ± 0.0428 | 0.8504 ± 0.0063 |
| 0% | Trimmed Mean | 0.8637 ± 0.0069 | 0.6094 ± 0.0377 | 0.8447 ± 0.0150 |
| 0% | Multi Krum | 0.8330 ± 0.0497 | 0.5658 ± 0.1055 | 0.7639 ± 0.0707 |
| 0% | Cosine Trust | 0.8665 ± 0.0093 | 0.6199 ± 0.0440 | 0.8497 ± 0.0134 |
| 10% | FedAvg Undefended | 0.8493 ± 0.0120 | 0.5074 ± 0.0694 | 0.6657 ± 0.1739 |
| 10% | Coordinate Median | 0.8621 ± 0.0138 | 0.6227 ± 0.0401 | 0.8278 ± 0.0150 |
| 10% | Trimmed Mean | 0.8661 ± 0.0055 | 0.6054 ± 0.0359 | 0.8264 ± 0.0221 |
| 10% | Multi Krum | 0.8474 ± 0.0486 | 0.6511 ± 0.0575 | 0.8267 ± 0.0118 |
| 10% | Cosine Trust | 0.8493 ± 0.0120 | 0.5074 ± 0.0694 | 0.6657 ± 0.1739 |
| 20% | FedAvg Undefended | 0.8405 ± 0.0000 | 0.4567 ± 0.0000 | 0.5324 ± 0.0724 |
| 20% | Coordinate Median | 0.8463 ± 0.0477 | 0.6008 ± 0.0211 | 0.8160 ± 0.0575 |
| 20% | Trimmed Mean | 0.8525 ± 0.0298 | 0.6021 ± 0.0361 | 0.8126 ± 0.0466 |
| 20% | Multi Krum | 0.8411 ± 0.0479 | 0.5761 ± 0.0163 | 0.7757 ± 0.0449 |
| 20% | Cosine Trust | 0.8405 ± 0.0000 | 0.4567 ± 0.0000 | 0.5324 ± 0.0724 |
| 30% | FedAvg Undefended | 0.8405 ± 0.0000 | 0.4567 ± 0.0000 | 0.5000 ± 0.0000 |
| 30% | Coordinate Median | 0.8411 ± 0.0424 | 0.5715 ± 0.0653 | 0.7977 ± 0.0622 |
| 30% | Trimmed Mean | 0.8544 ± 0.0141 | 0.5423 ± 0.0883 | 0.6982 ± 0.1344 |
| 30% | Multi Krum | 0.8562 ± 0.0146 | 0.5501 ± 0.0879 | 0.7054 ± 0.1440 |
| 30% | Cosine Trust | 0.8405 ± 0.0000 | 0.4567 ± 0.0000 | 0.5000 ± 0.0000 |
| 50% | FedAvg Undefended | 0.8405 ± 0.0000 | 0.4567 ± 0.0000 | 0.5000 ± 0.0000 |
| 50% | Coordinate Median | 0.7933 ± 0.1055 | 0.4656 ± 0.0201 | 0.6452 ± 0.0896 |
| 50% | Trimmed Mean | 0.8405 ± 0.0000 | 0.4567 ± 0.0000 | 0.5000 ± 0.0000 |
| 50% | Multi Krum | 0.4638 ± 0.3249 | 0.3613 ± 0.2312 | 0.7134 ± 0.1318 |
| 50% | Cosine Trust | 0.8405 ± 0.0000 | 0.4567 ± 0.0000 | 0.5000 ± 0.0000 |

**Table 7.** Cross-dataset transfer Edge-IIoTset → WUSTL-IIoT-2021 — *provenance: measured; 3 semantically shared features (tcp.len, http.content_length, tcp.connection.synack); 50,000 of 1,194,464 target flows; source model centrally trained on the shared-feature subset (not the FL checkpoint)*

| Setting | Accuracy | Macro-F1 | ROC-AUC | PR-AUC |
|---|---:|---:|---:|---:|
| Zero-shot (source scaler, no target labels) | 0.0717 ± 0.0001 | 0.0669 ± 0.0001 | 0.6602 ± 0.3625 | 0.4053 ± 0.3634 |
| Fine-tuned on 20 % of target | 0.5857 ± 0.4692 | 0.3158 ± 0.2272 | 0.6945 ± 0.2666 | 0.3612 ± 0.3965 |
| From scratch on the same 20 % of target | 0.9276 ± 0.0016 | 0.4831 ± 0.0016 | 0.8389 ± 0.3278 | 0.6307 ± 0.2641 |

Edge-IIoTset is packet-level; WUSTL-IIoT-2021 is flow-level. Only 3 semantically shared features exist; zero-shot transfer is reported as a negative result.

