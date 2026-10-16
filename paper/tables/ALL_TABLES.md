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

**Table 3.** Role-based ML-KEM-768 + AES-256-GCM overhead — *provenance: measured; 1,000 iterations after 50 warm-up; kyber-py pure-Python FIPS-203 reference implementation*

| Operation | Role | Frequency | Median (ms) | P95 (ms) | Std (ms) | Overhead |
|---|---|---|---:|---:|---:|---|
| ML-KEM-768 KeyGen | Server | 1 × per FL round (reused across clients) | 6.8259 | 10.0072 | 1.3838 | pk 1184 B / sk 2400 B |
| ML-KEM-768 Encaps | Client | 1 × per client uplink | 9.1113 | 13.1704 | 1.8549 | ct 1088 B |
| ML-KEM-768 Decaps | Server | 1 × per client uplink | 12.3505 | 17.1974 | 2.3260 | ss 32 B |
| AES-256-GCM encrypt | Client | 1 × per client uplink | 0.1344 | 0.2013 | 0.0396 | payload 25,000 B |
| AES-256-GCM decrypt | Server | 1 × per client uplink | 0.0575 | 0.0927 | 0.0253 | nonce 12 B + tag 16 B |
| **KEM total (keygen+encaps+decaps)** | Server + Client | Combined cycle | **28.2877** | — | — | ciphertext overhead per round 1,116 B |

*Key reuse policy: The server generates one ML-KEM-768 keypair per round and broadcasts its public key. Each participating client encapsulates once, and the server decapsulates once per reporting client.*

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

**Table 6.** Robustness to Byzantine clients — *provenance: measured; K = 20, 15 rounds, 10,000 samples, 5 seeds*

| Attack | Dirichlet α | Malicious clients | Defense | Accuracy | Macro-F1 | ROC-AUC |
|---|---:|---|---|---:|---:|---:|
| label_flip | 0.1 | 0% | FedAvg Undefended | 0.8603 ± 0.0114 | 0.5690 ± 0.0642 | 0.8284 ± 0.0240 |
| label_flip | 0.1 | 0% | Coordinate Median | 0.5306 ± 0.3190 | 0.3828 ± 0.1730 | 0.7487 ± 0.0433 |
| label_flip | 0.1 | 0% | Trimmed Mean | 0.7199 ± 0.3135 | 0.5100 ± 0.2278 | 0.8194 ± 0.0353 |
| label_flip | 0.1 | 0% | Multi Krum | 0.6315 ± 0.3121 | 0.4066 ± 0.1569 | 0.6277 ± 0.0395 |
| label_flip | 0.1 | 0% | Cosine Trust NormBounded | 0.4639 ± 0.3499 | 0.3015 ± 0.1599 | 0.6853 ± 0.0636 |
| label_flip | 0.1 | 10% | FedAvg Undefended | 0.7203 ± 0.3120 | 0.4806 ± 0.2000 | 0.8200 ± 0.0454 |
| label_flip | 0.1 | 10% | Coordinate Median | 0.5051 ± 0.3367 | 0.3559 ± 0.1846 | 0.7468 ± 0.0507 |
| label_flip | 0.1 | 10% | Trimmed Mean | 0.7192 ± 0.3131 | 0.4917 ± 0.2128 | 0.7857 ± 0.0860 |
| label_flip | 0.1 | 10% | Multi Krum | 0.4319 ± 0.3730 | 0.2652 ± 0.1748 | 0.6019 ± 0.0411 |
| label_flip | 0.1 | 10% | Cosine Trust NormBounded | 0.4319 ± 0.3730 | 0.2652 ± 0.1748 | 0.6237 ± 0.0882 |
| label_flip | 0.1 | 20% | FedAvg Undefended | 0.5768 ± 0.3810 | 0.3797 ± 0.2252 | 0.7876 ± 0.0742 |
| label_flip | 0.1 | 20% | Coordinate Median | 0.5656 ± 0.3714 | 0.4012 ± 0.2535 | 0.7102 ± 0.0403 |
| label_flip | 0.1 | 20% | Trimmed Mean | 0.6509 ± 0.3102 | 0.4585 ± 0.1845 | 0.7492 ± 0.0953 |
| label_flip | 0.1 | 20% | Multi Krum | 0.4333 ± 0.3749 | 0.2815 ± 0.1991 | 0.5717 ± 0.1168 |
| label_flip | 0.1 | 20% | Cosine Trust NormBounded | 0.5681 ± 0.3730 | 0.3290 ± 0.1748 | 0.5860 ± 0.0916 |
| label_flip | 0.1 | 30% | FedAvg Undefended | 0.8500 ± 0.0131 | 0.5272 ± 0.1028 | 0.8047 ± 0.0433 |
| label_flip | 0.1 | 30% | Coordinate Median | 0.6509 ± 0.2943 | 0.4576 ± 0.1859 | 0.7036 ± 0.0621 |
| label_flip | 0.1 | 30% | Trimmed Mean | 0.7449 ± 0.2191 | 0.4475 ± 0.0590 | 0.7047 ± 0.1019 |
| label_flip | 0.1 | 30% | Multi Krum | 0.5110 ± 0.3373 | 0.3644 ± 0.2196 | 0.4904 ± 0.1167 |
| label_flip | 0.1 | 30% | Cosine Trust NormBounded | 0.7062 ± 0.3056 | 0.4046 ± 0.1514 | 0.6271 ± 0.0931 |
| label_flip | 0.5 | 0% | FedAvg Undefended | 0.8694 ± 0.0031 | 0.6217 ± 0.0248 | 0.8595 ± 0.0056 |
| label_flip | 0.5 | 0% | Coordinate Median | 0.8702 ± 0.0064 | 0.6408 ± 0.0427 | 0.8513 ± 0.0097 |
| label_flip | 0.5 | 0% | Trimmed Mean | 0.8694 ± 0.0031 | 0.6217 ± 0.0248 | 0.8522 ± 0.0064 |
| label_flip | 0.5 | 0% | Multi Krum | 0.8543 ± 0.0187 | 0.5877 ± 0.0327 | 0.7605 ± 0.0257 |
| label_flip | 0.5 | 0% | Cosine Trust NormBounded | 0.8669 ± 0.0025 | 0.6052 ± 0.0122 | 0.8112 ± 0.0261 |
| label_flip | 0.5 | 10% | FedAvg Undefended | 0.8665 ± 0.0061 | 0.6210 ± 0.0309 | 0.8537 ± 0.0105 |
| label_flip | 0.5 | 10% | Coordinate Median | 0.8171 ± 0.1215 | 0.6188 ± 0.0511 | 0.8473 ± 0.0224 |
| label_flip | 0.5 | 10% | Trimmed Mean | 0.8696 ± 0.0031 | 0.6369 ± 0.0367 | 0.8548 ± 0.0090 |
| label_flip | 0.5 | 10% | Multi Krum | 0.8087 ± 0.1041 | 0.5615 ± 0.0302 | 0.7286 ± 0.0487 |
| label_flip | 0.5 | 10% | Cosine Trust NormBounded | 0.7982 ± 0.1570 | 0.5914 ± 0.0660 | 0.8014 ± 0.0297 |
| label_flip | 0.5 | 20% | FedAvg Undefended | 0.8680 ± 0.0000 | 0.6107 ± 0.0000 | 0.8555 ± 0.0079 |
| label_flip | 0.5 | 20% | Coordinate Median | 0.7454 ± 0.1716 | 0.5957 ± 0.0796 | 0.8326 ± 0.0222 |
| label_flip | 0.5 | 20% | Trimmed Mean | 0.8255 ± 0.0990 | 0.6151 ± 0.0318 | 0.8246 ± 0.0478 |
| label_flip | 0.5 | 20% | Multi Krum | 0.6598 ± 0.3010 | 0.4772 ± 0.2063 | 0.7017 ± 0.0806 |
| label_flip | 0.5 | 20% | Cosine Trust NormBounded | 0.7250 ± 0.1924 | 0.5698 ± 0.0832 | 0.7825 ± 0.0548 |
| label_flip | 0.5 | 30% | FedAvg Undefended | 0.8187 ± 0.1079 | 0.6002 ± 0.0458 | 0.8116 ± 0.0821 |
| label_flip | 0.5 | 30% | Coordinate Median | 0.6785 ± 0.3080 | 0.5079 ± 0.2078 | 0.7902 ± 0.0576 |
| label_flip | 0.5 | 30% | Trimmed Mean | 0.7238 ± 0.3155 | 0.5041 ± 0.2064 | 0.7700 ± 0.1043 |
| label_flip | 0.5 | 30% | Multi Krum | 0.6375 ± 0.3072 | 0.4496 ± 0.1824 | 0.7002 ± 0.0507 |
| label_flip | 0.5 | 30% | Cosine Trust NormBounded | 0.6707 ± 0.3076 | 0.4916 ± 0.1993 | 0.7603 ± 0.0549 |
| label_flip | 1.0 | 0% | FedAvg Undefended | 0.8694 ± 0.0031 | 0.6217 ± 0.0248 | 0.8595 ± 0.0055 |
| label_flip | 1.0 | 0% | Coordinate Median | 0.8762 ± 0.0056 | 0.6692 ± 0.0372 | 0.8659 ± 0.0054 |
| label_flip | 1.0 | 0% | Trimmed Mean | 0.8749 ± 0.0048 | 0.6621 ± 0.0326 | 0.8629 ± 0.0046 |
| label_flip | 1.0 | 0% | Multi Krum | 0.8642 ± 0.0050 | 0.5926 ± 0.0261 | 0.7917 ± 0.0482 |
| label_flip | 1.0 | 0% | Cosine Trust NormBounded | 0.8680 ± 0.0000 | 0.6107 ± 0.0000 | 0.8546 ± 0.0078 |
| label_flip | 1.0 | 10% | FedAvg Undefended | 0.8708 ± 0.0038 | 0.6328 ± 0.0303 | 0.8586 ± 0.0083 |
| label_flip | 1.0 | 10% | Coordinate Median | 0.8776 ± 0.0036 | 0.6803 ± 0.0194 | 0.8672 ± 0.0037 |
| label_flip | 1.0 | 10% | Trimmed Mean | 0.8735 ± 0.0057 | 0.6510 ± 0.0396 | 0.8627 ± 0.0033 |
| label_flip | 1.0 | 10% | Multi Krum | 0.8654 ± 0.0050 | 0.5986 ± 0.0261 | 0.8014 ± 0.0405 |
| label_flip | 1.0 | 10% | Cosine Trust NormBounded | 0.8680 ± 0.0000 | 0.6107 ± 0.0000 | 0.8528 ± 0.0072 |
| label_flip | 1.0 | 20% | FedAvg Undefended | 0.8708 ± 0.0038 | 0.6328 ± 0.0303 | 0.8553 ± 0.0089 |
| label_flip | 1.0 | 20% | Coordinate Median | 0.8775 ± 0.0060 | 0.6763 ± 0.0398 | 0.8604 ± 0.0091 |
| label_flip | 1.0 | 20% | Trimmed Mean | 0.8748 ± 0.0068 | 0.6581 ± 0.0457 | 0.8593 ± 0.0058 |
| label_flip | 1.0 | 20% | Multi Krum | 0.8638 ± 0.0094 | 0.5880 ± 0.0506 | 0.7676 ± 0.0574 |
| label_flip | 1.0 | 20% | Cosine Trust NormBounded | 0.8694 ± 0.0031 | 0.6217 ± 0.0248 | 0.8483 ± 0.0172 |
| label_flip | 1.0 | 30% | FedAvg Undefended | 0.8682 ± 0.0089 | 0.6169 ± 0.0537 | 0.8467 ± 0.0164 |
| label_flip | 1.0 | 30% | Coordinate Median | 0.8675 ± 0.0176 | 0.6529 ± 0.0460 | 0.8582 ± 0.0086 |
| label_flip | 1.0 | 30% | Trimmed Mean | 0.8721 ± 0.0061 | 0.6399 ± 0.0420 | 0.8553 ± 0.0155 |
| label_flip | 1.0 | 30% | Multi Krum | 0.8642 ± 0.0050 | 0.5926 ± 0.0261 | 0.7920 ± 0.0552 |
| label_flip | 1.0 | 30% | Cosine Trust NormBounded | 0.8707 ± 0.0060 | 0.6288 ± 0.0406 | 0.8413 ± 0.0114 |
| sign_flip | 0.1 | 0% | FedAvg Undefended | 0.8603 ± 0.0114 | 0.5690 ± 0.0642 | 0.8284 ± 0.0240 |
| sign_flip | 0.1 | 0% | Coordinate Median | 0.5306 ± 0.3190 | 0.3828 ± 0.1730 | 0.7487 ± 0.0433 |
| sign_flip | 0.1 | 0% | Trimmed Mean | 0.7199 ± 0.3135 | 0.5100 ± 0.2278 | 0.8194 ± 0.0353 |
| sign_flip | 0.1 | 0% | Multi Krum | 0.6315 ± 0.3121 | 0.4066 ± 0.1569 | 0.6277 ± 0.0395 |
| sign_flip | 0.1 | 0% | Cosine Trust NormBounded | 0.4639 ± 0.3499 | 0.3015 ± 0.1599 | 0.6853 ± 0.0636 |
| sign_flip | 0.1 | 10% | FedAvg Undefended | 0.7117 ± 0.3089 | 0.4354 ± 0.1780 | 0.6640 ± 0.2362 |
| sign_flip | 0.1 | 10% | Coordinate Median | 0.4970 ± 0.3431 | 0.3399 ± 0.1864 | 0.7392 ± 0.0482 |
| sign_flip | 0.1 | 10% | Trimmed Mean | 0.6685 ± 0.2986 | 0.4410 ± 0.1800 | 0.7753 ± 0.0698 |
| sign_flip | 0.1 | 10% | Multi Krum | 0.5108 ± 0.3414 | 0.3400 ± 0.1861 | 0.6316 ± 0.0754 |
| sign_flip | 0.1 | 10% | Cosine Trust NormBounded | 0.4319 ± 0.3730 | 0.2652 ± 0.1748 | 0.6249 ± 0.0996 |
| sign_flip | 0.1 | 20% | FedAvg Undefended | 0.4144 ± 0.2944 | 0.3359 ± 0.2112 | 0.4994 ± 0.2547 |
| sign_flip | 0.1 | 20% | Coordinate Median | 0.5799 ± 0.3840 | 0.4131 ± 0.2659 | 0.7014 ± 0.0334 |
| sign_flip | 0.1 | 20% | Trimmed Mean | 0.6466 ± 0.3068 | 0.4322 ± 0.1763 | 0.7351 ± 0.1278 |
| sign_flip | 0.1 | 20% | Multi Krum | 0.4319 ± 0.3730 | 0.2652 ± 0.1748 | 0.5769 ± 0.1275 |
| sign_flip | 0.1 | 20% | Cosine Trust NormBounded | 0.5681 ± 0.3730 | 0.3290 ± 0.1748 | 0.6029 ± 0.1027 |
| sign_flip | 0.1 | 30% | FedAvg Undefended | 0.4708 ± 0.3484 | 0.3014 ± 0.1597 | 0.4923 ± 0.1550 |
| sign_flip | 0.1 | 30% | Coordinate Median | 0.6681 ± 0.2895 | 0.4290 ± 0.1691 | 0.6847 ± 0.0258 |
| sign_flip | 0.1 | 30% | Trimmed Mean | 0.8465 ± 0.0082 | 0.4996 ± 0.0593 | 0.6505 ± 0.1305 |
| sign_flip | 0.1 | 30% | Multi Krum | 0.4880 ± 0.3352 | 0.3681 ± 0.2150 | 0.6334 ± 0.0625 |
| sign_flip | 0.1 | 30% | Cosine Trust NormBounded | 0.7105 ± 0.3083 | 0.4306 ± 0.1831 | 0.6431 ± 0.1065 |
| sign_flip | 0.5 | 0% | FedAvg Undefended | 0.8694 ± 0.0031 | 0.6217 ± 0.0248 | 0.8595 ± 0.0056 |
| sign_flip | 0.5 | 0% | Coordinate Median | 0.8702 ± 0.0064 | 0.6408 ± 0.0427 | 0.8513 ± 0.0097 |
| sign_flip | 0.5 | 0% | Trimmed Mean | 0.8694 ± 0.0031 | 0.6217 ± 0.0248 | 0.8522 ± 0.0064 |
| sign_flip | 0.5 | 0% | Multi Krum | 0.8543 ± 0.0187 | 0.5877 ± 0.0327 | 0.7605 ± 0.0257 |
| sign_flip | 0.5 | 0% | Cosine Trust NormBounded | 0.8669 ± 0.0025 | 0.6052 ± 0.0122 | 0.8112 ± 0.0261 |
| sign_flip | 0.5 | 10% | FedAvg Undefended | 0.5791 ± 0.3832 | 0.3906 ± 0.2394 | 0.6662 ± 0.2106 |
| sign_flip | 0.5 | 10% | Coordinate Median | 0.8006 ± 0.1584 | 0.6040 ± 0.0767 | 0.8377 ± 0.0231 |
| sign_flip | 0.5 | 10% | Trimmed Mean | 0.8685 ± 0.0090 | 0.6317 ± 0.0624 | 0.8470 ± 0.0222 |
| sign_flip | 0.5 | 10% | Multi Krum | 0.8547 ± 0.0102 | 0.5394 ± 0.0574 | 0.7298 ± 0.0732 |
| sign_flip | 0.5 | 10% | Cosine Trust NormBounded | 0.7985 ± 0.1533 | 0.5886 ± 0.0603 | 0.8003 ± 0.0312 |
| sign_flip | 0.5 | 20% | FedAvg Undefended | 0.2938 ± 0.3056 | 0.2000 ± 0.1435 | 0.3981 ± 0.2126 |
| sign_flip | 0.5 | 20% | Coordinate Median | 0.7438 ± 0.1741 | 0.5944 ± 0.0816 | 0.8286 ± 0.0238 |
| sign_flip | 0.5 | 20% | Trimmed Mean | 0.8684 ± 0.0075 | 0.6186 ± 0.0449 | 0.8212 ± 0.0456 |
| sign_flip | 0.5 | 20% | Multi Krum | 0.8512 ± 0.0047 | 0.5562 ± 0.0768 | 0.7412 ± 0.0526 |
| sign_flip | 0.5 | 20% | Cosine Trust NormBounded | 0.7206 ± 0.1942 | 0.5421 ± 0.0585 | 0.7728 ± 0.0659 |
| sign_flip | 0.5 | 30% | FedAvg Undefended | 0.1487 ± 0.0115 | 0.1312 ± 0.0078 | 0.2886 ± 0.0762 |
| sign_flip | 0.5 | 30% | Coordinate Median | 0.6708 ± 0.2921 | 0.4746 ± 0.1763 | 0.7545 ± 0.0510 |
| sign_flip | 0.5 | 30% | Trimmed Mean | 0.7150 ± 0.3108 | 0.4541 ± 0.1928 | 0.6930 ± 0.0987 |
| sign_flip | 0.5 | 30% | Multi Krum | 0.7112 ± 0.3085 | 0.4346 ± 0.1699 | 0.6811 ± 0.0719 |
| sign_flip | 0.5 | 30% | Cosine Trust NormBounded | 0.6667 ± 0.3043 | 0.4684 ± 0.1939 | 0.7331 ± 0.0631 |
| sign_flip | 1.0 | 0% | FedAvg Undefended | 0.8694 ± 0.0031 | 0.6217 ± 0.0248 | 0.8595 ± 0.0055 |
| sign_flip | 1.0 | 0% | Coordinate Median | 0.8762 ± 0.0056 | 0.6692 ± 0.0372 | 0.8659 ± 0.0054 |
| sign_flip | 1.0 | 0% | Trimmed Mean | 0.8749 ± 0.0048 | 0.6621 ± 0.0326 | 0.8629 ± 0.0046 |
| sign_flip | 1.0 | 0% | Multi Krum | 0.8642 ± 0.0050 | 0.5926 ± 0.0261 | 0.7917 ± 0.0482 |
| sign_flip | 1.0 | 0% | Cosine Trust NormBounded | 0.8680 ± 0.0000 | 0.6107 ± 0.0000 | 0.8546 ± 0.0078 |
| sign_flip | 1.0 | 10% | FedAvg Undefended | 0.7247 ± 0.3161 | 0.5115 ± 0.2144 | 0.7934 ± 0.0920 |
| sign_flip | 1.0 | 10% | Coordinate Median | 0.8748 ± 0.0068 | 0.6581 ± 0.0457 | 0.8670 ± 0.0033 |
| sign_flip | 1.0 | 10% | Trimmed Mean | 0.8721 ± 0.0061 | 0.6399 ± 0.0420 | 0.8601 ± 0.0063 |
| sign_flip | 1.0 | 10% | Multi Krum | 0.8645 ± 0.0052 | 0.5929 ± 0.0263 | 0.7962 ± 0.0438 |
| sign_flip | 1.0 | 10% | Cosine Trust NormBounded | 0.8680 ± 0.0000 | 0.6107 ± 0.0000 | 0.8507 ± 0.0070 |
| sign_flip | 1.0 | 20% | FedAvg Undefended | 0.1581 ± 0.0031 | 0.1380 ± 0.0010 | 0.3585 ± 0.0912 |
| sign_flip | 1.0 | 20% | Coordinate Median | 0.8734 ± 0.0074 | 0.6470 ± 0.0498 | 0.8600 ± 0.0114 |
| sign_flip | 1.0 | 20% | Trimmed Mean | 0.8694 ± 0.0031 | 0.6217 ± 0.0248 | 0.8516 ± 0.0134 |
| sign_flip | 1.0 | 20% | Multi Krum | 0.8626 ± 0.0091 | 0.5821 ± 0.0490 | 0.7817 ± 0.0653 |
| sign_flip | 1.0 | 20% | Cosine Trust NormBounded | 0.8669 ± 0.0025 | 0.6052 ± 0.0122 | 0.8478 ± 0.0173 |
| sign_flip | 1.0 | 30% | FedAvg Undefended | 0.2913 ± 0.3072 | 0.1980 ± 0.1448 | 0.3651 ± 0.0674 |
| sign_flip | 1.0 | 30% | Coordinate Median | 0.8645 ± 0.0201 | 0.6364 ± 0.0456 | 0.8384 ± 0.0286 |
| sign_flip | 1.0 | 30% | Trimmed Mean | 0.7120 ± 0.3090 | 0.4390 ± 0.1779 | 0.6689 ± 0.2045 |
| sign_flip | 1.0 | 30% | Multi Krum | 0.8655 ± 0.0064 | 0.6012 ± 0.0374 | 0.8087 ± 0.0589 |
| sign_flip | 1.0 | 30% | Cosine Trust NormBounded | 0.8694 ± 0.0031 | 0.6217 ± 0.0248 | 0.8317 ± 0.0282 |
| combined | 0.1 | 0% | FedAvg Undefended | 0.8603 ± 0.0114 | 0.5690 ± 0.0642 | 0.8284 ± 0.0240 |
| combined | 0.1 | 0% | Coordinate Median | 0.5306 ± 0.3190 | 0.3828 ± 0.1730 | 0.7487 ± 0.0433 |
| combined | 0.1 | 0% | Trimmed Mean | 0.7199 ± 0.3135 | 0.5100 ± 0.2278 | 0.8194 ± 0.0353 |
| combined | 0.1 | 0% | Multi Krum | 0.6315 ± 0.3121 | 0.4066 ± 0.1569 | 0.6277 ± 0.0395 |
| combined | 0.1 | 0% | Cosine Trust NormBounded | 0.4639 ± 0.3499 | 0.3015 ± 0.1599 | 0.6853 ± 0.0636 |
| combined | 0.1 | 10% | FedAvg Undefended | 0.8559 ± 0.0142 | 0.5436 ± 0.0801 | 0.7758 ± 0.1108 |
| combined | 0.1 | 10% | Coordinate Median | 0.4657 ± 0.3515 | 0.3208 ± 0.1759 | 0.7486 ± 0.0448 |
| combined | 0.1 | 10% | Trimmed Mean | 0.8607 ± 0.0119 | 0.5845 ± 0.0722 | 0.8144 ± 0.0433 |
| combined | 0.1 | 10% | Multi Krum | 0.5108 ± 0.3414 | 0.3400 ± 0.1861 | 0.6054 ± 0.0507 |
| combined | 0.1 | 10% | Cosine Trust NormBounded | 0.4319 ± 0.3730 | 0.2652 ± 0.1748 | 0.6338 ± 0.0855 |
| combined | 0.1 | 20% | FedAvg Undefended | 0.8504 ± 0.0137 | 0.5128 ± 0.0775 | 0.6780 ± 0.1295 |
| combined | 0.1 | 20% | Coordinate Median | 0.4893 ± 0.3355 | 0.3522 ± 0.1723 | 0.7450 ± 0.0435 |
| combined | 0.1 | 20% | Trimmed Mean | 0.7197 ± 0.3134 | 0.4798 ± 0.2016 | 0.8122 ± 0.0527 |
| combined | 0.1 | 20% | Multi Krum | 0.2957 ± 0.3046 | 0.2014 ± 0.1427 | 0.6291 ± 0.0347 |
| combined | 0.1 | 20% | Cosine Trust NormBounded | 0.4319 ± 0.3730 | 0.2652 ± 0.1748 | 0.6463 ± 0.0793 |
| combined | 0.1 | 30% | FedAvg Undefended | 0.7153 ± 0.3110 | 0.4544 ± 0.1932 | 0.6664 ± 0.1167 |
| combined | 0.1 | 30% | Coordinate Median | 0.5104 ± 0.3476 | 0.3683 ± 0.2180 | 0.7175 ± 0.0938 |
| combined | 0.1 | 30% | Trimmed Mean | 0.6940 ± 0.3033 | 0.4861 ± 0.2072 | 0.7477 ± 0.0996 |
| combined | 0.1 | 30% | Multi Krum | 0.4319 ± 0.3730 | 0.2652 ± 0.1748 | 0.5756 ± 0.0694 |
| combined | 0.1 | 30% | Cosine Trust NormBounded | 0.4338 ± 0.3756 | 0.2769 ± 0.1919 | 0.6665 ± 0.0713 |
| combined | 0.5 | 0% | FedAvg Undefended | 0.8694 ± 0.0031 | 0.6217 ± 0.0248 | 0.8595 ± 0.0056 |
| combined | 0.5 | 0% | Coordinate Median | 0.8702 ± 0.0064 | 0.6408 ± 0.0427 | 0.8513 ± 0.0097 |
| combined | 0.5 | 0% | Trimmed Mean | 0.8694 ± 0.0031 | 0.6217 ± 0.0248 | 0.8522 ± 0.0064 |
| combined | 0.5 | 0% | Multi Krum | 0.8543 ± 0.0187 | 0.5877 ± 0.0327 | 0.7605 ± 0.0257 |
| combined | 0.5 | 0% | Cosine Trust NormBounded | 0.8669 ± 0.0025 | 0.6052 ± 0.0122 | 0.8112 ± 0.0261 |
| combined | 0.5 | 10% | FedAvg Undefended | 0.8614 ± 0.0119 | 0.5744 ± 0.0669 | 0.7358 ± 0.1385 |
| combined | 0.5 | 10% | Coordinate Median | 0.8702 ± 0.0064 | 0.6408 ± 0.0427 | 0.8542 ± 0.0097 |
| combined | 0.5 | 10% | Trimmed Mean | 0.8683 ± 0.0044 | 0.6163 ± 0.0302 | 0.8522 ± 0.0130 |
| combined | 0.5 | 10% | Multi Krum | 0.8591 ± 0.0067 | 0.5647 ± 0.0356 | 0.7658 ± 0.0330 |
| combined | 0.5 | 10% | Cosine Trust NormBounded | 0.8644 ± 0.0080 | 0.5916 ± 0.0427 | 0.8094 ± 0.0260 |
| combined | 0.5 | 20% | FedAvg Undefended | 0.8570 ± 0.0151 | 0.5491 ± 0.0843 | 0.6292 ± 0.0961 |
| combined | 0.5 | 20% | Coordinate Median | 0.8707 ± 0.0037 | 0.6303 ± 0.0273 | 0.8467 ± 0.0154 |
| combined | 0.5 | 20% | Trimmed Mean | 0.8669 ± 0.0025 | 0.6052 ± 0.0122 | 0.8330 ± 0.0240 |
| combined | 0.5 | 20% | Multi Krum | 0.8645 ± 0.0132 | 0.6110 ± 0.0661 | 0.7738 ± 0.0424 |
| combined | 0.5 | 20% | Cosine Trust NormBounded | 0.8669 ± 0.0025 | 0.6052 ± 0.0122 | 0.7975 ± 0.0205 |
| combined | 0.5 | 30% | FedAvg Undefended | 0.8603 ± 0.0114 | 0.5690 ± 0.0642 | 0.6310 ± 0.1102 |
| combined | 0.5 | 30% | Coordinate Median | 0.8696 ± 0.0071 | 0.6234 ± 0.0453 | 0.8330 ± 0.0287 |
| combined | 0.5 | 30% | Trimmed Mean | 0.8652 ± 0.0150 | 0.5980 ± 0.0883 | 0.7744 ± 0.1076 |
| combined | 0.5 | 30% | Multi Krum | 0.7638 ± 0.1520 | 0.5477 ± 0.0727 | 0.7489 ± 0.0410 |
| combined | 0.5 | 30% | Cosine Trust NormBounded | 0.8570 ± 0.0151 | 0.5491 ± 0.0843 | 0.7883 ± 0.0346 |
| combined | 1.0 | 0% | FedAvg Undefended | 0.8694 ± 0.0031 | 0.6217 ± 0.0248 | 0.8595 ± 0.0055 |
| combined | 1.0 | 0% | Coordinate Median | 0.8762 ± 0.0056 | 0.6692 ± 0.0372 | 0.8659 ± 0.0054 |
| combined | 1.0 | 0% | Trimmed Mean | 0.8749 ± 0.0048 | 0.6621 ± 0.0326 | 0.8629 ± 0.0046 |
| combined | 1.0 | 0% | Multi Krum | 0.8642 ± 0.0050 | 0.5926 ± 0.0261 | 0.7917 ± 0.0482 |
| combined | 1.0 | 0% | Cosine Trust NormBounded | 0.8680 ± 0.0000 | 0.6107 ± 0.0000 | 0.8546 ± 0.0078 |
| combined | 1.0 | 10% | FedAvg Undefended | 0.8669 ± 0.0025 | 0.6052 ± 0.0122 | 0.8249 ± 0.0400 |
| combined | 1.0 | 10% | Coordinate Median | 0.8748 ± 0.0068 | 0.6581 ± 0.0457 | 0.8642 ± 0.0040 |
| combined | 1.0 | 10% | Trimmed Mean | 0.8707 ± 0.0060 | 0.6288 ± 0.0406 | 0.8626 ± 0.0030 |
| combined | 1.0 | 10% | Multi Krum | 0.8645 ± 0.0052 | 0.5929 ± 0.0263 | 0.7917 ± 0.0405 |
| combined | 1.0 | 10% | Cosine Trust NormBounded | 0.8680 ± 0.0000 | 0.6107 ± 0.0000 | 0.8537 ± 0.0068 |
| combined | 1.0 | 20% | FedAvg Undefended | 0.8669 ± 0.0025 | 0.6052 ± 0.0122 | 0.6961 ± 0.1008 |
| combined | 1.0 | 20% | Coordinate Median | 0.8734 ± 0.0074 | 0.6470 ± 0.0498 | 0.8609 ± 0.0064 |
| combined | 1.0 | 20% | Trimmed Mean | 0.8694 ± 0.0031 | 0.6217 ± 0.0248 | 0.8505 ± 0.0044 |
| combined | 1.0 | 20% | Multi Krum | 0.8626 ± 0.0091 | 0.5821 ± 0.0490 | 0.7857 ± 0.0686 |
| combined | 1.0 | 20% | Cosine Trust NormBounded | 0.8680 ± 0.0000 | 0.6107 ± 0.0000 | 0.8458 ± 0.0053 |
| combined | 1.0 | 30% | FedAvg Undefended | 0.8570 ± 0.0151 | 0.5491 ± 0.0843 | 0.6135 ± 0.0808 |
| combined | 1.0 | 30% | Coordinate Median | 0.8720 ± 0.0060 | 0.6374 ± 0.0404 | 0.8502 ± 0.0082 |
| combined | 1.0 | 30% | Trimmed Mean | 0.8669 ± 0.0025 | 0.6052 ± 0.0122 | 0.7666 ± 0.1022 |
| combined | 1.0 | 30% | Multi Krum | 0.8655 ± 0.0064 | 0.6012 ± 0.0374 | 0.8099 ± 0.0594 |
| combined | 1.0 | 30% | Cosine Trust NormBounded | 0.8669 ± 0.0025 | 0.6052 ± 0.0122 | 0.8237 ± 0.0263 |
| alie_formula | 0.1 | 0% | FedAvg Undefended | 0.8603 ± 0.0114 | 0.5690 ± 0.0642 | 0.8284 ± 0.0240 |
| alie_formula | 0.1 | 0% | Coordinate Median | 0.5306 ± 0.3190 | 0.3828 ± 0.1730 | 0.7487 ± 0.0433 |
| alie_formula | 0.1 | 0% | Trimmed Mean | 0.7199 ± 0.3135 | 0.5100 ± 0.2278 | 0.8194 ± 0.0353 |
| alie_formula | 0.1 | 0% | Multi Krum | 0.6315 ± 0.3121 | 0.4066 ± 0.1569 | 0.6277 ± 0.0395 |
| alie_formula | 0.1 | 0% | Cosine Trust NormBounded | 0.4639 ± 0.3499 | 0.3015 ± 0.1599 | 0.6853 ± 0.0636 |
| alie_formula | 0.1 | 10% | FedAvg Undefended | 0.8614 ± 0.0119 | 0.5744 ± 0.0669 | 0.8215 ± 0.0383 |
| alie_formula | 0.1 | 10% | Coordinate Median | 0.5864 ± 0.2896 | 0.4354 ± 0.1759 | 0.7686 ± 0.0562 |
| alie_formula | 0.1 | 10% | Trimmed Mean | 0.7208 ± 0.3140 | 0.4852 ± 0.2055 | 0.8127 ± 0.0435 |
| alie_formula | 0.1 | 10% | Multi Krum | 0.5035 ± 0.3406 | 0.3349 ± 0.1806 | 0.6394 ± 0.0135 |
| alie_formula | 0.1 | 10% | Cosine Trust NormBounded | 0.5736 ± 0.3782 | 0.3598 ± 0.2124 | 0.7174 ± 0.0751 |
| alie_formula | 0.1 | 20% | FedAvg Undefended | 0.8604 ± 0.0133 | 0.5843 ± 0.0954 | 0.8330 ± 0.0269 |
| alie_formula | 0.1 | 20% | Coordinate Median | 0.8022 ± 0.1226 | 0.5645 ± 0.0461 | 0.7926 ± 0.0459 |
| alie_formula | 0.1 | 20% | Trimmed Mean | 0.8113 ± 0.1167 | 0.5915 ± 0.0976 | 0.8137 ± 0.0440 |
| alie_formula | 0.1 | 20% | Multi Krum | 0.6489 ± 0.3010 | 0.4155 ± 0.1580 | 0.6361 ± 0.0204 |
| alie_formula | 0.1 | 20% | Cosine Trust NormBounded | 0.8019 ± 0.1112 | 0.5261 ± 0.0676 | 0.7449 ± 0.0875 |
| alie_formula | 0.1 | 30% | FedAvg Undefended | 0.8603 ± 0.0114 | 0.5690 ± 0.0642 | 0.8135 ± 0.0486 |
| alie_formula | 0.1 | 30% | Coordinate Median | 0.8626 ± 0.0080 | 0.5963 ± 0.0464 | 0.7961 ± 0.0578 |
| alie_formula | 0.1 | 30% | Trimmed Mean | 0.8625 ± 0.0123 | 0.5799 ± 0.0689 | 0.7895 ± 0.0698 |
| alie_formula | 0.1 | 30% | Multi Krum | 0.6489 ± 0.3010 | 0.4155 ± 0.1580 | 0.6520 ± 0.0368 |
| alie_formula | 0.1 | 30% | Cosine Trust NormBounded | 0.8534 ± 0.0139 | 0.5300 ± 0.0774 | 0.7717 ± 0.0684 |
| alie_formula | 0.5 | 0% | FedAvg Undefended | 0.8694 ± 0.0031 | 0.6217 ± 0.0248 | 0.8595 ± 0.0056 |
| alie_formula | 0.5 | 0% | Coordinate Median | 0.8702 ± 0.0064 | 0.6408 ± 0.0427 | 0.8513 ± 0.0097 |
| alie_formula | 0.5 | 0% | Trimmed Mean | 0.8694 ± 0.0031 | 0.6217 ± 0.0248 | 0.8522 ± 0.0064 |
| alie_formula | 0.5 | 0% | Multi Krum | 0.8543 ± 0.0187 | 0.5877 ± 0.0327 | 0.7605 ± 0.0257 |
| alie_formula | 0.5 | 0% | Cosine Trust NormBounded | 0.8669 ± 0.0025 | 0.6052 ± 0.0122 | 0.8112 ± 0.0261 |
| alie_formula | 0.5 | 10% | FedAvg Undefended | 0.8669 ± 0.0025 | 0.6052 ± 0.0122 | 0.8533 ± 0.0105 |
| alie_formula | 0.5 | 10% | Coordinate Median | 0.8689 ± 0.0080 | 0.6335 ± 0.0394 | 0.8561 ± 0.0098 |
| alie_formula | 0.5 | 10% | Trimmed Mean | 0.8683 ± 0.0044 | 0.6163 ± 0.0302 | 0.8511 ± 0.0106 |
| alie_formula | 0.5 | 10% | Multi Krum | 0.8584 ± 0.0209 | 0.6127 ± 0.0366 | 0.8018 ± 0.0528 |
| alie_formula | 0.5 | 10% | Cosine Trust NormBounded | 0.8669 ± 0.0025 | 0.6052 ± 0.0122 | 0.8202 ± 0.0276 |
| alie_formula | 0.5 | 20% | FedAvg Undefended | 0.8694 ± 0.0031 | 0.6217 ± 0.0248 | 0.8599 ± 0.0030 |
| alie_formula | 0.5 | 20% | Coordinate Median | 0.8694 ± 0.0031 | 0.6217 ± 0.0248 | 0.8540 ± 0.0083 |
| alie_formula | 0.5 | 20% | Trimmed Mean | 0.8680 ± 0.0000 | 0.6107 ± 0.0000 | 0.8529 ± 0.0091 |
| alie_formula | 0.5 | 20% | Multi Krum | 0.8078 ± 0.1041 | 0.5735 ± 0.0837 | 0.7354 ± 0.1021 |
| alie_formula | 0.5 | 20% | Cosine Trust NormBounded | 0.8680 ± 0.0000 | 0.6107 ± 0.0000 | 0.8384 ± 0.0246 |
| alie_formula | 0.5 | 30% | FedAvg Undefended | 0.8710 ± 0.0074 | 0.6345 ± 0.0481 | 0.8517 ± 0.0171 |
| alie_formula | 0.5 | 30% | Coordinate Median | 0.8708 ± 0.0038 | 0.6328 ± 0.0303 | 0.8454 ± 0.0349 |
| alie_formula | 0.5 | 30% | Trimmed Mean | 0.8708 ± 0.0038 | 0.6328 ± 0.0303 | 0.8511 ± 0.0245 |
| alie_formula | 0.5 | 30% | Multi Krum | 0.8625 ± 0.0123 | 0.5799 ± 0.0689 | 0.7634 ± 0.0932 |
| alie_formula | 0.5 | 30% | Cosine Trust NormBounded | 0.8683 ± 0.0044 | 0.6163 ± 0.0302 | 0.8462 ± 0.0305 |
| alie_formula | 1.0 | 0% | FedAvg Undefended | 0.8694 ± 0.0031 | 0.6217 ± 0.0248 | 0.8595 ± 0.0055 |
| alie_formula | 1.0 | 0% | Coordinate Median | 0.8762 ± 0.0056 | 0.6692 ± 0.0372 | 0.8659 ± 0.0054 |
| alie_formula | 1.0 | 0% | Trimmed Mean | 0.8749 ± 0.0048 | 0.6621 ± 0.0326 | 0.8629 ± 0.0046 |
| alie_formula | 1.0 | 0% | Multi Krum | 0.8642 ± 0.0050 | 0.5926 ± 0.0261 | 0.7917 ± 0.0482 |
| alie_formula | 1.0 | 0% | Cosine Trust NormBounded | 0.8680 ± 0.0000 | 0.6107 ± 0.0000 | 0.8546 ± 0.0078 |
| alie_formula | 1.0 | 10% | FedAvg Undefended | 0.8694 ± 0.0031 | 0.6217 ± 0.0248 | 0.8580 ± 0.0070 |
| alie_formula | 1.0 | 10% | Coordinate Median | 0.8748 ± 0.0068 | 0.6581 ± 0.0457 | 0.8632 ± 0.0035 |
| alie_formula | 1.0 | 10% | Trimmed Mean | 0.8721 ± 0.0061 | 0.6399 ± 0.0420 | 0.8633 ± 0.0023 |
| alie_formula | 1.0 | 10% | Multi Krum | 0.8707 ± 0.0060 | 0.6288 ± 0.0406 | 0.8607 ± 0.0060 |
| alie_formula | 1.0 | 10% | Cosine Trust NormBounded | 0.8680 ± 0.0000 | 0.6107 ± 0.0000 | 0.8548 ± 0.0090 |
| alie_formula | 1.0 | 20% | FedAvg Undefended | 0.8708 ± 0.0038 | 0.6328 ± 0.0303 | 0.8596 ± 0.0053 |
| alie_formula | 1.0 | 20% | Coordinate Median | 0.8735 ± 0.0057 | 0.6510 ± 0.0396 | 0.8590 ± 0.0047 |
| alie_formula | 1.0 | 20% | Trimmed Mean | 0.8749 ± 0.0048 | 0.6621 ± 0.0326 | 0.8629 ± 0.0073 |
| alie_formula | 1.0 | 20% | Multi Krum | 0.8735 ± 0.0057 | 0.6510 ± 0.0396 | 0.8592 ± 0.0056 |
| alie_formula | 1.0 | 20% | Cosine Trust NormBounded | 0.8680 ± 0.0000 | 0.6107 ± 0.0000 | 0.8544 ± 0.0091 |
| alie_formula | 1.0 | 30% | FedAvg Undefended | 0.8707 ± 0.0060 | 0.6288 ± 0.0406 | 0.8610 ± 0.0021 |
| alie_formula | 1.0 | 30% | Coordinate Median | 0.8735 ± 0.0057 | 0.6510 ± 0.0396 | 0.8632 ± 0.0032 |
| alie_formula | 1.0 | 30% | Trimmed Mean | 0.8721 ± 0.0061 | 0.6399 ± 0.0420 | 0.8636 ± 0.0048 |
| alie_formula | 1.0 | 30% | Multi Krum | 0.8735 ± 0.0057 | 0.6510 ± 0.0396 | 0.8633 ± 0.0031 |
| alie_formula | 1.0 | 30% | Cosine Trust NormBounded | 0.8707 ± 0.0060 | 0.6288 ± 0.0406 | 0.8601 ± 0.0029 |
| alie_z1.0 | 0.1 | 0% | FedAvg Undefended | 0.8603 ± 0.0114 | 0.5690 ± 0.0642 | 0.8284 ± 0.0240 |
| alie_z1.0 | 0.1 | 0% | Coordinate Median | 0.5306 ± 0.3190 | 0.3828 ± 0.1730 | 0.7487 ± 0.0433 |
| alie_z1.0 | 0.1 | 0% | Trimmed Mean | 0.7199 ± 0.3135 | 0.5100 ± 0.2278 | 0.8194 ± 0.0353 |
| alie_z1.0 | 0.1 | 0% | Multi Krum | 0.6315 ± 0.3121 | 0.4066 ± 0.1569 | 0.6277 ± 0.0395 |
| alie_z1.0 | 0.1 | 0% | Cosine Trust NormBounded | 0.4639 ± 0.3499 | 0.3015 ± 0.1599 | 0.6853 ± 0.0636 |
| alie_z1.0 | 0.1 | 10% | FedAvg Undefended | 0.8614 ± 0.0119 | 0.5744 ± 0.0669 | 0.8250 ± 0.0442 |
| alie_z1.0 | 0.1 | 10% | Coordinate Median | 0.5041 ± 0.3251 | 0.3670 ± 0.1670 | 0.7512 ± 0.0470 |
| alie_z1.0 | 0.1 | 10% | Trimmed Mean | 0.7208 ± 0.3140 | 0.4852 ± 0.2055 | 0.8245 ± 0.0346 |
| alie_z1.0 | 0.1 | 10% | Multi Krum | 0.4935 ± 0.3408 | 0.3282 ± 0.1740 | 0.6391 ± 0.0404 |
| alie_z1.0 | 0.1 | 10% | Cosine Trust NormBounded | 0.4319 ± 0.3730 | 0.2652 ± 0.1748 | 0.6854 ± 0.0557 |
| alie_z1.0 | 0.1 | 20% | FedAvg Undefended | 0.8686 ± 0.0050 | 0.6282 ± 0.0557 | 0.8177 ± 0.0693 |
| alie_z1.0 | 0.1 | 20% | Coordinate Median | 0.5549 ± 0.3159 | 0.4343 ± 0.2056 | 0.7610 ± 0.0375 |
| alie_z1.0 | 0.1 | 20% | Trimmed Mean | 0.7324 ± 0.3013 | 0.5357 ± 0.2082 | 0.7980 ± 0.1033 |
| alie_z1.0 | 0.1 | 20% | Multi Krum | 0.3093 ± 0.2984 | 0.2188 ± 0.1382 | 0.6414 ± 0.0357 |
| alie_z1.0 | 0.1 | 20% | Cosine Trust NormBounded | 0.5977 ± 0.2432 | 0.4513 ± 0.0915 | 0.7310 ± 0.0454 |
| alie_z1.0 | 0.1 | 30% | FedAvg Undefended | 0.8625 ± 0.0123 | 0.5799 ± 0.0689 | 0.7899 ± 0.0657 |
| alie_z1.0 | 0.1 | 30% | Coordinate Median | 0.6743 ± 0.2826 | 0.4869 ± 0.1735 | 0.7743 ± 0.0552 |
| alie_z1.0 | 0.1 | 30% | Trimmed Mean | 0.8580 ± 0.0106 | 0.5572 ± 0.0599 | 0.7252 ± 0.0967 |
| alie_z1.0 | 0.1 | 30% | Multi Krum | 0.6945 ± 0.2006 | 0.4536 ± 0.0170 | 0.6174 ± 0.0276 |
| alie_z1.0 | 0.1 | 30% | Cosine Trust NormBounded | 0.8301 ± 0.0667 | 0.5615 ± 0.0640 | 0.7218 ± 0.0351 |
| alie_z1.0 | 0.5 | 0% | FedAvg Undefended | 0.8694 ± 0.0031 | 0.6217 ± 0.0248 | 0.8595 ± 0.0056 |
| alie_z1.0 | 0.5 | 0% | Coordinate Median | 0.8702 ± 0.0064 | 0.6408 ± 0.0427 | 0.8513 ± 0.0097 |
| alie_z1.0 | 0.5 | 0% | Trimmed Mean | 0.8694 ± 0.0031 | 0.6217 ± 0.0248 | 0.8522 ± 0.0064 |
| alie_z1.0 | 0.5 | 0% | Multi Krum | 0.8543 ± 0.0187 | 0.5877 ± 0.0327 | 0.7605 ± 0.0257 |
| alie_z1.0 | 0.5 | 0% | Cosine Trust NormBounded | 0.8669 ± 0.0025 | 0.6052 ± 0.0122 | 0.8112 ± 0.0261 |
| alie_z1.0 | 0.5 | 10% | FedAvg Undefended | 0.8680 ± 0.0000 | 0.6107 ± 0.0000 | 0.8570 ± 0.0084 |
| alie_z1.0 | 0.5 | 10% | Coordinate Median | 0.8246 ± 0.1048 | 0.6241 ± 0.0445 | 0.8532 ± 0.0229 |
| alie_z1.0 | 0.5 | 10% | Trimmed Mean | 0.8703 ± 0.0044 | 0.6447 ± 0.0312 | 0.8592 ± 0.0100 |
| alie_z1.0 | 0.5 | 10% | Multi Krum | 0.8569 ± 0.0074 | 0.6039 ± 0.0521 | 0.7507 ± 0.0360 |
| alie_z1.0 | 0.5 | 10% | Cosine Trust NormBounded | 0.8669 ± 0.0025 | 0.6052 ± 0.0122 | 0.8185 ± 0.0293 |
| alie_z1.0 | 0.5 | 20% | FedAvg Undefended | 0.8694 ± 0.0031 | 0.6217 ± 0.0248 | 0.8622 ± 0.0018 |
| alie_z1.0 | 0.5 | 20% | Coordinate Median | 0.8083 ± 0.1374 | 0.6050 ± 0.0498 | 0.8554 ± 0.0172 |
| alie_z1.0 | 0.5 | 20% | Trimmed Mean | 0.8707 ± 0.0037 | 0.6303 ± 0.0273 | 0.8556 ± 0.0109 |
| alie_z1.0 | 0.5 | 20% | Multi Krum | 0.7171 ± 0.3118 | 0.5057 ± 0.2111 | 0.7558 ± 0.0803 |
| alie_z1.0 | 0.5 | 20% | Cosine Trust NormBounded | 0.8680 ± 0.0000 | 0.6107 ± 0.0000 | 0.8139 ± 0.0478 |
| alie_z1.0 | 0.5 | 30% | FedAvg Undefended | 0.8708 ± 0.0038 | 0.6328 ± 0.0303 | 0.8498 ± 0.0253 |
| alie_z1.0 | 0.5 | 30% | Coordinate Median | 0.8660 ± 0.0069 | 0.6045 ± 0.0421 | 0.8479 ± 0.0051 |
| alie_z1.0 | 0.5 | 30% | Trimmed Mean | 0.8680 ± 0.0000 | 0.6107 ± 0.0000 | 0.8358 ± 0.0190 |
| alie_z1.0 | 0.5 | 30% | Multi Krum | 0.7166 ± 0.3117 | 0.4626 ± 0.1941 | 0.7024 ± 0.0687 |
| alie_z1.0 | 0.5 | 30% | Cosine Trust NormBounded | 0.8646 ± 0.0051 | 0.5934 ± 0.0261 | 0.8452 ± 0.0148 |
| alie_z1.0 | 1.0 | 0% | FedAvg Undefended | 0.8694 ± 0.0031 | 0.6217 ± 0.0248 | 0.8595 ± 0.0055 |
| alie_z1.0 | 1.0 | 0% | Coordinate Median | 0.8762 ± 0.0056 | 0.6692 ± 0.0372 | 0.8659 ± 0.0054 |
| alie_z1.0 | 1.0 | 0% | Trimmed Mean | 0.8749 ± 0.0048 | 0.6621 ± 0.0326 | 0.8629 ± 0.0046 |
| alie_z1.0 | 1.0 | 0% | Multi Krum | 0.8642 ± 0.0050 | 0.5926 ± 0.0261 | 0.7917 ± 0.0482 |
| alie_z1.0 | 1.0 | 0% | Cosine Trust NormBounded | 0.8680 ± 0.0000 | 0.6107 ± 0.0000 | 0.8546 ± 0.0078 |
| alie_z1.0 | 1.0 | 10% | FedAvg Undefended | 0.8694 ± 0.0031 | 0.6217 ± 0.0248 | 0.8599 ± 0.0034 |
| alie_z1.0 | 1.0 | 10% | Coordinate Median | 0.8776 ± 0.0036 | 0.6803 ± 0.0194 | 0.8675 ± 0.0035 |
| alie_z1.0 | 1.0 | 10% | Trimmed Mean | 0.8748 ± 0.0068 | 0.6581 ± 0.0457 | 0.8648 ± 0.0021 |
| alie_z1.0 | 1.0 | 10% | Multi Krum | 0.8623 ± 0.0089 | 0.5817 ± 0.0488 | 0.8073 ± 0.0489 |
| alie_z1.0 | 1.0 | 10% | Cosine Trust NormBounded | 0.8680 ± 0.0000 | 0.6107 ± 0.0000 | 0.8550 ± 0.0054 |
| alie_z1.0 | 1.0 | 20% | FedAvg Undefended | 0.8735 ± 0.0057 | 0.6510 ± 0.0396 | 0.8614 ± 0.0040 |
| alie_z1.0 | 1.0 | 20% | Coordinate Median | 0.8749 ± 0.0048 | 0.6621 ± 0.0326 | 0.8621 ± 0.0061 |
| alie_z1.0 | 1.0 | 20% | Trimmed Mean | 0.8749 ± 0.0048 | 0.6621 ± 0.0326 | 0.8636 ± 0.0028 |
| alie_z1.0 | 1.0 | 20% | Multi Krum | 0.8608 ± 0.0086 | 0.5867 ± 0.0534 | 0.7968 ± 0.0799 |
| alie_z1.0 | 1.0 | 20% | Cosine Trust NormBounded | 0.8680 ± 0.0000 | 0.6107 ± 0.0000 | 0.8610 ± 0.0025 |
| alie_z1.0 | 1.0 | 30% | FedAvg Undefended | 0.8735 ± 0.0057 | 0.6510 ± 0.0396 | 0.8611 ± 0.0038 |
| alie_z1.0 | 1.0 | 30% | Coordinate Median | 0.8721 ± 0.0061 | 0.6399 ± 0.0420 | 0.8594 ± 0.0067 |
| alie_z1.0 | 1.0 | 30% | Trimmed Mean | 0.8735 ± 0.0057 | 0.6510 ± 0.0396 | 0.8630 ± 0.0039 |
| alie_z1.0 | 1.0 | 30% | Multi Krum | 0.8652 ± 0.0106 | 0.5991 ± 0.0617 | 0.8273 ± 0.0692 |
| alie_z1.0 | 1.0 | 30% | Cosine Trust NormBounded | 0.8694 ± 0.0031 | 0.6217 ± 0.0248 | 0.8588 ± 0.0101 |
| alie_z1.5 | 0.1 | 0% | FedAvg Undefended | 0.8603 ± 0.0114 | 0.5690 ± 0.0642 | 0.8284 ± 0.0240 |
| alie_z1.5 | 0.1 | 0% | Coordinate Median | 0.5306 ± 0.3190 | 0.3828 ± 0.1730 | 0.7487 ± 0.0433 |
| alie_z1.5 | 0.1 | 0% | Trimmed Mean | 0.7199 ± 0.3135 | 0.5100 ± 0.2278 | 0.8194 ± 0.0353 |
| alie_z1.5 | 0.1 | 0% | Multi Krum | 0.6315 ± 0.3121 | 0.4066 ± 0.1569 | 0.6277 ± 0.0395 |
| alie_z1.5 | 0.1 | 0% | Cosine Trust NormBounded | 0.4639 ± 0.3499 | 0.3015 ± 0.1599 | 0.6853 ± 0.0636 |
| alie_z1.5 | 0.1 | 10% | FedAvg Undefended | 0.8634 ± 0.0140 | 0.5868 ± 0.0798 | 0.8328 ± 0.0349 |
| alie_z1.5 | 0.1 | 10% | Coordinate Median | 0.5041 ± 0.3251 | 0.3670 ± 0.1670 | 0.7512 ± 0.0470 |
| alie_z1.5 | 0.1 | 10% | Trimmed Mean | 0.7208 ± 0.3140 | 0.4852 ± 0.2055 | 0.8317 ± 0.0271 |
| alie_z1.5 | 0.1 | 10% | Multi Krum | 0.5344 ± 0.3491 | 0.3371 ± 0.1829 | 0.6082 ± 0.0576 |
| alie_z1.5 | 0.1 | 10% | Cosine Trust NormBounded | 0.4319 ± 0.3730 | 0.2652 ± 0.1748 | 0.6836 ± 0.0563 |
| alie_z1.5 | 0.1 | 20% | FedAvg Undefended | 0.8715 ± 0.0078 | 0.6322 ± 0.0481 | 0.8431 ± 0.0183 |
| alie_z1.5 | 0.1 | 20% | Coordinate Median | 0.5549 ± 0.3159 | 0.4343 ± 0.2056 | 0.7610 ± 0.0375 |
| alie_z1.5 | 0.1 | 20% | Trimmed Mean | 0.7326 ± 0.3032 | 0.5282 ± 0.2061 | 0.7545 ± 0.1182 |
| alie_z1.5 | 0.1 | 20% | Multi Krum | 0.3873 ± 0.3217 | 0.2807 ± 0.1980 | 0.6261 ± 0.0338 |
| alie_z1.5 | 0.1 | 20% | Cosine Trust NormBounded | 0.5510 ± 0.2748 | 0.4112 ± 0.0989 | 0.7274 ± 0.0497 |
| alie_z1.5 | 0.1 | 30% | FedAvg Undefended | 0.8622 ± 0.0074 | 0.5807 ± 0.0390 | 0.8015 ± 0.0528 |
| alie_z1.5 | 0.1 | 30% | Coordinate Median | 0.6743 ± 0.2826 | 0.4869 ± 0.1735 | 0.7664 ± 0.0633 |
| alie_z1.5 | 0.1 | 30% | Trimmed Mean | 0.8504 ± 0.0137 | 0.5128 ± 0.0775 | 0.6764 ± 0.1247 |
| alie_z1.5 | 0.1 | 30% | Multi Krum | 0.6470 ± 0.2994 | 0.4038 ± 0.1507 | 0.5982 ± 0.0476 |
| alie_z1.5 | 0.1 | 30% | Cosine Trust NormBounded | 0.7938 ± 0.1367 | 0.5702 ± 0.0871 | 0.7169 ± 0.0419 |
| alie_z1.5 | 0.5 | 0% | FedAvg Undefended | 0.8694 ± 0.0031 | 0.6217 ± 0.0248 | 0.8595 ± 0.0056 |
| alie_z1.5 | 0.5 | 0% | Coordinate Median | 0.8702 ± 0.0064 | 0.6408 ± 0.0427 | 0.8513 ± 0.0097 |
| alie_z1.5 | 0.5 | 0% | Trimmed Mean | 0.8694 ± 0.0031 | 0.6217 ± 0.0248 | 0.8522 ± 0.0064 |
| alie_z1.5 | 0.5 | 0% | Multi Krum | 0.8543 ± 0.0187 | 0.5877 ± 0.0327 | 0.7605 ± 0.0257 |
| alie_z1.5 | 0.5 | 0% | Cosine Trust NormBounded | 0.8669 ± 0.0025 | 0.6052 ± 0.0122 | 0.8112 ± 0.0261 |
| alie_z1.5 | 0.5 | 10% | FedAvg Undefended | 0.8694 ± 0.0031 | 0.6217 ± 0.0248 | 0.8576 ± 0.0075 |
| alie_z1.5 | 0.5 | 10% | Coordinate Median | 0.8246 ± 0.1048 | 0.6241 ± 0.0445 | 0.8532 ± 0.0229 |
| alie_z1.5 | 0.5 | 10% | Trimmed Mean | 0.8703 ± 0.0044 | 0.6447 ± 0.0312 | 0.8593 ± 0.0096 |
| alie_z1.5 | 0.5 | 10% | Multi Krum | 0.8572 ± 0.0069 | 0.6043 ± 0.0527 | 0.7658 ± 0.0464 |
| alie_z1.5 | 0.5 | 10% | Cosine Trust NormBounded | 0.8669 ± 0.0025 | 0.6052 ± 0.0122 | 0.8183 ± 0.0295 |
| alie_z1.5 | 0.5 | 20% | FedAvg Undefended | 0.8680 ± 0.0000 | 0.6107 ± 0.0000 | 0.8627 ± 0.0020 |
| alie_z1.5 | 0.5 | 20% | Coordinate Median | 0.8083 ± 0.1374 | 0.6050 ± 0.0498 | 0.8556 ± 0.0172 |
| alie_z1.5 | 0.5 | 20% | Trimmed Mean | 0.8693 ± 0.0029 | 0.6193 ± 0.0192 | 0.8549 ± 0.0118 |
| alie_z1.5 | 0.5 | 20% | Multi Krum | 0.8576 ± 0.0068 | 0.5918 ± 0.0575 | 0.7683 ± 0.0611 |
| alie_z1.5 | 0.5 | 20% | Cosine Trust NormBounded | 0.8669 ± 0.0025 | 0.6052 ± 0.0122 | 0.8117 ± 0.0386 |
| alie_z1.5 | 0.5 | 30% | FedAvg Undefended | 0.8694 ± 0.0031 | 0.6217 ± 0.0248 | 0.8362 ± 0.0367 |
| alie_z1.5 | 0.5 | 30% | Coordinate Median | 0.8660 ± 0.0069 | 0.6045 ± 0.0421 | 0.8431 ± 0.0137 |
| alie_z1.5 | 0.5 | 30% | Trimmed Mean | 0.8658 ± 0.0030 | 0.5998 ± 0.0149 | 0.8412 ± 0.0165 |
| alie_z1.5 | 0.5 | 30% | Multi Krum | 0.7207 ± 0.3138 | 0.4876 ± 0.2011 | 0.7502 ± 0.0795 |
| alie_z1.5 | 0.5 | 30% | Cosine Trust NormBounded | 0.8634 ± 0.0063 | 0.5871 ± 0.0322 | 0.8224 ± 0.0323 |
| alie_z1.5 | 1.0 | 0% | FedAvg Undefended | 0.8694 ± 0.0031 | 0.6217 ± 0.0248 | 0.8595 ± 0.0055 |
| alie_z1.5 | 1.0 | 0% | Coordinate Median | 0.8762 ± 0.0056 | 0.6692 ± 0.0372 | 0.8659 ± 0.0054 |
| alie_z1.5 | 1.0 | 0% | Trimmed Mean | 0.8749 ± 0.0048 | 0.6621 ± 0.0326 | 0.8629 ± 0.0046 |
| alie_z1.5 | 1.0 | 0% | Multi Krum | 0.8642 ± 0.0050 | 0.5926 ± 0.0261 | 0.7917 ± 0.0482 |
| alie_z1.5 | 1.0 | 0% | Cosine Trust NormBounded | 0.8680 ± 0.0000 | 0.6107 ± 0.0000 | 0.8546 ± 0.0078 |
| alie_z1.5 | 1.0 | 10% | FedAvg Undefended | 0.8708 ± 0.0038 | 0.6328 ± 0.0303 | 0.8614 ± 0.0036 |
| alie_z1.5 | 1.0 | 10% | Coordinate Median | 0.8776 ± 0.0036 | 0.6803 ± 0.0194 | 0.8675 ± 0.0035 |
| alie_z1.5 | 1.0 | 10% | Trimmed Mean | 0.8748 ± 0.0068 | 0.6581 ± 0.0457 | 0.8664 ± 0.0026 |
| alie_z1.5 | 1.0 | 10% | Multi Krum | 0.8669 ± 0.0025 | 0.6052 ± 0.0122 | 0.7904 ± 0.0548 |
| alie_z1.5 | 1.0 | 10% | Cosine Trust NormBounded | 0.8680 ± 0.0000 | 0.6107 ± 0.0000 | 0.8550 ± 0.0054 |
| alie_z1.5 | 1.0 | 20% | FedAvg Undefended | 0.8749 ± 0.0048 | 0.6621 ± 0.0326 | 0.8626 ± 0.0021 |
| alie_z1.5 | 1.0 | 20% | Coordinate Median | 0.8749 ± 0.0048 | 0.6621 ± 0.0326 | 0.8617 ± 0.0064 |
| alie_z1.5 | 1.0 | 20% | Trimmed Mean | 0.8749 ± 0.0048 | 0.6621 ± 0.0326 | 0.8626 ± 0.0031 |
| alie_z1.5 | 1.0 | 20% | Multi Krum | 0.8626 ± 0.0091 | 0.5821 ± 0.0490 | 0.7901 ± 0.0578 |
| alie_z1.5 | 1.0 | 20% | Cosine Trust NormBounded | 0.8680 ± 0.0000 | 0.6107 ± 0.0000 | 0.8601 ± 0.0030 |
| alie_z1.5 | 1.0 | 30% | FedAvg Undefended | 0.8735 ± 0.0057 | 0.6510 ± 0.0396 | 0.8635 ± 0.0031 |
| alie_z1.5 | 1.0 | 30% | Coordinate Median | 0.8721 ± 0.0061 | 0.6399 ± 0.0420 | 0.8558 ± 0.0070 |
| alie_z1.5 | 1.0 | 30% | Trimmed Mean | 0.8721 ± 0.0061 | 0.6399 ± 0.0420 | 0.8615 ± 0.0036 |
| alie_z1.5 | 1.0 | 30% | Multi Krum | 0.8625 ± 0.0106 | 0.5845 ± 0.0603 | 0.8152 ± 0.0514 |
| alie_z1.5 | 1.0 | 30% | Cosine Trust NormBounded | 0.8683 ± 0.0044 | 0.6163 ± 0.0302 | 0.8539 ± 0.0195 |

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
| Single-sample inference latency, median | 2.5221 ms | measured | batch = 1, 200 warm-up, 2000 timed |
| Single-sample inference latency, P95 / P99 | 3.9607 / 5.3815 ms | measured | same run |
| Throughput at batch = 1 | 396.49 samples/s | measured | 1000 / median latency |
| Process RSS | 429.71 MB | measured | psutil.Process().memory_info().rss |
| Trainable parameters | 43,138 | measured | sum(p.numel()) |
| Serialized float32 size | 168.51 KB | measured | params × 4 |
| Median FL round time (SCAFFOLD, random split) | 6.05 s | measured | from Table 4 run |
| Energy per round | 211.84 J | **estimated** | round time × assumed 35.0 W TDP |
| Uplink payload per round (FedAvg / FedProx, Top-k 30%) | 117.66 KB | measured | sparse weights + indices (120,486 B) |
| Uplink payload per round (SCAFFOLD, Top-k 30%) | 295.23 KB | measured | sparse Δw (117.66 KB) + dense Δc (177.57 KB) |
| PQC + AEAD transport overhead per round | 1.09 KB | measured | ML-KEM-768 (1,088 B) + nonce (12 B) + tag (16 B) |

**Table 10.** Systematic Data Leakage Ablation across Feature Configurations — *provenance: measured*

| Split | Model | Feature Configuration | Features Count | Accuracy | Macro-F1 | ROC-AUC | PR-AUC | MCC |
|---|---|---|---:|---:|---:|---:|---:|---:|
| random | Centralized | Full (19 semantic + 17 identifiers) | 36 | 0.9469 ± 0.0034 | 0.8976 ± 0.0050 | 0.9835 ± 0.0021 | 0.9969 ± 0.0004 | 0.7976 ± 0.0098 |
| random | Centralized | Minus IPs / Ports | 33 | 0.9137 ± 0.0011 | 0.7986 ± 0.0037 | 0.9234 ± 0.0040 | 0.9847 ± 0.0009 | 0.6364 ± 0.0053 |
| random | Centralized | Minus Seq / Ack numbers | 32 | 0.9375 ± 0.0129 | 0.8768 ± 0.0193 | 0.9761 ± 0.0052 | 0.9955 ± 0.0010 | 0.7576 ± 0.0402 |
| random | Centralized | Minus Stream / Checksum | 33 | 0.9466 ± 0.0052 | 0.8942 ± 0.0149 | 0.9852 ± 0.0014 | 0.9972 ± 0.0003 | 0.7917 ± 0.0249 |
| random | Centralized | All Identifiers Removed (19 Semantic) | 19 | 0.8924 ± 0.0019 | 0.7379 ± 0.0073 | 0.8840 ± 0.0020 | 0.9691 ± 0.0004 | 0.5272 ± 0.0109 |
| random | Centralized | Identifiers Only (17 features) | 17 | 0.8935 ± 0.0046 | 0.7570 ± 0.0315 | 0.9349 ± 0.0081 | 0.9875 ± 0.0016 | 0.5456 ± 0.0373 |
| random | FedAvg | Full (19 semantic + 17 identifiers) | 36 | 0.9125 ± 0.0114 | 0.7853 ± 0.0390 | 0.9598 ± 0.0082 | 0.9912 ± 0.0024 | 0.6309 ± 0.0558 |
| random | FedAvg | Minus IPs / Ports | 33 | 0.8973 ± 0.0075 | 0.7307 ± 0.0326 | 0.9080 ± 0.0094 | 0.9803 ± 0.0026 | 0.5546 ± 0.0375 |
| random | FedAvg | Minus Seq / Ack numbers | 32 | 0.9071 ± 0.0143 | 0.7667 ± 0.0550 | 0.9526 ± 0.0085 | 0.9901 ± 0.0026 | 0.6021 ± 0.0748 |
| random | FedAvg | Minus Stream / Checksum | 33 | 0.9146 ± 0.0117 | 0.7950 ± 0.0455 | 0.9628 ± 0.0070 | 0.9920 ± 0.0021 | 0.6415 ± 0.0586 |
| random | FedAvg | All Identifiers Removed (19 Semantic) | 19 | 0.8780 ± 0.0055 | 0.6574 ± 0.0357 | 0.8730 ± 0.0085 | 0.9658 ± 0.0018 | 0.4402 ± 0.0328 |
| random | FedAvg | Identifiers Only (17 features) | 17 | 0.8701 ± 0.0106 | 0.6176 ± 0.0563 | 0.8944 ± 0.0161 | 0.9780 ± 0.0037 | 0.3811 ± 0.0740 |
| session-disjoint | Centralized | Full (19 semantic + 17 identifiers) | 36 | 0.9200 ± 0.0435 | 0.8377 ± 0.0626 | 0.9170 ± 0.1166 | 0.9619 ± 0.0681 | 0.6906 ± 0.1066 |
| session-disjoint | Centralized | Minus IPs / Ports | 33 | 0.8873 ± 0.0408 | 0.7156 ± 0.0476 | 0.8324 ± 0.1349 | 0.9357 ± 0.0950 | 0.5059 ± 0.0649 |
| session-disjoint | Centralized | Minus Seq / Ack numbers | 32 | 0.9045 ± 0.0481 | 0.8137 ± 0.0664 | 0.9281 ± 0.0893 | 0.9710 ± 0.0504 | 0.6472 ± 0.1174 |
| session-disjoint | Centralized | Minus Stream / Checksum | 33 | 0.9214 ± 0.0434 | 0.8420 ± 0.0605 | 0.9089 ± 0.1302 | 0.9556 ± 0.0802 | 0.6954 ± 0.1090 |
| session-disjoint | Centralized | All Identifiers Removed (19 Semantic) | 19 | 0.8822 ± 0.0379 | 0.7076 ± 0.0444 | 0.8318 ± 0.1205 | 0.9323 ± 0.0862 | 0.4778 ± 0.0532 |
| session-disjoint | Centralized | Identifiers Only (17 features) | 17 | 0.8536 ± 0.0260 | 0.6706 ± 0.0419 | 0.8362 ± 0.1040 | 0.9422 ± 0.0785 | 0.3714 ± 0.0950 |
| session-disjoint | FedAvg | Full (19 semantic + 17 identifiers) | 36 | 0.8928 ± 0.0435 | 0.7276 ± 0.0684 | 0.8773 ± 0.1489 | 0.9408 ± 0.1028 | 0.5390 ± 0.0927 |
| session-disjoint | FedAvg | Minus IPs / Ports | 33 | 0.8804 ± 0.0409 | 0.6726 ± 0.0515 | 0.8219 ± 0.1473 | 0.9273 ± 0.1097 | 0.4651 ± 0.0610 |
| session-disjoint | FedAvg | Minus Seq / Ack numbers | 32 | 0.8953 ± 0.0428 | 0.7349 ± 0.0695 | 0.9180 ± 0.0671 | 0.9768 ± 0.0291 | 0.5502 ± 0.0973 |
| session-disjoint | FedAvg | Minus Stream / Checksum | 33 | 0.8916 ± 0.0417 | 0.7221 ± 0.0612 | 0.8761 ± 0.1544 | 0.9378 ± 0.1086 | 0.5308 ± 0.0819 |
| session-disjoint | FedAvg | All Identifiers Removed (19 Semantic) | 19 | 0.8776 ± 0.0400 | 0.6692 ± 0.0534 | 0.8328 ± 0.1083 | 0.9417 ± 0.0646 | 0.4476 ± 0.0609 |
| session-disjoint | FedAvg | Identifiers Only (17 features) | 17 | 0.8460 ± 0.0410 | 0.5067 ± 0.0620 | 0.8014 ± 0.1268 | 0.9281 ± 0.0989 | 0.1160 ± 0.1299 |

**Top 15 Feature Importances (Random Forest on Full 36 Features):**
1. `tcp.dstport`: 0.2618
2. `tcp.srcport`: 0.2065
3. `tcp.seq`: 0.1527
4. `tcp.ack`: 0.0723
5. `tcp.flags`: 0.0560
6. `mqtt.msgtype`: 0.0523
7. `mqtt.hdrflags`: 0.0497
8. `tcp.len`: 0.0369
9. `mqtt.len`: 0.0319
10. `tcp.ack_raw`: 0.0222
11. `tcp.checksum`: 0.0110
12. `tcp.connection.rst`: 0.0104
13. `tcp.flags.ack`: 0.0083
14. `tcp.connection.syn`: 0.0044
15. `tcp.connection.synack`: 0.0041

**Table 11.** Edge-IIoTset `dns.qry.name.len` formatting artifact audit — *provenance: measured; 157,800 rows; citation: Galal, arXiv:2608.15761*

### Part 1: Formatting artifact distribution in ML-EdgeIIoT-dataset.csv

| Raw String Representation | Normal Traffic Rows | Attack Traffic Rows | Total Rows | Attack Share (%) |
|---|---:|---:|---:|---:|
| String `"0"` | 24,272 | 0 | 24,272 | 0.00 |
| String `"0.0"` | 0 | 133,272 | 133,272 | 100.00 |
| Other string values | 29 | 227 | 256 | 88.67 |

### Part 2: Impact on Classifier Performance

| Preprocessing Recipe | Feature Representation | Test Accuracy | Test ROC-AUC | Diagnostic Finding |
|---|---|---:|---:|---|
| String One-Hot (Official Edge-IIoTset Recipe) | String categorical one-hot | 0.9998 | 1.0000 | Achieves ~1.0 ROC-AUC (99.98% accuracy) purely by memorizing the string formatting anomaly ('0' for normal vs '0.0' for attack). |
| Numeric Parsing (Strict float32) | `pd.to_numeric` | 0.8460 | 0.5007 | Collapses both '0' and '0.0' to identical 0.0, destroying the artifact and dropping ROC-AUC to chance (~0.50). |

**Table 12.** Operating points and threshold calibration under class imbalance (Edge-IIoTset Random Split) — *provenance: measured; carved 20% validation split for calibration*

| Algorithm | Operating Point | Normal Recall | Attack Recall | FPR | Precision | Macro-F1 | MCC | ROC-AUC |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| FedAvg (Adam) | Max Macro-F1 | 0.4025 | 0.9850 | 0.5975 | 0.8983 | 0.7412 | 0.5324 | 0.8705 |
| FedAvg (Adam) | FPR ≤ 5% | 0.9936 | 0.3881 | 0.0064 | 0.9970 | 0.4678 | 0.2960 | 0.8705 |
| FedAvg (SGD) | Max Macro-F1 | 0.2903 | 0.9917 | 0.7097 | 0.8821 | 0.6843 | 0.4596 | 0.8145 |
| FedAvg (SGD) | FPR ≤ 5% (unreachable; min FPR=0.0822) | 0.9407 | 0.3849 | 0.0593 | 0.9720 | 0.4554 | 0.2514 | 0.8145 |
| FedProx (SGD) | Max Macro-F1 | 0.2903 | 0.9917 | 0.7097 | 0.8821 | 0.6843 | 0.4596 | 0.8145 |
| FedProx (SGD) | FPR ≤ 5% (unreachable; min FPR=0.0822) | 0.9407 | 0.3849 | 0.0593 | 0.9720 | 0.4554 | 0.2514 | 0.8145 |
| SCAFFOLD (SGD) | Max Macro-F1 | 0.4004 | 0.9850 | 0.5996 | 0.8979 | 0.7401 | 0.5306 | 0.8581 |
| SCAFFOLD (SGD) | FPR ≤ 5% | 0.9619 | 0.4759 | 0.0381 | 0.9853 | 0.5226 | 0.3244 | 0.8581 |
| FedAvg (Class-Weighted) | Max Macro-F1 | 0.4025 | 0.9850 | 0.5975 | 0.8983 | 0.7412 | 0.5324 | 0.8673 |
| FedAvg (Class-Weighted) | FPR ≤ 5% | 0.9936 | 0.4260 | 0.0064 | 0.9972 | 0.4946 | 0.3184 | 0.8673 |

**Table 13.** Systematic Data Leakage, Chronological Generalization, and Identifier-Shortcut Audit on WUSTL-IIoT-2021 — *provenance: measured; full dataset: 1,194,464 rows; evaluation sample: 15,000 flows*

### Part 1: Leakage and Shortcut Feature Group Ablation Across Three Evaluation Splits

| Split | Model | Feature Configuration | Features Count | Accuracy | Macro-F1 | ROC-AUC | PR-AUC | MCC |
|---|---|---|---:|---:|---:|---:|---:|---:|
| random | Centralized MLP | Full (all groups + semantic) | 54 | 0.9995 ± 0.0002 | 0.9983 ± 0.0007 | 0.9988 ± 0.0019 | 0.9901 ± 0.0040 | 0.9966 ± 0.0013 |
| random | Centralized MLP | Minus G1 (hosts/ports: SrcAddr, DstAddr, Sport, Dport) | 50 | 0.9991 ± 0.0003 | 0.9966 ± 0.0010 | 0.9989 ± 0.0020 | 0.9950 ± 0.0049 | 0.9931 ± 0.0020 |
| random | Centralized MLP | Minus G2 (IP-ID counters: sIpId, dIpId) | 52 | 0.9995 ± 0.0003 | 0.9980 ± 0.0011 | 0.9988 ± 0.0019 | 0.9867 ± 0.0118 | 0.9961 ± 0.0022 |
| random | Centralized MLP | Minus G3 (timestamps: StartTime, LastTime) | 52 | 0.9995 ± 0.0002 | 0.9983 ± 0.0007 | 0.9989 ± 0.0019 | 0.9922 ± 0.0091 | 0.9966 ± 0.0013 |
| random | Centralized MLP | Minus G4 (host fingerprints: sTtl, dTtl, sTos) | 51 | 0.9997 ± 0.0002 | 0.9988 ± 0.0009 | 0.9989 ± 0.0019 | 0.9917 ± 0.0060 | 0.9975 ± 0.0017 |
| random | Centralized MLP | Semantic only (36 flow statistics + one-hot Proto) | 43 | 0.9960 ± 0.0011 | 0.9855 ± 0.0040 | 0.9985 ± 0.0018 | 0.9839 ± 0.0166 | 0.9712 ± 0.0079 |
| random | Centralized MLP | Identifiers only (G1–G4) | 11 | 0.9993 ± 0.0005 | 0.9975 ± 0.0020 | 0.9998 ± 0.0001 | 0.9963 ± 0.0038 | 0.9951 ± 0.0039 |
| random | FedAvg (Adam) | Full (all groups + semantic) | 54 | 0.9985 ± 0.0007 | 0.9943 ± 0.0026 | 0.9955 ± 0.0061 | 0.9906 ± 0.0044 | 0.9886 ± 0.0052 |
| random | FedAvg (Adam) | Minus G1 (hosts/ports: SrcAddr, DstAddr, Sport, Dport) | 50 | 0.9964 ± 0.0010 | 0.9864 ± 0.0041 | 0.9915 ± 0.0075 | 0.9862 ± 0.0075 | 0.9732 ± 0.0079 |
| random | FedAvg (Adam) | Minus G2 (IP-ID counters: sIpId, dIpId) | 52 | 0.9983 ± 0.0007 | 0.9938 ± 0.0028 | 0.9950 ± 0.0058 | 0.9882 ± 0.0040 | 0.9876 ± 0.0056 |
| random | FedAvg (Adam) | Minus G3 (timestamps: StartTime, LastTime) | 52 | 0.9985 ± 0.0006 | 0.9946 ± 0.0021 | 0.9946 ± 0.0059 | 0.9892 ± 0.0035 | 0.9891 ± 0.0042 |
| random | FedAvg (Adam) | Minus G4 (host fingerprints: sTtl, dTtl, sTos) | 51 | 0.9984 ± 0.0008 | 0.9940 ± 0.0030 | 0.9931 ± 0.0086 | 0.9879 ± 0.0085 | 0.9881 ± 0.0059 |
| random | FedAvg (Adam) | Semantic only (36 flow statistics + one-hot Proto) | 43 | 0.9897 ± 0.0038 | 0.9599 ± 0.0167 | 0.9907 ± 0.0076 | 0.9718 ± 0.0111 | 0.9219 ± 0.0311 |
| random | FedAvg (Adam) | Identifiers only (G1–G4) | 11 | 0.9984 ± 0.0013 | 0.9940 ± 0.0047 | 0.9956 ± 0.0054 | 0.9901 ± 0.0059 | 0.9881 ± 0.0094 |
| session-disjoint | Centralized MLP | Full (all groups + semantic) | 54 | 0.9995 ± 0.0003 | 0.9980 ± 0.0010 | 0.9972 ± 0.0021 | 0.9936 ± 0.0052 | 0.9961 ± 0.0020 |
| session-disjoint | Centralized MLP | Minus G1 (hosts/ports: SrcAddr, DstAddr, Sport, Dport) | 50 | 0.9988 ± 0.0008 | 0.9956 ± 0.0029 | 0.9972 ± 0.0022 | 0.9967 ± 0.0021 | 0.9913 ± 0.0058 |
| session-disjoint | Centralized MLP | Minus G2 (IP-ID counters: sIpId, dIpId) | 52 | 0.9995 ± 0.0002 | 0.9983 ± 0.0007 | 0.9972 ± 0.0021 | 0.9939 ± 0.0040 | 0.9967 ± 0.0014 |
| session-disjoint | Centralized MLP | Minus G3 (timestamps: StartTime, LastTime) | 52 | 0.9992 ± 0.0019 | 0.9972 ± 0.0065 | 0.9972 ± 0.0021 | 0.9939 ± 0.0041 | 0.9944 ± 0.0126 |
| session-disjoint | Centralized MLP | Minus G4 (host fingerprints: sTtl, dTtl, sTos) | 51 | 0.9994 ± 0.0002 | 0.9978 ± 0.0008 | 0.9972 ± 0.0022 | 0.9943 ± 0.0043 | 0.9956 ± 0.0016 |
| session-disjoint | Centralized MLP | Semantic only (36 flow statistics + one-hot Proto) | 43 | 0.9957 ± 0.0013 | 0.9842 ± 0.0047 | 0.9970 ± 0.0021 | 0.9913 ± 0.0063 | 0.9687 ± 0.0093 |
| session-disjoint | Centralized MLP | Identifiers only (G1–G4) | 11 | 0.9992 ± 0.0009 | 0.9973 ± 0.0033 | 0.9997 ± 0.0006 | 0.9915 ± 0.0182 | 0.9946 ± 0.0066 |
| session-disjoint | FedAvg (Adam) | Full (all groups + semantic) | 54 | 0.9983 ± 0.0019 | 0.9937 ± 0.0067 | 0.9961 ± 0.0027 | 0.9924 ± 0.0034 | 0.9875 ± 0.0130 |
| session-disjoint | FedAvg (Adam) | Minus G1 (hosts/ports: SrcAddr, DstAddr, Sport, Dport) | 50 | 0.9963 ± 0.0027 | 0.9863 ± 0.0103 | 0.9947 ± 0.0053 | 0.9882 ± 0.0077 | 0.9731 ± 0.0198 |
| session-disjoint | FedAvg (Adam) | Minus G2 (IP-ID counters: sIpId, dIpId) | 52 | 0.9987 ± 0.0008 | 0.9953 ± 0.0027 | 0.9965 ± 0.0023 | 0.9923 ± 0.0035 | 0.9906 ± 0.0054 |
| session-disjoint | FedAvg (Adam) | Minus G3 (timestamps: StartTime, LastTime) | 52 | 0.9973 ± 0.0030 | 0.9905 ± 0.0105 | 0.9961 ± 0.0021 | 0.9870 ± 0.0228 | 0.9812 ± 0.0204 |
| session-disjoint | FedAvg (Adam) | Minus G4 (host fingerprints: sTtl, dTtl, sTos) | 51 | 0.9988 ± 0.0004 | 0.9955 ± 0.0016 | 0.9959 ± 0.0030 | 0.9922 ± 0.0024 | 0.9910 ± 0.0032 |
| session-disjoint | FedAvg (Adam) | Semantic only (36 flow statistics + one-hot Proto) | 43 | 0.9914 ± 0.0038 | 0.9674 ± 0.0150 | 0.9949 ± 0.0038 | 0.9793 ± 0.0121 | 0.9362 ± 0.0284 |
| session-disjoint | FedAvg (Adam) | Identifiers only (G1–G4) | 11 | 0.9977 ± 0.0033 | 0.9914 ± 0.0127 | 0.9951 ± 0.0112 | 0.9907 ± 0.0166 | 0.9832 ± 0.0243 |
| chronological | Centralized MLP | Full (all groups + semantic) | 54 | 0.9999 ± 0.0001 | 0.9000 ± 0.2236 | N/A* | 0.0000 ± 0.0000 | 0.0000 ± 0.0000 |
| chronological | Centralized MLP | Minus G1 (hosts/ports: SrcAddr, DstAddr, Sport, Dport) | 50 | 0.9997 ± 0.0004 | 0.7999 ± 0.2740 | N/A* | 0.0000 ± 0.0000 | 0.0000 ± 0.0000 |
| chronological | Centralized MLP | Minus G2 (IP-ID counters: sIpId, dIpId) | 52 | 0.9999 ± 0.0001 | 0.9000 ± 0.2236 | N/A* | 0.0000 ± 0.0000 | 0.0000 ± 0.0000 |
| chronological | Centralized MLP | Minus G3 (timestamps: StartTime, LastTime) | 52 | 0.9999 ± 0.0001 | 0.9000 ± 0.2236 | N/A* | 0.0000 ± 0.0000 | 0.0000 ± 0.0000 |
| chronological | Centralized MLP | Minus G4 (host fingerprints: sTtl, dTtl, sTos) | 51 | 0.9999 ± 0.0003 | 0.9000 ± 0.2237 | N/A* | 0.0000 ± 0.0000 | 0.0000 ± 0.0000 |
| chronological | Centralized MLP | Semantic only (36 flow statistics + one-hot Proto) | 43 | 0.9995 ± 0.0005 | 0.6999 ± 0.2740 | N/A* | 0.0000 ± 0.0000 | 0.0000 ± 0.0000 |
| chronological | Centralized MLP | Identifiers only (G1–G4) | 11 | 1.0000 ± 0.0000 | 1.0000 ± 0.0000 | N/A* | 0.0000 ± 0.0000 | 0.0000 ± 0.0000 |
| chronological | FedAvg (Adam) | Full (all groups + semantic) | 54 | 0.9999 ± 0.0003 | 0.9000 ± 0.2237 | N/A* | 0.0000 ± 0.0000 | 0.0000 ± 0.0000 |
| chronological | FedAvg (Adam) | Minus G1 (hosts/ports: SrcAddr, DstAddr, Sport, Dport) | 50 | 0.9995 ± 0.0010 | 0.7999 ± 0.2740 | N/A* | 0.0000 ± 0.0000 | 0.0000 ± 0.0000 |
| chronological | FedAvg (Adam) | Minus G2 (IP-ID counters: sIpId, dIpId) | 52 | 0.9999 ± 0.0001 | 0.9000 ± 0.2236 | N/A* | 0.0000 ± 0.0000 | 0.0000 ± 0.0000 |
| chronological | FedAvg (Adam) | Minus G3 (timestamps: StartTime, LastTime) | 52 | 0.9999 ± 0.0001 | 0.9000 ± 0.2236 | N/A* | 0.0000 ± 0.0000 | 0.0000 ± 0.0000 |
| chronological | FedAvg (Adam) | Minus G4 (host fingerprints: sTtl, dTtl, sTos) | 51 | 0.9999 ± 0.0003 | 0.9000 ± 0.2237 | N/A* | 0.0000 ± 0.0000 | 0.0000 ± 0.0000 |
| chronological | FedAvg (Adam) | Semantic only (36 flow statistics + one-hot Proto) | 43 | 0.9994 ± 0.0005 | 0.5998 ± 0.2237 | N/A* | 0.0000 ± 0.0000 | 0.0000 ± 0.0000 |
| chronological | FedAvg (Adam) | Identifiers only (G1–G4) | 11 | 0.9999 ± 0.0001 | 0.9000 ± 0.2236 | N/A* | 0.0000 ± 0.0000 | 0.0000 ± 0.0000 |

### Part 2: Session-Disjoint Per-Split ROC-AUC Means (5 Group Partitions × 5 Seeds = 25 Runs)

| Model | Feature Configuration | Split 0 | Split 1 | Split 2 | Split 3 | Split 4 | Overall Mean ± SD |
|---|---|---:|---:|---:|---:|---:|---:|
| Centralized MLP | Full (all groups + semantic) | 0.9953 | 0.9955 | 0.9997 | 0.9997 | 0.9956 | 0.9972 ± 0.0021 |
| Centralized MLP | Minus G1 (hosts/ports: SrcAddr, DstAddr, Sport, Dport) | 0.9952 | 0.9955 | 0.9999 | 0.9999 | 0.9956 | 0.9972 ± 0.0022 |
| Centralized MLP | Minus G2 (IP-ID counters: sIpId, dIpId) | 0.9953 | 0.9955 | 0.9998 | 0.9997 | 0.9956 | 0.9972 ± 0.0021 |
| Centralized MLP | Minus G3 (timestamps: StartTime, LastTime) | 0.9953 | 0.9955 | 0.9998 | 0.9997 | 0.9956 | 0.9972 ± 0.0021 |
| Centralized MLP | Minus G4 (host fingerprints: sTtl, dTtl, sTos) | 0.9953 | 0.9955 | 0.9998 | 0.9997 | 0.9956 | 0.9972 ± 0.0022 |
| Centralized MLP | Semantic only (36 flow statistics + one-hot Proto) | 0.9951 | 0.9955 | 0.9995 | 0.9996 | 0.9954 | 0.9970 ± 0.0021 |
| Centralized MLP | Identifiers only (G1–G4) | 1.0000 | 1.0000 | 1.0000 | 0.9986 | 1.0000 | 0.9997 ± 0.0006 |
| FedAvg (Adam) | Full (all groups + semantic) | 0.9951 | 0.9940 | 0.9981 | 0.9996 | 0.9939 | 0.9961 ± 0.0027 |
| FedAvg (Adam) | Minus G1 (hosts/ports: SrcAddr, DstAddr, Sport, Dport) | 0.9921 | 0.9953 | 0.9913 | 0.9994 | 0.9955 | 0.9947 ± 0.0053 |
| FedAvg (Adam) | Minus G2 (IP-ID counters: sIpId, dIpId) | 0.9953 | 0.9955 | 0.9979 | 0.9996 | 0.9942 | 0.9965 ± 0.0023 |
| FedAvg (Adam) | Minus G3 (timestamps: StartTime, LastTime) | 0.9953 | 0.9950 | 0.9973 | 0.9984 | 0.9947 | 0.9961 ± 0.0021 |
| FedAvg (Adam) | Minus G4 (host fingerprints: sTtl, dTtl, sTos) | 0.9950 | 0.9929 | 0.9987 | 0.9994 | 0.9934 | 0.9959 ± 0.0030 |
| FedAvg (Adam) | Semantic only (36 flow statistics + one-hot Proto) | 0.9914 | 0.9950 | 0.9960 | 0.9992 | 0.9932 | 0.9949 ± 0.0038 |
| FedAvg (Adam) | Identifiers only (G1–G4) | 0.9859 | 0.9951 | 0.9977 | 0.9994 | 0.9975 | 0.9951 ± 0.0112 |

### Part 3: Operating Points for FedAvg (Adam) on Semantic-Only Features Across All Three Splits

| Split | Operating Point | Normal Recall | Attack Recall | FPR | Precision | Macro-F1 | MCC | ROC-AUC | FPR ≤ 5% Reached |
|---|---|---:|---:|---:|---:|---:|---:|---:|:---:|
| random | Max Macro-F1 | 0.9946 | 0.9406 | 0.0054 | 0.9321 | 0.9657 | 0.9313 | 0.9961 | True |
| random | FPR ≤ 5% | 0.9946 | 0.9406 | 0.0054 | 0.9321 | 0.9657 | 0.9313 | 0.9961 | True |
| session-disjoint | Max Macro-F1 | 0.9993 | 0.9340 | 0.0007 | 0.9900 | 0.9791 | 0.9588 | 0.9914 | True |
| session-disjoint | FPR ≤ 5% | 0.9968 | 0.9434 | 0.0032 | 0.9569 | 0.9732 | 0.9464 | 0.9914 | True |
| chronological | Max Macro-F1 | 0.9997 | 0.0000 | 0.0003 | 0.0000 | 0.4999 | 0.0000 | N/A* | True |
| chronological | FPR ≤ 5% | 0.9993 | 0.0000 | 0.0007 | 0.0000 | 0.4998 | 0.0000 | N/A* | True |

### Part 4: Chronological Split Metadata & Raw String Artifact Audit

- **Full Dataset Size:** 1,194,464 rows (StartTime parse success: 100.00%)
- **Chronological Cutoff (80th Percentile):** `2019-08-19 15:24:37`
- **Pre-Cutoff Training Pool:** 955,609 rows (Attack rate: 9.11%)
- **Post-Cutoff Test Pool:** 238,855 rows (Attack rate: 0.00%, Total attack flows: 0)
- **Chronological Split Finding:** *Test period has fewer than 50 attack rows (0 attack rows in the final 20% of data).*
- **Attack Types Exclusively Pre-Cutoff:** Backdoor, CommInj, DoS, Reconn
- **Raw Text Artifact Audit:** Identified 20 raw string values occurring exclusively in one class with ≥ 100 rows.

**Top Exclusive Single-Class Categorical Values in Raw Dataset:**
| Column | Value | Exclusive Class | Row Count |
|---|---|---|---:|
| `SrcAddr` | `209.240.235.92` | attack_only | 46,615 |
| `SrcAddr` | `192.168.0.10` | attack_only | 26,797 |
| `SrcAddr` | `192.168.0.44` | normal_only | 8,317 |
| `SrcAddr` | `20.1.249.77` | attack_only | 7,220 |
| `DstAddr` | `192.168.0.1` | normal_only | 6,938 |
| `SrcAddr` | `49.48.134.64` | attack_only | 6,320 |
| `DstAddr` | `192.168.0.255` | normal_only | 3,876 |
| `SrcAddr` | `01:80:c2:00:00:0e` | normal_only | 2,529 |
| `DstAddr` | `6c:b0:ce:22:b0:57` | normal_only | 2,529 |
| `DstAddr` | `255.255.255.255` | normal_only | 1,994 |

\* *Note: ROC-AUC and PR-AUC are undefined on the chronological test split due to zero positive attack instances in the post-cutoff test period.*

