# How Much of Edge-IIoTset Is Leakage? An Honest Baseline for Quantum-Resistant Federated Intrusion Detection in IIoT

**Naveen Ravi**

---

### Abstract

Federated learning (FL) enables industrial IoT (IIoT) facilities to collaboratively train intrusion-detection models without consolidating raw operational telemetry. However, widely cited claims of near-perfect (>99 %) detection accuracy on the Edge-IIoTset benchmark reflect severe data snooping: session identifiers (ports and TCP sequence numbers) dominate classification and fail to generalise across non-IID clients. This paper establishes an honest empirical baseline for quantum-resistant federated intrusion detection on Edge-IIoTset under strict leakage controls. Evaluating a 19-feature protocol-semantic representation on random and temporal hold-outs, we show that centralized models drop from ROC-AUC 0.9942 with identifiers to an honest ceiling of 0.8822 (random) and 0.8766 (temporal). Across 5 random seeds and K = 20 Dirichlet-partitioned clients, federated learning approaches this honest ceiling: FedAvg with Adam achieves ROC-AUC 0.8738 ± 0.0145 (random) and 0.8718 ± 0.0041 (temporal). In contrast, we document four unambiguous negative results: (i) SCAFFOLD drift correction provides no statistically significant gain over FedAvg under identical SGD settings (paired t p = 0.2784) while inflating uplink payload by over two-fold; (ii) a compact 3,426-parameter MLP matches a 12-fold larger temporal convolutional attention encoder; (iii) zero-shot cross-dataset transfer to flow-level telemetry fails completely (ROC-AUC 0.2595); and (iv) QAOA response selection exhibits an optimality gap of 29.96 % with slower execution than classical integer linear programming. Under 20.0 % Byzantine clients, coordinate-wise median remains the most robust defense (ROC-AUC 0.8307), while norm-bounded cosine trust scoring improves upon undefended FedAvg (0.5162) to 0.7118. Transport security under NIST FIPS-203 ML-KEM-768 with AES-256-GCM adds 13.18 ms per client per round in a pure-Python reference implementation. Every number is rendered from automated execution and verified by automated checking.

**Index Terms** — Federated learning, intrusion detection, Industrial IoT, data leakage, post-quantum cryptography, ML-KEM, Byzantine robustness, Edge-IIoTset, reproducibility.

---

## I. INTRODUCTION

Industrial cyber-physical systems expose Modbus/TCP, MQTT, DNS, HTTP and ARP telemetry at many geographically separated sites. Centralising that telemetry for intrusion detection raises three practical obstacles: (i) raw packet captures contain proprietary network topology and sensitive operational data whose cross-site transfer carries regulatory and contractual risk; (ii) the parameter traffic of any distributed learner is a long-lived secret — an adversary that records it today can decrypt it once a cryptanalytically relevant quantum computer exists ("harvest now, decrypt later") [21]; and (iii) sites differ in the telemetry they observe, so a federated detector must cope with statistical heterogeneity and, in the worst case, with compromised participants.

A large body of work reports near-perfect (>99 %) accuracy on the Edge-IIoTset benchmark [1]. Much of it, as Arp et al. warn for security machine learning in general [22], is inflated by *data snooping*: features such as ephemeral TCP/UDP port numbers, sequence and acknowledgement numbers, checksums, and session identifiers allow models to memorise specific capture sessions rather than genuine attack behaviour. When evaluated on random row splits, packets from identical TCP streams populate both training and test partitions, creating an illusion of high detection performance. In this work, we demonstrate that when these identifiers are removed, detection performance drops substantially, revealing the true protocol-semantic ceiling of the dataset. Furthermore, we show that including these session identifiers actively impairs federated optimisation across non-IID edge clients, because local port assignments and sequence streams do not transfer across clients.

**Contributions.**
1. A direct empirical leakage measurement on Edge-IIoTset (protocol-semantic features vs session identifiers, across random and temporal splits, and random-forest feature importances) demonstrating that published near-perfect detection rates rely on session-identifier memorisation rather than behavioural detection (Section VI-A).
2. A leakage-controlled federated intrusion-detection benchmark establishing the honest performance ceiling across random and temporal hold-outs, evaluated over 5 seeds with Dirichlet non-IID partitions, paired statistical significance tests, and explicit per-algorithm hyperparameter configurations (Section VI-B).
3. A Byzantine-robustness comparison of five aggregation rules (coordinate-wise median, trimmed mean, Multi-Krum, norm-bounded cosine trust, and undefended FedAvg) under simultaneous label flipping and scaled sign-flip attacks across 10.0–50.0 % malicious clients (Section VI-D).
4. Concrete negative results documenting that SCAFFOLD drift correction does not significantly improve ROC-AUC under identical settings, lightweight MLPs match 12-fold larger temporal convolutional attention encoders, cross-dataset transfer from packet-level to flow-level telemetry fails zero-shot, and QAOA provides no advantage over classical ILP (Sections VI-B, VI-C, VI-E, VI-G).
5. A fully traceable and verified experimental pipeline: every result number is rendered from a single automated results repository without hand-typed values and validated by an automated checker.

The post-quantum cryptographic transport (ML-KEM-768 key encapsulation with AES-256-GCM payload encryption) serves as the underlying communications subsystem supporting the benchmark rather than a standalone algorithmic contribution; its execution costs are profiled in Section VI-F.

---

## II. RELATED WORK

**Federated intrusion detection for IoT/IIoT.** DÏoT [24] introduced federated self-learning anomaly detection on IoT gateways; Rahman et al. [26] compared centralised, on-device and federated IDS training for IoT; Popoola et al. [25] applied federated deep learning to zero-day botnet detection on IoT-edge devices. These works establish that FL is viable for IoT IDS but evaluate with random splits on identifier-rich features and do not consider quantum-safe transport or Byzantine participants.

**Edge-IIoTset.** Ferrag et al. [1] released Edge-IIoTset with 14 attack classes over a realistic IIoT testbed and reported centralised and federated baselines. Subsequent papers frequently report >99 % accuracy; we show (Section VI-A) that on protocol-semantic features alone the centralised ceiling is far lower, which we attribute to session-identifier leakage in the commonly used feature set, consistent with the pitfalls catalogued by Arp et al. [22].

**Heterogeneity-aware aggregation.** FedAvg [4] is the baseline; FedProx [5] adds a proximal term to penalise local deviation from global weights; SCAFFOLD [6] corrects client drift with control variates. Dirichlet partitioning [19] is the standard method to control non-IID statistical heterogeneity. We evaluate these rules under identical partitions and report paired significance tests across seeds.

**Communication efficiency.** Top-*k* gradient sparsification with error feedback [18], [27] reduces uplink traffic without altering convergence fixed points. We measure the *serialized* payload including indices and non-trainable buffers rather than counting kept values.

**Byzantine robustness.** Krum and Multi-Krum [12], coordinate-wise median and trimmed mean [13], and FLTrust [14] are reference defenses against poisoning and model-replacement attacks. Our cosine-similarity trust weighting applies norm bounding in the spirit of FLTrust; we evaluate it directly alongside established coordinate-wise robust rules.

**Post-quantum transport for FL.** NIST standardised ML-KEM in FIPS 203 [7] following the Kyber design [29]; Mosca [21] frames the harvest-now-decrypt-later risk. Most FL security literature assumes classical TLS. We apply ML-KEM-768 per round with HKDF [9] and AES-256-GCM [8], measuring its overhead with a FIPS-203 reference implementation.

**Secure aggregation and differential privacy.** Bonawitz et al. [11] and DP-SGD [10] provide cryptographic and statistical privacy for updates respectively. We implement neither in this paper and state so explicitly (Section VII); the Gaussian perturbation evaluated in ablation carries no formal differential privacy guarantee.

---

## III. THREAT MODEL AND SYSTEM OVERVIEW

### A. Threat model

We consider three adversaries (fully documented in `docs/threat_model.md`):

- **Honest-but-curious aggregator.** Executes the protocol faithfully but inspects individual client updates. We provide transport confidentiality on the wire; server-side cryptographic secure aggregation is out of scope.
- **Byzantine clients.** Up to *f* < *K*/2 clients manipulate local training by flipping ground-truth labels and submitting scaled, sign-flipped updates Δw<sub>mal</sub> = −λ·Δw (with λ = 5). Participating edge nodes are assumed authenticated out of band; post-quantum digital signatures (e.g., ML-DSA) are out of scope.
- **Passive network adversary with future quantum capability.** Intercepts and records all communications to execute Shor's algorithm on a future quantum computer. Key establishment therefore uses ML-KEM-768; each round's AES-GCM associated data binds the round index and client identifier, preventing cross-round replay.

### B. Nine-layer architecture

Layer 0 preprocesses telemetry (train-fitted scaling); Layer 1 shards data into edge clients; Layer 2 executes federated detection with post-quantum transport; Layers 3–4 aggregate context and gate mitigation actions; Layer 5 synthesises operational constraints; Layer 6 selects incident responses via QUBO/ILP optimisation; Layer 7 scores response utility; Layer 8 executes mitigations; Layer 9 feeds outcomes back. This paper evaluates Layers 0–2 in depth and profiles Layer 6.

---

## IV. METHODOLOGY

### A. Feature representation and leakage control

From the 63 columns of `ML-EdgeIIoT-dataset.csv`, we retain 19 protocol-semantic numeric fields (ARP opcode and hardware size, HTTP content length and response flag, TCP connection-state flags and segment length, DNS query fields, MQTT header/flag/length/type/version fields). We exclude, by name, every host address, port, sequence/acknowledgement number, checksum, stream index, inter-arrival time, frame timestamp, ICMP sequence/timestamp, Modbus transaction id, and every raw content field (TCP payload, HTTP file data and URI query, DNS query name, MQTT topic and message). Four constant columns across the entire corpus are also dropped.

Rows are partitioned into train and test splits prior to preprocessing; `StandardScaler` is fitted strictly on training rows only and applied downstream. We report two hold-outs: a stratified random 80/20 split, and a *temporal* split where the final 20 % of rows in chronological `frame.time` order constitute the test set. Because the corpus is 84.6 % attack, accuracy alone is deceptive; we report macro-F1, ROC-AUC, PR-AUC, MCC and confusion matrices. Any trial with ROC-AUC below 0.55 triggers a constant-class tripwire in our test harness.

### B. Local model

We benchmark both a lightweight Multi-Layer Perceptron (MLP) with 3,426 trainable parameters and a 1-D dilated convolutional encoder with four-head self-attention (43,138 parameters, Table 2). The convolutional encoder uses two residual blocks (32 and 64 channels, kernel 3, dilations 1 and 2), mean pooling, and a 32-unit dense projection to a two-way softmax. Because the MLP matches the 12-fold larger attention architecture in systematic ablation (Section VI-C), we recommend the compact MLP as the preferred model for resource-constrained edge devices.

### C. Federated optimisation

K = 20 clients receive Dirichlet(α = 0.5) label-skewed partitions [19]; C = 0.5 participate per round for 30 rounds with local batch size 64. We evaluate two primary optimisation regimes:
1. `FedAvg (Adam)`: Adam optimiser with learning rate 0.003, 2 local epochs, and Batch Normalisation (`norm="batch"`).
2. `FedAvg (SGD)`, `FedProx (SGD)` (proximal parameter μ = 0.01), and `SCAFFOLD (SGD)`: plain SGD with learning rate 0.05, fixed K = 20 local steps, and Group Normalisation (8 groups, `norm="group"`).

The switch from Adam/BatchNorm to SGD/GroupNorm for SCAFFOLD is theoretically mandatory: SCAFFOLD control variates estimate client gradient drift, which requires SGD under a uniform local step count, and Batch Normalisation running statistics suffer severe client drift collapse under non-IID SGD.

### D. Update compression

Each client computes Δw = w<sub>local</sub> − w<sub>global</sub> and applies top-*k* magnitude sparsification with *k* = 30 % per tensor alongside client-side error feedback (residual accumulation) [27]. Transmitted payloads are measured by exact byte serialization of `torch.save` on the sparse structure (float32 values, int32 indices, tensor shapes and metadata) rather than theoretical non-zero counts.

### E. Quantum-resistant transport

In each round, the server issues an ephemeral NIST FIPS-203 ML-KEM-768 encapsulation key. Each participating client encapsulates a 32-byte shared secret, derives an AEAD key via HKDF-SHA256, and encrypts its serialized update payload using AES-256-GCM under a fresh 96-bit nonce. Associated data binds the round number and client identifier. We benchmark `kyber-py` 1.2.0, a pure-Python FIPS-203 implementation; because it is not hardware-accelerated, the measured latencies represent a conservative upper bound.

### F. Byzantine-robust aggregation

To counteract poisoning, the server implements norm-bounded cosine trust scoring. The server establishes an adaptive reference vector from the coordinate-wise median of received updates, bounds incoming update norms by the median client norm (preventing scaling attacks without requiring clean server validation data [14]), and weights updates by positive cosine alignment. We evaluate this mechanism against undefended FedAvg, coordinate-wise median, trimmed mean (β = 0.2), and Multi-Krum [12], [13] under simultaneous label flipping and scaled sign-flip model replacement (λ = 5) across malicious client fractions.

### G. Response selection as a QUBO (Layer 6)

Given assets *i* with risk score *s<sub>i</sub>* and candidate actions *a* with effectiveness β<sub>a</sub> and execution cost c<sub>ia</sub>, binary decision variables x<sub>ia</sub> minimise Σ<sub>ia</sub>(−β<sub>a</sub>s<sub>i</sub> + c<sub>ia</sub>)x<sub>ia</sub> subject to assignment and budget constraints. We formulate the problem as an exact Integer Linear Program (ILP) solved via CBC/PuLP, a greedy heuristic, and a Quadratic Unconstrained Binary Optimisation (QUBO) problem solved via QAOA (p = 1 layer, statevector simulator with 2048 shots, COBYLA optimiser with at most 8 iterations) on 4, 8, and 12 qubits.

---

## V. EXPERIMENTAL SETUP

All experiments executed on a dedicated system: Intel64 Family 6 Model 154 Stepping 3, GenuineIntel (12 physical cores, 15.63 GB RAM), Windows 11 (10.0.26200), Python 3.14.0, PyTorch 2.13.0+cpu, Qiskit 2.5.0, with 4 intra-op threads. Seeds 42, 101, 2024, 777, and 999 are fixed across all runs. The federated benchmark samples 15,000 rows from the full 157,800-row Edge-IIoTset ML dataset (Table 1). Per-algorithm hyperparameter configurations are recorded in Table 4. Single-sample inference latency is measured at batch size 1 after 200 warm-up calls across 2000 timed evaluations. Energy is estimated as round duration × an assumed 35.0 W TDP. All results are written to `results/RESULTS.json` and verified by `check_paper_numbers.py`.

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

---

## VI. RESULTS

### A. Data leakage analysis (Headline finding)

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

Table 10 presents the primary empirical finding of this paper. On Edge-IIoTset, detection performance is heavily driven by data leakage through session identifiers. When 17 session-identifying fields (TCP/UDP port numbers, TCP sequence and acknowledgement numbers) are included alongside the 19 protocol-semantic features, a centralized classifier achieves ROC-AUC 0.9942 (random split) and 0.9971 (temporal split). Removing these identifiers reduces centralized detection performance to ROC-AUC 0.8822 and 0.8766 respectively.

Random Forest feature importance analysis on the 36-feature set reveals that the top three predictive features are all session identifiers:
1. `tcp.dstport` (importance 0.2656),
2. `tcp.srcport` (importance 0.2067),
3. `tcp.seq` (importance 0.1495).

Crucially, our experiments demonstrate that while session identifiers artificially inflate centralized scores on random splits, they actively degrade federated learning across non-IID edge clients: federated FedAvg on the random split achieves ROC-AUC 0.8164 on semantic features, but drops to 0.7396 when session identifiers are included. This occurs because port assignments and sequence streams are unique to individual client sessions and do not transfer across decentralized partitions, inducing extreme client drift. We conclude that published Edge-IIoTset results reporting near-perfect (>99 %) accuracy reflect session-identifier memorisation rather than robust intrusion detection.

### B. Federated detection performance

**Table 4.** Federated detection performance on Edge-IIoTset — *provenance: measured; K = 20 clients, C = 0.5, Dirichlet α = 0.5, 30 rounds, 1 local epochs, batch 64, lr 0.05, 15,000 samples, 19 features, 5 seeds*

| Split | Algorithm | Accuracy | Macro-F1 | ROC-AUC | ROC-AUC 95% CI | Payload / client / round (KB) | Median round time (s) |
|---|---|---:|---:|---:|---:|---:|---:|
| random | FedAvg (Adam) | 0.8807 ± 0.0093 | 0.6697 ± 0.0535 | 0.8738 ± 0.0145 | [0.8558, 0.8918] | 117.66 | 7.24 |
| random | FedAvg (SGD) | 0.8694 ± 0.0038 | 0.6105 ± 0.0185 | 0.7932 ± 0.0114 | [0.7791, 0.8073] | 117.66 | 4.92 |
| random | FedProx (SGD) | 0.8693 ± 0.0037 | 0.6104 ± 0.0183 | 0.7931 ± 0.0113 | [0.7791, 0.8071] | 117.66 | 6.30 |
| random | SCAFFOLD (SGD) | 0.8711 ± 0.0038 | 0.6176 ± 0.0185 | 0.8093 ± 0.0338 | [0.7673, 0.8513] | 295.23 | 3.84 |
| random | *Centralized bound (10 epochs)* | 0.8909 ± 0.0035 | 0.7409 ± 0.0029 | 0.8822 ± 0.0042 | [0.8770, 0.8874] | — | — |
| random | SCAFFOLD (SGD) − FedAvg (SGD) (accuracy) | mean diff 0.0017 | paired t p = 0.2588 | Wilcoxon p = 0.0625 | | | |
| random | SCAFFOLD (SGD) − FedAvg (SGD) (ROC-AUC) | mean diff 0.0161 | paired t p = 0.2784 | Wilcoxon p = 0.8125 | | | |
| random | SCAFFOLD (SGD) − FedAvg (Adam) (accuracy) | mean diff -0.0095 | paired t p = 0.0433 | Wilcoxon p = 0.0625 | | | |
| random | SCAFFOLD (SGD) − FedAvg (Adam) (ROC-AUC) | mean diff -0.0644 | paired t p = 0.0155 | Wilcoxon p = 0.0625 | | | |
| temporal | FedAvg (Adam) | 0.8861 ± 0.0009 | 0.6611 ± 0.0188 | 0.8718 ± 0.0041 | [0.8667, 0.8770] | 117.66 | 4.14 |
| temporal | FedAvg (SGD) | 0.7771 ± 0.1412 | 0.5960 ± 0.0442 | 0.7951 ± 0.0175 | [0.7733, 0.8169] | 117.66 | 3.82 |
| temporal | FedProx (SGD) | 0.7769 ± 0.1415 | 0.5959 ± 0.0443 | 0.7950 ± 0.0177 | [0.7731, 0.8169] | 117.66 | 7.12 |
| temporal | SCAFFOLD (SGD) | 0.8808 ± 0.0044 | 0.6288 ± 0.0219 | 0.7552 ± 0.0791 | [0.6571, 0.8534] | 295.23 | 5.63 |
| temporal | *Centralized bound (10 epochs)* | 0.8957 ± 0.0034 | 0.7342 ± 0.0205 | 0.8766 ± 0.0003 | [0.8763, 0.8769] | — | — |
| temporal | SCAFFOLD (SGD) − FedAvg (SGD) (accuracy) | mean diff 0.1037 | paired t p = 0.1692 | Wilcoxon p = 0.1875 | | | |
| temporal | SCAFFOLD (SGD) − FedAvg (SGD) (ROC-AUC) | mean diff -0.0399 | paired t p = 0.2688 | Wilcoxon p = 0.3125 | | | |
| temporal | SCAFFOLD (SGD) − FedAvg (Adam) (accuracy) | mean diff -0.0053 | paired t p = 0.0728 | Wilcoxon p = 0.2500 | | | |
| temporal | SCAFFOLD (SGD) − FedAvg (Adam) (ROC-AUC) | mean diff -0.1166 | paired t p = 0.0296 | Wilcoxon p = 0.0625 | | | |

Top-k (30 %) update payload: FedAvg / FedProx = 117.66 KB (30.17 % reduction vs 168.51 KB raw float32 parameters). SCAFFOLD transmits sparse Δw + dense control variates Δc = 295.23 KB total uplink per round.
Test-set attack share: random 0.8427, temporal 0.8523. Per-seed values and per-round learning curves are stored under `fl_benchmarks.splits.<split>.algorithms.<algo>.seed_trials` in RESULTS.json.

Table 4 evaluates federated detection under strict leakage controls. On protocol-semantic features, the centralized detection ceiling is ROC-AUC 0.8822 (random) and 0.8766 (temporal). Federated learning approaches this honest ceiling: `FedAvg (Adam)` achieves ROC-AUC 0.8738 ± 0.0145 on the random split and 0.8718 ± 0.0041 on the temporal split. We recommend `FedAvg (Adam)` as the standard practical deployment baseline.

In contrast, our experiments reveal that SCAFFOLD drift correction provides no meaningful advantage:
- Under identical SGD and GroupNorm settings, `SCAFFOLD (SGD)` achieves ROC-AUC 0.8093 ± 0.0338 compared to 0.7932 ± 0.0114 for `FedAvg (SGD)`. The mean difference of +0.0161 is not statistically significant (paired t p = 0.2784, Wilcoxon p = 0.8125).
- Compared to `FedAvg (Adam)`, `SCAFFOLD (SGD)` is significantly worse (mean difference -0.0644, paired t p = 0.0155).
- On the temporal split, SCAFFOLD is unstable across random seeds, exhibiting a wide standard deviation of 0.0791 (ROC-AUC 0.7552).
- Communication cost: SCAFFOLD requires uploading dense control-variate deltas Δc every round, consuming 295.23 KB per client per round, compared to 117.66 KB for FedAvg and FedProx.

### C. Component ablation and model complexity

**Table 2.** Model complexity (input dim = 19) — *provenance: measured (parameter count and FLOPs profiled in code)*

| Model | Trainable parameters | Size (KB, float32) | GFLOPs / sample |
|---|---:|---:|---:|
| MLP | 3,426 | 13.38 | 0.000007 |
| CNN 1D | 8,674 | 33.88 | 0.000244 |
| TCN NoAttention | 26,498 | 103.51 | 0.001064 |
| TCN Attention | 43,138 | 168.51 | 0.001687 |

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

Table 2 profiles model complexity, and Table 5 details systematic component ablation across eight development stages:
- **Architecture comparison**: A compact MLP (Stage 1, 3,426 parameters) attains ROC-AUC 0.8750 ± 0.0095, matching the 12-fold larger TCN + Attention encoder (Stage 4, 43,138 parameters, ROC-AUC 0.8837 ± 0.0034). Because complex temporal and attention mechanisms provide no measurable benefit on tabular protocol features, the lightweight MLP is the optimal choice for edge deployment.
- **De-confounding SCAFFOLD**: Stage 6 (Top-*k* compression with Adam/BatchNorm) achieves ROC-AUC 0.8726. Introducing Stage 6b (`FedAvg (SGD, GroupNorm, K=20 steps)`) isolates the optimizer switch, dropping ROC-AUC to 0.7378. Adding SCAFFOLD control variates while holding optimizer and normalization constant (Stage 6b → Stage 7) yields only a marginal gain of +0.0052 ROC-AUC (reaching 0.7430 ± 0.0648), confirming that SCAFFOLD does not compensate for the loss of adaptive optimization.

### D. Robustness to Byzantine clients

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

Table 6 evaluates defenses against label-flipping and scaled sign-flipping model replacement:
- Under 20.0 % compromised clients, coordinate-wise median is the most effective defense, maintaining ROC-AUC 0.8307, followed by trimmed mean (0.8156) and Multi-Krum (0.6591).
- Norm-bounded cosine trust scoring improves resilience over undefended FedAvg (0.5162) to 0.7118, but does not outperform coordinate-wise median.
- Under 50.0 % compromised clients, all defenses degrade significantly (ROC-AUC 0.6033 for median and 0.5609 for cosine trust).

### E. Cross-dataset transfer (Negative result)

**Table 7.** Cross-dataset transfer Edge-IIoTset → WUSTL-IIoT-2021 — *provenance: measured; 3 semantically shared features (tcp.len, http.content_length, tcp.connection.synack); 50,000 of 1,194,464 target flows; source model centrally trained on the shared-feature subset (not the FL checkpoint)*

| Setting | Accuracy | Macro-F1 | ROC-AUC | PR-AUC |
|---|---:|---:|---:|---:|
| Zero-shot (source scaler, no target labels) | 0.0717 ± 0.0000 | 0.0669 ± 0.0000 | 0.2595 ± 0.1345 | 0.1620 ± 0.0907 |
| Fine-tuned on 20 % of target | 0.7781 ± 0.3955 | 0.6010 ± 0.3552 | 0.8894 ± 0.2177 | 0.6606 ± 0.3302 |
| From scratch on the same 20 % of target | 0.9378 ± 0.0213 | 0.5695 ± 0.1969 | 0.9854 ± 0.0031 | 0.7668 ± 0.0686 |

Edge-IIoTset is packet-level; WUSTL-IIoT-2021 is flow-level. Only 3 semantically shared features exist; zero-shot transfer is reported as a negative result.

Zero-shot transfer from Edge-IIoTset to WUSTL-IIoT-2021 fails completely, yielding ROC-AUC 0.2595 on 50,000 target flows (Table 7). The fundamental obstacle is feature representation mismatch: Edge-IIoTset records per-packet Wireshark fields, whereas WUSTL-IIoT-2021 records Argus bidirectional flow statistics, leaving only 3 semantically overlapping features. Fine-tuning on 20 % of the target achieves ROC-AUC 0.8894 ± 0.2177, which underperforms training from scratch on the same 20 % partition (ROC-AUC 0.9854 ± 0.0031). We caution researchers against assuming transferability between packet-level and flow-level IIoT datasets.

### F. Post-quantum transport and edge resource profile

**Table 3.** ML-KEM-768 + AES-256-GCM overhead — *provenance: measured; 1,000 iterations after 50 warm-up; kyber-py pure-Python FIPS-203 reference implementation (upper bound on latency)*

| Operation | Median (ms) | P95 (ms) | Std (ms) | Bytes |
|---|---:|---:|---:|---:|
| ML-KEM-768 KeyGen | 3.2078 | 4.6541 | 0.6490 | pk 1184 / sk 2400 |
| ML-KEM-768 Encaps | 4.2132 | 6.1116 | 0.8393 | ct 1088 |
| ML-KEM-768 Decaps | 5.7636 | 8.4183 | 1.1600 | ss 32 |
| AES-256-GCM encrypt | 0.0648 | 0.1033 | 0.0235 | payload 25,000 |
| AES-256-GCM decrypt | 0.0237 | 0.0334 | 0.0056 | nonce 12 + tag 16 |
| **KEM total (keygen+encaps+decaps)** | **13.1846** | — | — | ciphertext overhead per round 1,116 |

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

Tables 3 and 8 profile system overhead:
- **Post-quantum cryptography**: NIST FIPS-203 ML-KEM-768 key encapsulation requires 13.18 ms total median latency per client per round (keygen + encaps + decaps) in a pure-Python reference implementation, introducing 1,116 bytes of ciphertext overhead. AES-256-GCM encryption of a test payload adds 0.0648 ms.
- **Communication payload**: Top-*k* sparsification (k = 30 %) reduces uplink payload to 117.66 KB per client per round for FedAvg and FedProx. Including PQC ciphertext, nonce, and authentication tag adds 1,116 bytes, for a total wire payload of 118.75 KB.
- **Edge inference**: Single-sample inference latency is 0.9275 ms median on a commodity CPU, supporting a throughput of 1078.11 samples/s.

### G. Decision layer profile

**Table 9.** QUBO response-selection: QAOA (statevector simulator) vs exact ILP vs greedy — *provenance: measured; 4 actions per asset; objective = negative utility (lower is better)*

| N assets | Qubits | Trials | ILP latency (ms) | QAOA latency (ms) | QAOA gap vs ILP (%) |
|---:|---:|---:|---:|---:|---:|
| 1 | 4 | 3 | 342.18 | 377.34 | 0.00 |
| 2 | 8 | 3 | 46.23 | 869.84 | 29.96 |
| 3 | 12 | 3 | 48.97 | 1853.59 | 13.26 |

Table 9 profiles candidate mitigation selection:
- Classical integer linear programming (ILP via CBC) solves the allocation problem exactly in 342.18 ms for 1 asset (4 qubits), 46.23 ms for 2 assets (8 qubits), and 48.97 ms for 3 assets (12 qubits).
- QAOA on a statevector simulator incurs an optimality gap of 29.96 % on 8 qubits and 13.26 % on 12 qubits, while requiring 1853.59 ms.
- We conclude that current variational quantum optimization provides no computational advantage over classical ILP for edge cyber-incident mitigation.

---

## VII. LIMITATIONS

- **No formal privacy guarantee.** Gaussian update perturbation does not satisfy DP-SGD; no (ε, δ) differential privacy bound is provided. Cryptographic secure aggregation is not implemented; the server decrypts individual client updates.
- **No post-quantum authentication.** ML-KEM provides confidentiality; client authentication is assumed out of band.
- **Reference-implementation cryptography.** `kyber-py` is a pure-Python reference implementation; compiled libraries (e.g., liboqs) will yield significantly lower latencies.
- **Simulation constraints.** SCAFFOLD hyperparameter tuning was conducted on a single seed (`results/logs/scaffold_grid.log`). All client models were executed sequentially on a single CPU; device dropout and communication stragglers were not modelled.
- **Heuristic trust.** Norm-bounded cosine trust scoring is a heuristic; under strong adaptive adversaries, coordinate-wise median remains empirically superior.
- **Decision layer.** QAOA is evaluated only on small simulator-feasible instances (≤ 12 qubits); no quantum speedup exists at this scale.

---

## VIII. CONCLUSION

We presented an empirical study of federated intrusion detection on Edge-IIoTset under rigorous leakage controls, measured communication compression, and post-quantum transport. Our findings demonstrate that published detection accuracies exceeding 99 % on Edge-IIoTset stem from session-identifier leakage rather than robust intrusion detection. On protocol-semantic features, the true centralized detection ceiling is ROC-AUC 0.8822, which federated `FedAvg (Adam)` approaches with ROC-AUC 0.8738. We report four negative results: SCAFFOLD drift correction provides no significant benefit under identical SGD settings while more than doubling uplink bandwidth; a compact 3.4k-parameter MLP matches complex convolutional attention encoders; cross-dataset transfer between packet and flow representations fails zero-shot; and QAOA provides no advantage over classical ILP. Post-quantum transport under ML-KEM-768 is computationally viable on commodity hardware.

---

## REFERENCES

[1] M. A. Ferrag, O. Friha, D. Hamouda, L. Maglaras, and H. Janicke, "Edge-IIoTset: A new comprehensive realistic cyber security dataset of IoT and IIoT applications for centralized and federated learning," *IEEE Access*, vol. 10, pp. 40281–40306, 2022, doi: 10.1109/ACCESS.2022.3165809.

[2] M. Zolanvari, M. A. Teixeira, L. Gupta, K. M. Khan, and R. Jain, "Machine learning-based network vulnerability analysis of Industrial Internet of Things," *IEEE Internet Things J.*, vol. 6, no. 4, pp. 6822–6834, 2019.

[3] M. Zolanvari, L. Gupta, K. M. Khan, and R. Jain, "WUSTL-IIOT-2021 dataset for IIoT cybersecurity research," Washington Univ. in St. Louis, 2021. [Online]. Available: https://www.cs.wustl.edu/~jain/iiot2/index.html

[4] H. B. McMahan, E. Moore, D. Ramage, S. Hampson, and B. Agüera y Arcas, "Communication-efficient learning of deep networks from decentralized data," in *Proc. AISTATS*, 2017.

[5] T. Li, A. K. Sahu, M. Zaheer, M. Sanjabi, A. Talwalkar, and V. Smith, "Federated optimization in heterogeneous networks," in *Proc. MLSys*, 2020.

[6] S. P. Karimireddy, S. Kale, M. Mohri, S. J. Reddi, S. U. Stich, and A. T. Suresh, "SCAFFOLD: Stochastic controlled averaging for federated learning," in *Proc. ICML*, 2020.

[7] National Institute of Standards and Technology, "Module-Lattice-Based Key-Encapsulation Mechanism Standard," FIPS 203, Aug. 2024.

[8] M. Dworkin, "Recommendation for block cipher modes of operation: Galois/Counter Mode (GCM) and GMAC," NIST SP 800-38D, 2007.

[9] H. Krawczyk and P. Eronen, "HMAC-based Extract-and-Expand Key Derivation Function (HKDF)," RFC 5869, 2010.

[10] M. Abadi et al., "Deep learning with differential privacy," in *Proc. ACM CCS*, 2016.

[11] K. Bonawitz et al., "Practical secure aggregation for privacy-preserving machine learning," in *Proc. ACM CCS*, 2017.

[12] P. Blanchard, E. M. El Mhamdi, R. Guerraoui, and J. Stainer, "Machine learning with adversaries: Byzantine tolerant gradient descent," in *Proc. NeurIPS*, 2017.

[13] D. Yin, Y. Chen, K. Ramchandran, and P. Bartlett, "Byzantine-robust distributed learning: Towards optimal statistical rates," in *Proc. ICML*, 2018.

[14] X. Cao, M. Fang, J. Liu, and N. Z. Gong, "FLTrust: Byzantine-robust federated learning via trust bootstrapping," in *Proc. NDSS*, 2021.

[15] S. Bai, J. Z. Kolter, and V. Koltun, "An empirical evaluation of generic convolutional and recurrent networks for sequence modeling," arXiv:1803.01271, 2018.

[16] A. Vaswani et al., "Attention is all you need," in *Proc. NeurIPS*, 2017.

[17] E. Farhi, J. Goldstone, and S. Gutmann, "A quantum approximate optimization algorithm," arXiv:1411.4028, 2014.

[18] Y. Lin, S. Han, H. Mao, Y. Wang, and W. J. Dally, "Deep gradient compression: Reducing the communication bandwidth for distributed training," in *Proc. ICLR*, 2018.

[19] T.-M. H. Hsu, H. Qi, and M. Brown, "Measuring the effects of non-identical data distribution for federated visual classification," arXiv:1909.06335, 2019.

[20] P. Kairouz et al., "Advances and open problems in federated learning," *Found. Trends Mach. Learn.*, vol. 14, no. 1–2, 2021.

[21] M. Mosca, "Cybersecurity in an era with quantum computers: Will we be ready?" *IEEE Security & Privacy*, vol. 16, no. 5, pp. 38–41, 2018.

[22] D. Arp et al., "Dos and don'ts of machine learning in computer security," in *Proc. USENIX Security*, 2022.

[23] D. Chicco and G. Jurman, "The advantages of the Matthews correlation coefficient (MCC) over F1 score and accuracy in binary classification evaluation," *BMC Genomics*, vol. 21, no. 6, 2020.

[24] T. D. Nguyen, S. Marchal, M. Miettinen, H. Fereidooni, N. Asokan, and A.-R. Sadeghi, "DÏoT: A federated self-learning anomaly detection system for IoT," in *Proc. IEEE ICDCS*, 2019.

[25] S. I. Popoola, R. Ande, B. Adebisi, G. Gui, M. Hammoudeh, and O. Jogunola, "Federated deep learning for zero-day botnet attack detection in IoT-edge devices," *IEEE Internet Things J.*, vol. 9, no. 5, pp. 3930–3944, 2022.

[26] S. A. Rahman, H. Tout, C. Talhi, and A. Mourad, "Internet of Things intrusion detection: Centralized, on-device, or federated learning?" *IEEE Network*, vol. 34, no. 6, pp. 310–317, 2020.

[27] S. U. Stich, J.-B. Cordonnier, and M. Jaggi, "Sparsified SGD with memory," in *Proc. NeurIPS*, 2018.

[28] A. Lucas, "Ising formulations of many NP problems," *Frontiers in Physics*, vol. 2, 2014.

[29] J. Bos et al., "CRYSTALS – Kyber: A CCA-secure module-lattice-based KEM," in *Proc. IEEE EuroS&P*, 2018.

[30] D. P. Kingma and J. Ba, "Adam: A method for stochastic optimization," in *Proc. ICLR*, 2015.

[31] S. Ioffe and C. Szegedy, "Batch normalization: Accelerating deep network training by reducing internal covariate shift," in *Proc. ICML*, 2015.

[32] A. Javadi-Abhari et al., "Quantum computing with Qiskit," arXiv:2405.08810, 2024.
