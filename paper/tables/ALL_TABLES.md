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

**Table 3.** ML-KEM-768 + AES-256-GCM overhead — *provenance: measured; 1,000 iterations after 50 warm-up; kyber-py pure-Python FIPS-203 reference implementation (upper bound on latency)*

| Operation | Median (ms) | P95 (ms) | Std (ms) | Bytes |
|---|---:|---:|---:|---:|
| ML-KEM-768 KeyGen | 3.2078 | 4.6541 | 0.6490 | pk 1184 / sk 2400 |
| ML-KEM-768 Encaps | 4.2132 | 6.1116 | 0.8393 | ct 1088 |
| ML-KEM-768 Decaps | 5.7636 | 8.4183 | 1.1600 | ss 32 |
| AES-256-GCM encrypt | 0.0648 | 0.1033 | 0.0235 | payload 25,000 |
| AES-256-GCM decrypt | 0.0237 | 0.0334 | 0.0056 | nonce 12 + tag 16 |
| **KEM total (keygen+encaps+decaps)** | **13.1846** | — | — | ciphertext overhead per round 1,116 |

**Table 4.** Federated detection performance on Edge-IIoTset — *provenance: measured; K = 20 clients, C = 0.5, Dirichlet α = 0.5, 30 rounds, 1 local epochs, batch 64, lr 0.05, 15,000 samples, 19 features, 5 seeds*

| Split | Algorithm | Accuracy | Macro-F1 | ROC-AUC | ROC-AUC 95% CI | Payload / client / round (KB) | Median round time (s) |
|---|---|---:|---:|---:|---:|---:|---:|
| random | FedAvg (Adam) | 0.8807 ± 0.0093 | 0.6697 ± 0.0535 | 0.8738 ± 0.0145 | [0.8558, 0.8918] | 117.66 | 7.24 |
| random | FedAvg (SGD) | 0.8694 ± 0.0038 | 0.6105 ± 0.0185 | 0.7932 ± 0.0114 | [0.7791, 0.8073] | 117.66 | 4.92 |
| random | FedProx (SGD) | 0.8693 ± 0.0037 | 0.6104 ± 0.0183 | 0.7931 ± 0.0113 | [0.7791, 0.8071] | 117.66 | 6.30 |
| random | SCAFFOLD (SGD) | 0.8711 ± 0.0038 | 0.6176 ± 0.0185 | 0.8093 ± 0.0338 | [0.7673, 0.8513] | 117.66 | 3.84 |
| random | *Centralized bound (10 epochs)* | 0.8909 ± 0.0035 | 0.7409 ± 0.0029 | 0.8822 ± 0.0042 | [0.8770, 0.8874] | — | — |
| random | SCAFFOLD (SGD) − FedAvg (SGD) (accuracy) | mean diff 0.0017 | paired t p = 0.2588 | Wilcoxon p = 0.0625 | | | |
| random | SCAFFOLD (SGD) − FedAvg (SGD) (ROC-AUC) | mean diff 0.0161 | paired t p = 0.2784 | Wilcoxon p = 0.8125 | | | |
| random | SCAFFOLD (SGD) − FedAvg (Adam) (accuracy) | mean diff -0.0095 | paired t p = 0.0433 | Wilcoxon p = 0.0625 | | | |
| random | SCAFFOLD (SGD) − FedAvg (Adam) (ROC-AUC) | mean diff -0.0644 | paired t p = 0.0155 | Wilcoxon p = 0.0625 | | | |
| temporal | FedAvg (Adam) | 0.8861 ± 0.0009 | 0.6611 ± 0.0188 | 0.8718 ± 0.0041 | [0.8667, 0.8770] | 117.66 | 4.14 |
| temporal | FedAvg (SGD) | 0.7771 ± 0.1412 | 0.5960 ± 0.0442 | 0.7951 ± 0.0175 | [0.7733, 0.8169] | 117.66 | 3.82 |
| temporal | FedProx (SGD) | 0.7769 ± 0.1415 | 0.5959 ± 0.0443 | 0.7950 ± 0.0177 | [0.7731, 0.8169] | 117.66 | 7.12 |
| temporal | SCAFFOLD (SGD) | 0.8808 ± 0.0044 | 0.6288 ± 0.0219 | 0.7552 ± 0.0791 | [0.6571, 0.8534] | 117.66 | 5.63 |
| temporal | *Centralized bound (10 epochs)* | 0.8957 ± 0.0034 | 0.7342 ± 0.0205 | 0.8766 ± 0.0003 | [0.8763, 0.8769] | — | — |
| temporal | SCAFFOLD (SGD) − FedAvg (SGD) (accuracy) | mean diff 0.1037 | paired t p = 0.1692 | Wilcoxon p = 0.1875 | | | |
| temporal | SCAFFOLD (SGD) − FedAvg (SGD) (ROC-AUC) | mean diff -0.0399 | paired t p = 0.2688 | Wilcoxon p = 0.3125 | | | |
| temporal | SCAFFOLD (SGD) − FedAvg (Adam) (accuracy) | mean diff -0.0053 | paired t p = 0.0728 | Wilcoxon p = 0.2500 | | | |
| temporal | SCAFFOLD (SGD) − FedAvg (Adam) (ROC-AUC) | mean diff -0.1166 | paired t p = 0.0296 | Wilcoxon p = 0.0625 | | | |

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
| 6b | FedAvg (SGD, GroupNorm, K=20 steps) | 43,138 | 0.8556 ± 0.0131 | 0.5400 ± 0.0759 | 0.7378 ± 0.0439 |
| 7 | + SCAFFOLD Drift Correction | 43,138 | 0.8619 ± 0.0111 | 0.5693 ± 0.0627 | 0.7430 ± 0.0648 |
| 8 | + Cosine Trust Scorer (20% Poisoned) | 43,138 | 0.8363 ± 0.0352 | 0.5374 ± 0.0640 | 0.6511 ± 0.0297 |

**Table 6.** Robustness to Byzantine clients — *provenance: measured; K = 20, 15 rounds, 10,000 samples, 5 seeds; attack = label flip + scaled sign flip (λ = 5)*

| Malicious clients | Defense | Accuracy | Macro-F1 | ROC-AUC |
|---|---|---:|---:|---:|
| 0% | FedAvg Undefended | 0.8636 ± 0.0025 | 0.5889 ± 0.0122 | 0.8246 ± 0.0235 |
| 0% | Coordinate Median | 0.8189 ± 0.1051 | 0.5983 ± 0.0155 | 0.8367 ± 0.0090 |
| 0% | Trimmed Mean | 0.8641 ± 0.0050 | 0.6074 ± 0.0499 | 0.8175 ± 0.0103 |
| 0% | Multi Krum | 0.8405 ± 0.0000 | 0.4567 ± 0.0000 | 0.6165 ± 0.0429 |
| 0% | Cosine Trust NormBounded | 0.8496 ± 0.0125 | 0.5462 ± 0.0590 | 0.7612 ± 0.0602 |
| 10% | FedAvg Undefended | 0.8467 ± 0.0085 | 0.4936 ± 0.0506 | 0.6732 ± 0.1607 |
| 10% | Coordinate Median | 0.8606 ± 0.0075 | 0.6035 ± 0.0426 | 0.8250 ± 0.0116 |
| 10% | Trimmed Mean | 0.8584 ± 0.0113 | 0.5778 ± 0.0696 | 0.8281 ± 0.0175 |
| 10% | Multi Krum | 0.8405 ± 0.0000 | 0.4567 ± 0.0000 | 0.6336 ± 0.0483 |
| 10% | Cosine Trust NormBounded | 0.8494 ± 0.0123 | 0.5460 ± 0.0588 | 0.7291 ± 0.0881 |
| 20% | FedAvg Undefended | 0.8405 ± 0.0000 | 0.4567 ± 0.0000 | 0.5162 ± 0.0361 |
| 20% | Coordinate Median | 0.8622 ± 0.0059 | 0.6111 ± 0.0566 | 0.8307 ± 0.0078 |
| 20% | Trimmed Mean | 0.8521 ± 0.0109 | 0.5256 ± 0.0644 | 0.8156 ± 0.0338 |
| 20% | Multi Krum | 0.8470 ± 0.0087 | 0.5157 ± 0.0593 | 0.6591 ± 0.0791 |
| 20% | Cosine Trust NormBounded | 0.8448 ± 0.0049 | 0.5023 ± 0.0469 | 0.7118 ± 0.0787 |
| 30% | FedAvg Undefended | 0.8405 ± 0.0000 | 0.4567 ± 0.0000 | 0.5000 ± 0.0000 |
| 30% | Coordinate Median | 0.8483 ± 0.0108 | 0.5172 ± 0.0846 | 0.7975 ± 0.0329 |
| 30% | Trimmed Mean | 0.8441 ± 0.0080 | 0.4855 ± 0.0644 | 0.6470 ± 0.1500 |
| 30% | Multi Krum | 0.8405 ± 0.0000 | 0.4567 ± 0.0000 | 0.6232 ± 0.0375 |
| 30% | Cosine Trust NormBounded | 0.8446 ± 0.0092 | 0.4817 ± 0.0560 | 0.7254 ± 0.1009 |
| 50% | FedAvg Undefended | 0.8405 ± 0.0000 | 0.4567 ± 0.0000 | 0.5000 ± 0.0000 |
| 50% | Coordinate Median | 0.7672 ± 0.1693 | 0.4670 ± 0.0271 | 0.6033 ± 0.1137 |
| 50% | Trimmed Mean | 0.8405 ± 0.0000 | 0.4567 ± 0.0000 | 0.5000 ± 0.0000 |
| 50% | Multi Krum | 0.8392 ± 0.0029 | 0.4841 ± 0.0613 | 0.5805 ± 0.0458 |
| 50% | Cosine Trust NormBounded | 0.8446 ± 0.0092 | 0.4817 ± 0.0560 | 0.5609 ± 0.1361 |

**Table 7.** Cross-dataset transfer Edge-IIoTset → WUSTL-IIoT-2021 — *provenance: measured; 3 semantically shared features (tcp.len, http.content_length, tcp.connection.synack); 50,000 of 1,194,464 target flows; source model centrally trained on the shared-feature subset (not the FL checkpoint)*

| Setting | Accuracy | Macro-F1 | ROC-AUC | PR-AUC |
|---|---:|---:|---:|---:|
| Zero-shot (source scaler, no target labels) | 0.0717 ± 0.0000 | 0.0669 ± 0.0000 | 0.2595 ± 0.1345 | 0.1620 ± 0.0907 |
| Fine-tuned on 20 % of target | 0.7781 ± 0.3955 | 0.6010 ± 0.3552 | 0.8894 ± 0.2177 | 0.6606 ± 0.3302 |
| From scratch on the same 20 % of target | 0.9378 ± 0.0213 | 0.5695 ± 0.1969 | 0.9854 ± 0.0031 | 0.7668 ± 0.0686 |

Edge-IIoTset is packet-level; WUSTL-IIoT-2021 is flow-level. Only 3 semantically shared features exist; zero-shot transfer is reported as a negative result.

**Table 8.** Edge resource profile (CPU only) — *provenance per row*

| Metric | Value | Provenance | Method |
|---|---:|---|---|
| Single-sample inference latency, median | 0.9275 ms | measured | batch = 1, 200 warm-up, 2000 timed |
| Single-sample inference latency, P95 / P99 | 1.3658 / 1.8506 ms | measured | same run |
| Throughput at batch = 1 | 1078.11 samples/s | measured | 1000 / median latency |
| Process RSS | 425.98 MB | measured | psutil.Process().memory_info().rss |
| Trainable parameters | 43,138 | measured | sum(p.numel()) |
| Serialized float32 size | 168.51 KB | measured | params × 4 |
| Median FL round time (SCAFFOLD, random split) | 3.84 s | measured | from Table 4 run |
| Energy per round | 134.28 J | **estimated** | round time × assumed 35.0 W TDP |

**Table 9.** QUBO response-selection: QAOA (statevector simulator) vs exact ILP vs greedy — *provenance: measured; 4 actions per asset; objective = negative utility (lower is better)*

| N assets | Qubits | Trials | ILP latency (ms) | QAOA latency (ms) | QAOA gap vs ILP (%) |
|---:|---:|---:|---:|---:|---:|
| 1 | 4 | 3 | 342.18 | 377.34 | 0.00 |
| 2 | 8 | 3 | 46.23 | 869.84 | 29.96 |
| 3 | 12 | 3 | 48.97 | 1853.59 | 13.26 |

**Table 10.** Data leakage analysis: Protocol-semantic features (19) vs. Semantic + session identifiers (36) — *provenance: measured*

| Split | Model | Feature Set | Dim | Accuracy | Macro-F1 | ROC-AUC | PR-AUC | MCC |
|---|---|---|---:|---:|---:|---:|---:|---:|
| random | Centralized | Semantic (protocol-only) | 19 | 0.8909 ± 0.0035 | 0.7409 ± 0.0029 | 0.8822 ± 0.0042 | 0.9685 ± 0.0009 | 0.5243 ± 0.0103 |
| random | Centralized | Semantic + Session Identifiers | 36 | 0.9815 ± 0.0172 | 0.9623 ± 0.0375 | 0.9942 ± 0.0040 | 0.9986 ± 0.0009 | 0.9282 ± 0.0684 |
| random | FedAvg | Semantic (protocol-only) | 19 | 0.7948 ± 0.1803 | 0.6095 ± 0.0887 | 0.8164 ± 0.0143 | 0.9522 ± 0.0038 | 0.3883 ± 0.0790 |
| random | FedAvg | Semantic + Session Identifiers | 36 | 0.7682 ± 0.2127 | 0.5797 ± 0.1106 | 0.7396 ± 0.0296 | 0.9366 ± 0.0081 | 0.3218 ± 0.0554 |
| temporal | Centralized | Semantic (protocol-only) | 19 | 0.8957 ± 0.0034 | 0.7342 ± 0.0205 | 0.8766 ± 0.0003 | 0.9696 ± 0.0003 | 0.5138 ± 0.0242 |
| temporal | Centralized | Semantic + Session Identifiers | 36 | 0.9901 ± 0.0058 | 0.9800 ± 0.0120 | 0.9971 ± 0.0016 | 0.9990 ± 0.0010 | 0.9603 ± 0.0236 |
| temporal | FedAvg | Semantic (protocol-only) | 19 | 0.7965 ± 0.1328 | 0.6312 ± 0.0498 | 0.8149 ± 0.0315 | 0.9552 ± 0.0072 | 0.4133 ± 0.0499 |
| temporal | FedAvg | Semantic + Session Identifiers | 36 | 0.7443 ± 0.1735 | 0.5528 ± 0.0531 | 0.7922 ± 0.0533 | 0.9541 ± 0.0135 | 0.2911 ± 0.0541 |

**Top 15 Feature Importances (Random Forest on Semantic + Identifiers):**
1. `tcp.dstport`: 0.2656
2. `tcp.srcport`: 0.2067
3. `tcp.seq`: 0.1495
4. `tcp.ack`: 0.0709
5. `tcp.flags`: 0.0590
6. `mqtt.msgtype`: 0.0512
7. `mqtt.hdrflags`: 0.0488
8. `tcp.len`: 0.0359
9. `mqtt.len`: 0.0310
10. `tcp.ack_raw`: 0.0221
11. `tcp.checksum`: 0.0117
12. `tcp.connection.rst`: 0.0109
13. `tcp.flags.ack`: 0.0088
14. `tcp.connection.syn`: 0.0044
15. `tcp.connection.synack`: 0.0043

