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
| ML-KEM-768 KeyGen | Server | 1 × per FL round (reused across clients) | 3.2078 | 4.6541 | 0.6490 | pk 1184 B / sk 2400 B |
| ML-KEM-768 Encaps | Client | 1 × per client uplink | 4.2132 | 6.1116 | 0.8393 | ct 1088 B |
| ML-KEM-768 Decaps | Server | 1 × per client uplink | 5.7636 | 8.4183 | 1.1600 | ss 32 B |
| AES-256-GCM encrypt | Client | 1 × per client uplink | 0.0648 | 0.1033 | 0.0235 | payload 25,000 B |
| AES-256-GCM decrypt | Server | 1 × per client uplink | 0.0237 | 0.0334 | 0.0056 | nonce 12 B + tag 16 B |
| **KEM total (keygen+encaps+decaps)** | Server + Client | Combined cycle | **13.1846** | — | — | ciphertext overhead per round 1,116 B |

*Key reuse policy: The server generates one ML-KEM-768 keypair per round and broadcasts its public key. Each participating client encapsulates once, and the server decapsulates once per reporting client.*

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
| combined | 0.5 | 0% | FedAvg Undefended | 0.8636 ± 0.0025 | 0.5889 ± 0.0122 | 0.8246 ± 0.0235 |
| combined | 0.5 | 0% | Coordinate Median | 0.8189 ± 0.1051 | 0.5983 ± 0.0155 | 0.8367 ± 0.0090 |
| combined | 0.5 | 0% | Trimmed Mean | 0.8641 ± 0.0050 | 0.6074 ± 0.0499 | 0.8175 ± 0.0103 |
| combined | 0.5 | 0% | Multi Krum | 0.8405 ± 0.0000 | 0.4567 ± 0.0000 | 0.6165 ± 0.0429 |
| combined | 0.5 | 0% | Cosine Trust NormBounded | 0.8496 ± 0.0125 | 0.5462 ± 0.0590 | 0.7612 ± 0.0602 |
| combined | 0.5 | 10% | FedAvg Undefended | 0.8467 ± 0.0085 | 0.4936 ± 0.0506 | 0.6732 ± 0.1607 |
| combined | 0.5 | 10% | Coordinate Median | 0.8606 ± 0.0075 | 0.6035 ± 0.0426 | 0.8250 ± 0.0116 |
| combined | 0.5 | 10% | Trimmed Mean | 0.8584 ± 0.0113 | 0.5778 ± 0.0696 | 0.8281 ± 0.0175 |
| combined | 0.5 | 10% | Multi Krum | 0.8405 ± 0.0000 | 0.4567 ± 0.0000 | 0.6336 ± 0.0483 |
| combined | 0.5 | 10% | Cosine Trust NormBounded | 0.8494 ± 0.0123 | 0.5460 ± 0.0588 | 0.7291 ± 0.0881 |
| combined | 0.5 | 20% | FedAvg Undefended | 0.8405 ± 0.0000 | 0.4567 ± 0.0000 | 0.5162 ± 0.0361 |
| combined | 0.5 | 20% | Coordinate Median | 0.8622 ± 0.0059 | 0.6111 ± 0.0566 | 0.8307 ± 0.0078 |
| combined | 0.5 | 20% | Trimmed Mean | 0.8521 ± 0.0109 | 0.5256 ± 0.0644 | 0.8156 ± 0.0338 |
| combined | 0.5 | 20% | Multi Krum | 0.8470 ± 0.0087 | 0.5157 ± 0.0593 | 0.6591 ± 0.0791 |
| combined | 0.5 | 20% | Cosine Trust NormBounded | 0.8448 ± 0.0049 | 0.5023 ± 0.0469 | 0.7118 ± 0.0787 |
| combined | 0.5 | 30% | FedAvg Undefended | 0.8405 ± 0.0000 | 0.4567 ± 0.0000 | 0.5000 ± 0.0000 |
| combined | 0.5 | 30% | Coordinate Median | 0.8483 ± 0.0108 | 0.5172 ± 0.0846 | 0.7975 ± 0.0329 |
| combined | 0.5 | 30% | Trimmed Mean | 0.8441 ± 0.0080 | 0.4855 ± 0.0644 | 0.6470 ± 0.1500 |
| combined | 0.5 | 30% | Multi Krum | 0.8405 ± 0.0000 | 0.4567 ± 0.0000 | 0.6232 ± 0.0375 |
| combined | 0.5 | 30% | Cosine Trust NormBounded | 0.8446 ± 0.0092 | 0.4817 ± 0.0560 | 0.7254 ± 0.1009 |
| combined | 0.5 | 50% | FedAvg Undefended | 0.8405 ± 0.0000 | 0.4567 ± 0.0000 | 0.5000 ± 0.0000 |
| combined | 0.5 | 50% | Coordinate Median | 0.7672 ± 0.1693 | 0.4670 ± 0.0271 | 0.6033 ± 0.1137 |
| combined | 0.5 | 50% | Trimmed Mean | 0.8405 ± 0.0000 | 0.4567 ± 0.0000 | 0.5000 ± 0.0000 |
| combined | 0.5 | 50% | Multi Krum | 0.8392 ± 0.0029 | 0.4841 ± 0.0613 | 0.5805 ± 0.0458 |
| combined | 0.5 | 50% | Cosine Trust NormBounded | 0.8446 ± 0.0092 | 0.4817 ± 0.0560 | 0.5609 ± 0.1361 |

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
| Uplink payload per round (FedAvg / FedProx, Top-k 30%) | 117.66 KB | measured | sparse weights + indices (120,486 B) |
| Uplink payload per round (SCAFFOLD, Top-k 30%) | 295.23 KB | measured | sparse Δw (117.66 KB) + dense Δc (177.57 KB) |
| PQC + AEAD transport overhead per round | 1.09 KB | measured | ML-KEM-768 (1,088 B) + nonce (12 B) + tag (16 B) |

**Table 9.** QUBO response-selection: QAOA (statevector simulator) vs exact ILP vs greedy — *provenance: measured; 4 actions per asset; objective = negative utility (lower is better)*

| N assets | Qubits | Trials | ILP latency (ms) | QAOA latency (ms) | QAOA gap vs ILP (%) |
|---:|---:|---:|---:|---:|---:|
| 1 | 4 | 3 | 342.18 | 377.34 | 0.00 |
| 2 | 8 | 3 | 46.23 | 869.84 | 29.96 |
| 3 | 12 | 3 | 48.97 | 1853.59 | 13.26 |

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
| session-disjoint | Centralized | Full (19 semantic + 17 identifiers) | 36 | 0.8915 ± 0.0292 | 0.7987 ± 0.0627 | 0.7709 ± 0.1183 | 0.8908 ± 0.0582 | 0.6312 ± 0.1069 |
| session-disjoint | Centralized | Minus IPs / Ports | 33 | 0.9113 ± 0.0002 | 0.8406 ± 0.0004 | 0.9339 ± 0.0036 | 0.9803 ± 0.0011 | 0.7073 ± 0.0006 |
| session-disjoint | Centralized | Minus Seq / Ack numbers | 32 | 0.8925 ± 0.0316 | 0.8077 ± 0.0582 | 0.9307 ± 0.0138 | 0.9807 ± 0.0036 | 0.6405 ± 0.1102 |
| session-disjoint | Centralized | Minus Stream / Checksum | 33 | 0.8763 ± 0.0104 | 0.7639 ± 0.0186 | 0.7112 ± 0.0372 | 0.8542 ± 0.0202 | 0.5751 ± 0.0418 |
| session-disjoint | Centralized | All Identifiers Removed (19 Semantic) | 19 | 0.8318 ± 0.0000 | 0.6216 ± 0.0000 | 0.6971 ± 0.0261 | 0.8947 ± 0.0151 | 0.3669 ± 0.0000 |
| session-disjoint | Centralized | Identifiers Only (17 features) | 17 | 0.8583 ± 0.0070 | 0.7251 ± 0.0256 | 0.6595 ± 0.0041 | 0.8290 ± 0.0016 | 0.5004 ± 0.0328 |
| session-disjoint | FedAvg | Full (19 semantic + 17 identifiers) | 36 | 0.8576 ± 0.0384 | 0.6806 ± 0.1091 | 0.6789 ± 0.1690 | 0.8202 ± 0.0986 | 0.4858 ± 0.1583 |
| session-disjoint | FedAvg | Minus IPs / Ports | 33 | 0.8586 ± 0.0399 | 0.6903 ± 0.1193 | 0.6806 ± 0.2030 | 0.8362 ± 0.1219 | 0.4836 ± 0.1735 |
| session-disjoint | FedAvg | Minus Seq / Ack numbers | 32 | 0.8453 ± 0.0113 | 0.6527 ± 0.0448 | 0.8242 ± 0.0616 | 0.9443 ± 0.0266 | 0.4391 ± 0.0573 |
| session-disjoint | FedAvg | Minus Stream / Checksum | 33 | 0.8905 ± 0.0469 | 0.7698 ± 0.1315 | 0.8170 ± 0.2172 | 0.8979 ± 0.1281 | 0.6186 ± 0.1902 |
| session-disjoint | FedAvg | All Identifiers Removed (19 Semantic) | 19 | 0.8306 ± 0.0028 | 0.6119 ± 0.0216 | 0.6581 ± 0.0302 | 0.8689 ± 0.0174 | 0.3612 ± 0.0127 |
| session-disjoint | FedAvg | Identifiers Only (17 features) | 17 | 0.8034 ± 0.0051 | 0.4837 ± 0.0341 | 0.5661 ± 0.0272 | 0.7663 ± 0.0167 | 0.1309 ± 0.0868 |

**Top 15 Feature Importances (Random Forest on Full 36 Features):**
1. `tcp.dstport`: 0.2487
2. `tcp.srcport`: 0.2119
3. `tcp.seq`: 0.1530
4. `tcp.ack`: 0.0720
5. `tcp.flags`: 0.0575
6. `mqtt.msgtype`: 0.0547
7. `mqtt.hdrflags`: 0.0506
8. `tcp.len`: 0.0340
9. `mqtt.len`: 0.0339
10. `tcp.ack_raw`: 0.0222
11. `tcp.checksum`: 0.0118
12. `tcp.connection.rst`: 0.0116
13. `tcp.flags.ack`: 0.0096
14. `tcp.connection.synack`: 0.0046
15. `tcp.connection.syn`: 0.0042

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
| FedAvg (Adam) | Max Macro-F1 | 0.1992 | 1.0000 | 0.8008 | 0.8699 | 0.6313 | 0.4162 | 0.8555 |
| FedAvg (Adam) | FPR ≤ 5% | 1.0000 | 0.0000 | 0.0000 | 0.0000 | 0.1359 | 0.0000 | 0.8555 |
| FedAvg (SGD) | Max Macro-F1 | 0.1547 | 0.9996 | 0.8453 | 0.8636 | 0.5970 | 0.3644 | 0.7841 |
| FedAvg (SGD) | FPR ≤ 5% | 1.0000 | 0.0000 | 0.0000 | 0.0000 | 0.1359 | 0.0000 | 0.7841 |
| FedProx (SGD) | Max Macro-F1 | 0.1547 | 0.9996 | 0.8453 | 0.8636 | 0.5970 | 0.3644 | 0.7845 |
| FedProx (SGD) | FPR ≤ 5% | 1.0000 | 0.0000 | 0.0000 | 0.0000 | 0.1359 | 0.0000 | 0.7845 |
| SCAFFOLD (SGD) | Max Macro-F1 | 0.1547 | 1.0000 | 0.8453 | 0.8637 | 0.5974 | 0.3655 | 0.6105 |
| SCAFFOLD (SGD) | FPR ≤ 5% | 1.0000 | 0.0000 | 0.0000 | 0.0000 | 0.1359 | 0.0000 | 0.6105 |

