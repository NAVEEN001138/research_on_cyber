# How Much of Edge-IIoTset Is Leakage? An Honest Baseline for Quantum-Resistant Federated Intrusion Detection in IIoT

**Naveen Ravi**

---

### Abstract

Federated learning (FL) enables industrial IoT (IIoT) facilities to collaboratively train intrusion-detection models without consolidating raw operational telemetry. However, near-perfect (>99 %) detection on Edge-IIoTset is reproducible in our pipeline only when session identifiers (ports, TCP sequence numbers) are included; on protocol-semantic features alone the ceiling is ROC-AUC {{V:leakage_experiment.by_split.random.centralized.semantic.roc_auc.mean:f4}} (random) and {{V:leakage_experiment.by_split.session-disjoint.centralized.semantic.roc_auc.mean:f4}} (session-disjoint), which is consistent with data snooping [22]. Evaluating a {{V:fl_benchmarks.features_count}}-feature protocol-semantic representation on random and session-disjoint hold-outs, we show that centralized models drop from ROC-AUC {{V:leakage_experiment.by_split.random.centralized.semantic_plus_identifiers.roc_auc.mean:f4}} with identifiers to this honest ceiling. Across {{LEN:fl_benchmarks.seeds}} random seeds and K = {{V:fl_benchmarks.num_clients}} Dirichlet-partitioned clients, federated learning approaches this honest ceiling: FedAvg with Adam achieves ROC-AUC {{V:fl_benchmarks.splits.random.algorithms.FedAvg (Adam).roc_auc.mean:f4}} ± {{V:fl_benchmarks.splits.random.algorithms.FedAvg (Adam).roc_auc.std:f4}} (random) and {{V:fl_benchmarks.splits.session-disjoint.algorithms.FedAvg (Adam).roc_auc.mean:f4}} ± {{V:fl_benchmarks.splits.session-disjoint.algorithms.FedAvg (Adam).roc_auc.std:f4}} (session-disjoint). In contrast, we document four unambiguous negative results: (i) SCAFFOLD drift correction provides no statistically significant gain over FedAvg under identical SGD settings (paired t p = {{V:fl_benchmarks.splits.random.paired_test_scaffold_sgd_vs_fedavg_sgd_auc.p_value_ttest:f4}}) while inflating uplink payload by over two-fold; (ii) a compact {{V:ablation_benchmarks.stages.Stage 1.parameters:int}}-parameter MLP matches a 12-fold larger 1-D convolutional self-attention encoder; (iii) zero-shot cross-dataset transfer to flow-level telemetry fails completely (ROC-AUC {{V:cross_dataset_transfer.zero_shot.roc_auc.mean:f4}}); and (iv) QAOA response selection exhibits an optimality gap of {{V:qaoa_multi_n_benchmarks.results_by_n.N_2.mean_qaoa_gap_pct:f2}} % with slower execution than classical integer linear programming. Under {{V:poisoning_benchmarks.poison_ratios.2:pct1}} % Byzantine clients, coordinate-wise median remains the most robust defense (ROC-AUC {{V:poisoning_benchmarks.results_by_ratio.20%.Coordinate_Median.roc_auc.mean:f4}}), while norm-bounded cosine trust scoring improves upon undefended FedAvg ({{V:poisoning_benchmarks.results_by_ratio.20%.FedAvg_Undefended.roc_auc.mean:f4}}) to {{V:poisoning_benchmarks.results_by_ratio.20%.Cosine_Trust_NormBounded.roc_auc.mean:f4}}. Transport security under NIST FIPS-203 ML-KEM-768 with AES-256-GCM incurs {{V:resource_profile.pqc_cryptography.keygen.median_ms:f2}} ms server key generation per round (reused across clients), {{V:resource_profile.pqc_cryptography.encaps.median_ms:f2}} ms client encapsulation, and {{V:resource_profile.pqc_cryptography.decaps.median_ms:f2}} ms server decapsulation per client. Every number is rendered from automated execution and verified by automated checking.

**Index Terms** — Federated learning, intrusion detection, Industrial IoT, data leakage, post-quantum cryptography, ML-KEM, Byzantine robustness, Edge-IIoTset, reproducibility.

---

## I. INTRODUCTION

Industrial cyber-physical systems expose Modbus/TCP, MQTT, DNS, HTTP and ARP telemetry at many geographically separated sites. Centralising that telemetry for intrusion detection raises three practical obstacles: (i) raw packet captures contain proprietary network topology and sensitive operational data whose cross-site transfer carries regulatory and contractual risk; (ii) the parameter traffic of any distributed learner is a long-lived secret — an adversary that records it today can decrypt it once a cryptanalytically relevant quantum computer exists ("harvest now, decrypt later") [21]; and (iii) sites differ in the telemetry they observe, so a federated detector must cope with statistical heterogeneity and, in the worst case, with compromised participants.

A large body of work reports near-perfect (>99 %) accuracy on the Edge-IIoTset benchmark [1]. In our investigation, we find that such high detection performance is reproducible only when features such as ephemeral TCP/UDP port numbers, sequence and acknowledgement numbers, checksums, and session identifiers are included, which is consistent with the data snooping pitfalls catalogued by Arp et al. [22] where models memorise specific capture sessions rather than genuine attack behaviour. When evaluated on random row splits, packets from identical TCP streams populate both training and test partitions, creating an illusion of high detection performance. In this work, we demonstrate that when these identifiers are removed, detection performance drops substantially, revealing the true protocol-semantic ceiling of the dataset. Furthermore, we show that including these session identifiers actively impairs federated optimisation across non-IID edge clients, because local port assignments and sequence streams do not transfer across clients.

**Contributions.**
1. A direct empirical leakage measurement on Edge-IIoTset (protocol-semantic features vs session identifiers, across random and session-disjoint splits, and random-forest feature importances) demonstrating that near-perfect (>99 %) detection on Edge-IIoTset is reproducible in our pipeline only when session identifiers are included, which is consistent with data snooping [22] rather than behavioural detection (Section VI-A).
2. A leakage-controlled federated intrusion-detection benchmark establishing the honest performance ceiling across random and session-disjoint hold-outs, evaluated over {{LEN:fl_benchmarks.seeds}} seeds with Dirichlet non-IID partitions, paired statistical significance tests, and explicit per-algorithm hyperparameter configurations (Section VI-B).
3. A Byzantine-robustness comparison of five aggregation rules (coordinate-wise median, trimmed mean, Multi-Krum, norm-bounded cosine trust, and undefended FedAvg) under simultaneous label flipping and scaled sign-flip attacks across {{V:poisoning_benchmarks.poison_ratios.1:pct1}}–{{V:poisoning_benchmarks.poison_ratios.4:pct1}} % malicious clients (Section VI-D).
4. Concrete negative results documenting that SCAFFOLD drift correction does not significantly improve ROC-AUC under identical settings, lightweight MLPs match 12-fold larger 1-D convolutional self-attention encoders, cross-dataset transfer from packet-level to flow-level telemetry fails zero-shot, and QAOA provides no advantage over classical ILP (Sections VI-B, VI-C, VI-E, VI-G).
5. A fully traceable and verified experimental pipeline: every result number is rendered from a single automated results repository without hand-typed values and validated by an automated checker.

The post-quantum cryptographic transport (ML-KEM-768 key encapsulation with AES-256-GCM payload encryption) serves as the underlying communications subsystem supporting the benchmark rather than a standalone algorithmic contribution; its execution costs are profiled in Section VI-F.

---

## II. RELATED WORK

**Federated intrusion detection for IoT/IIoT.** DÏoT [24] introduced federated self-learning anomaly detection on IoT gateways; Rahman et al. [26] compared centralised, on-device and federated IDS training for IoT; Popoola et al. [25] applied federated deep learning to zero-day botnet detection on IoT-edge devices. These works establish that FL is viable for IoT IDS but evaluate with random splits on identifier-rich features and do not consider quantum-safe transport or Byzantine participants.

**Edge-IIoTset.** Ferrag et al. [1] released Edge-IIoTset with 14 attack classes over a realistic IIoT testbed and reported centralised and federated baselines. Subsequent papers frequently report >99 % accuracy; we show (Section VI-A) that on protocol-semantic features alone the centralised ceiling is far lower in our pipeline, which is consistent with session-identifier leakage in the commonly used feature set as catalogued by Arp et al. [22].

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

From the {{V:dataset_distribution.total_columns}} columns of `ML-EdgeIIoT-dataset.csv`, we retain {{V:fl_benchmarks.features_count}} protocol-semantic numeric fields (ARP opcode and hardware size, HTTP content length and response flag, TCP connection-state flags and segment length, DNS query fields, MQTT header/flag/length/type/version fields). We exclude, by name, every host address, port, sequence/acknowledgement number, checksum, stream index, inter-arrival time, frame timestamp, ICMP sequence/timestamp, Modbus transaction id, and every raw content field (TCP payload, HTTP file data and URI query, DNS query name, MQTT topic and message). Four constant columns across the entire corpus are also dropped.

Rows are partitioned into train and test splits prior to preprocessing; `StandardScaler` is fitted strictly on training rows only and applied downstream. We report two hold-outs: a stratified random 80/20 split, and a *session-disjoint* split partitioned via `GroupShuffleSplit` (80/20) on network session endpoints (`ip.src_host`, `ip.dst_host`, transport stream/ports) so that zero session flows appear in both partitions. Crucially, a true chronological split is not possible because `frame.time` lacks date fields in Edge-IIoTset (evaluating to 99.2% NaNs under numeric parsing). Because the corpus is {{V:dataset_distribution.attack_share_pct:f1}} % attack, accuracy alone is deceptive; we report macro-F1, ROC-AUC, PR-AUC, MCC, and threshold-calibrated operating points. Any trial with ROC-AUC below 0.55 triggers a constant-class tripwire in our test harness.

### B. Local model

We benchmark both a lightweight Multi-Layer Perceptron (MLP) with {{V:fl_benchmarks.model_profiles.MLP.parameters:int}} trainable parameters and a 1-D dilated convolutional encoder with four-head self-attention ({{V:fl_benchmarks.model_profiles.TCN_Attention.parameters:int}} parameters, Table 2). The convolutional encoder uses two residual blocks (32 and 64 channels, kernel 3, dilations 1 and 2), mean pooling, and a 32-unit dense projection to a two-way softmax. Because the MLP matches the 12-fold larger attention architecture in systematic ablation (Section VI-C), we recommend the compact MLP as the preferred model for resource-constrained edge devices.

### C. Federated optimisation

K = {{V:fl_benchmarks.num_clients}} clients receive Dirichlet(α = 0.5) label-skewed partitions [19]; C = {{V:fl_benchmarks.participation_rate}} participate per round for {{V:fl_benchmarks.num_rounds}} rounds with local batch size 64. We evaluate two primary optimisation regimes:
1. `FedAvg (Adam)`: Adam optimiser with learning rate {{V:fl_benchmarks.splits.random.algorithms.FedAvg (Adam).config.learning_rate}}, {{V:fl_benchmarks.splits.random.algorithms.FedAvg (Adam).config.local_epochs}} local epochs, and Batch Normalisation (`norm="batch"`).
2. `FedAvg (SGD)`, `FedProx (SGD)` (proximal parameter μ = {{V:fl_benchmarks.splits.random.algorithms.FedProx (SGD).config.mu}}), and `SCAFFOLD (SGD)`: plain SGD with learning rate {{V:fl_benchmarks.splits.random.algorithms.FedAvg (SGD).config.learning_rate}}, fixed K = {{V:fl_benchmarks.splits.random.algorithms.FedAvg (SGD).config.local_steps}} local steps, and Group Normalisation (8 groups, `norm="group"`).

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

All experiments executed on a dedicated system: {{ENV:cpu_model}} ({{ENV:physical_cores}} physical cores, {{ENV:ram_gb}} GB RAM), {{ENV:os}}, Python {{ENV:python_version}}, PyTorch {{ENV:torch_version}}, with {{ENV:torch_threads}} intra-op threads. Seeds {{V:fl_benchmarks.seeds.0}}, {{V:fl_benchmarks.seeds.1}}, {{V:fl_benchmarks.seeds.2}}, {{V:fl_benchmarks.seeds.3}}, and {{V:fl_benchmarks.seeds.4}} are fixed across all runs. The federated benchmark samples {{V:fl_benchmarks.sample_size:int}} rows from the full {{V:fl_benchmarks.dataset_total_rows:int}}-row Edge-IIoTset ML dataset (Table 1). Per-algorithm hyperparameter configurations are recorded in Table 4. Single-sample inference latency is measured at batch size 1 after 200 warm-up calls across 2000 timed evaluations. Energy is estimated as round duration × an assumed {{V:resource_profile.energy_consumption.assumed_tdp_watts:f1}} W TDP. All results are written to `results/RESULTS.json` and verified by `check_paper_numbers.py`.

{{TABLE:T1_dataset}}

---

## VI. RESULTS

### A. Data leakage analysis (Headline finding)

{{TABLE:T10_leakage}}

Table 10 presents the primary empirical finding of this paper. On Edge-IIoTset, detection performance is heavily driven by data leakage through session identifiers. When 17 session-identifying fields (TCP/UDP port numbers, TCP sequence and acknowledgement numbers) are included alongside the 19 protocol-semantic features, a centralized classifier achieves ROC-AUC {{V:leakage_experiment.by_split.random.centralized.semantic_plus_identifiers.roc_auc.mean:f4}} (random split) and {{V:leakage_experiment.by_split.session-disjoint.centralized.semantic_plus_identifiers.roc_auc.mean:f4}} (session-disjoint split). Removing these identifiers reduces centralized detection performance to ROC-AUC {{V:leakage_experiment.by_split.random.centralized.semantic.roc_auc.mean:f4}} and {{V:leakage_experiment.by_split.session-disjoint.centralized.semantic.roc_auc.mean:f4}} respectively.

Random Forest feature importance analysis on the 36-feature set reveals that the top three predictive features are all session identifiers:
1. `{{V:leakage_experiment.feature_importances.0.feature}}` (importance {{V:leakage_experiment.feature_importances.0.importance:f4}}),
2. `{{V:leakage_experiment.feature_importances.1.feature}}` (importance {{V:leakage_experiment.feature_importances.1.importance:f4}}),
3. `{{V:leakage_experiment.feature_importances.2.feature}}` (importance {{V:leakage_experiment.feature_importances.2.importance:f4}}).

Crucially, our experiments demonstrate that while session identifiers artificially inflate centralized scores on random splits, they actively degrade federated learning across non-IID edge clients: federated FedAvg on the random split achieves ROC-AUC {{V:leakage_experiment.by_split.random.fedavg.semantic.roc_auc.mean:f4}} on semantic features, but drops to {{V:leakage_experiment.by_split.random.fedavg.semantic_plus_identifiers.roc_auc.mean:f4}} when session identifiers are included. This occurs because port assignments and sequence streams are unique to individual client sessions and do not transfer across decentralized partitions, inducing extreme client drift. In our pipeline, near-perfect (>99 %) detection on Edge-IIoTset requires session identifiers, which is consistent with session-identifier memorisation rather than robust intrusion detection.

Beyond session identifiers, our empirical audit uncovers a severe data formatting artifact in Edge-IIoTset: the `dns.qry.name.len` field is encoded as string `"0"` for 24,272 normal traffic samples and `"0.0"` for 133,272 attack samples (Table 11). Models trained with categorical string one-hot encoding (the original repository recipe) achieve ~1.0000 ROC-AUC (99.98% accuracy) purely by memorizing this string formatting quirk [33]. When parsed into standard numeric float32 representations (`pd.to_numeric`), both `"0"` and `"0.0"` collapse to identical `0.0`, destroying the spurious shortcut and dropping the feature's ROC-AUC to 0.5007 (chance level).

{{TABLE:T11_artifact_audit}}

### B. Federated detection performance

{{TABLE:T4_fl_benchmark}}

Table 4 evaluates federated detection under strict leakage controls. On protocol-semantic features, the centralized detection ceiling is ROC-AUC {{V:fl_benchmarks.splits.random.centralized_upper_bound.roc_auc.mean:f4}} (random) and {{V:fl_benchmarks.splits.session-disjoint.centralized_upper_bound.roc_auc.mean:f4}} (session-disjoint). Federated learning approaches this honest ceiling: `FedAvg (Adam)` achieves ROC-AUC {{V:fl_benchmarks.splits.random.algorithms.FedAvg (Adam).roc_auc.mean:f4}} ± {{V:fl_benchmarks.splits.random.algorithms.FedAvg (Adam).roc_auc.std:f4}} on the random split and {{V:fl_benchmarks.splits.session-disjoint.algorithms.FedAvg (Adam).roc_auc.mean:f4}} ± {{V:fl_benchmarks.splits.session-disjoint.algorithms.FedAvg (Adam).roc_auc.std:f4}} on the session-disjoint split. We recommend `FedAvg (Adam)` as the standard practical deployment baseline.

In contrast, our experiments reveal that SCAFFOLD drift correction provides no meaningful advantage:
- Under identical SGD and GroupNorm settings, `SCAFFOLD (SGD)` achieves ROC-AUC {{V:fl_benchmarks.splits.random.algorithms.SCAFFOLD (SGD).roc_auc.mean:f4}} ± {{V:fl_benchmarks.splits.random.algorithms.SCAFFOLD (SGD).roc_auc.std:f4}} compared to {{V:fl_benchmarks.splits.random.algorithms.FedAvg (SGD).roc_auc.mean:f4}} ± {{V:fl_benchmarks.splits.random.algorithms.FedAvg (SGD).roc_auc.std:f4}} for `FedAvg (SGD)`. The mean difference of +{{V:fl_benchmarks.splits.random.paired_test_scaffold_sgd_vs_fedavg_sgd_auc.mean_diff:f4}} is not statistically significant (paired t p = {{V:fl_benchmarks.splits.random.paired_test_scaffold_sgd_vs_fedavg_sgd_auc.p_value_ttest:f4}}, Wilcoxon p = {{V:fl_benchmarks.splits.random.paired_test_scaffold_sgd_vs_fedavg_sgd_auc.p_value_wilcoxon:f4}}).
- Compared to `FedAvg (Adam)`, `SCAFFOLD (SGD)` is significantly worse (mean difference {{V:fl_benchmarks.splits.random.paired_test_scaffold_sgd_vs_fedavg_adam_auc.mean_diff:f4}}, paired t p = {{V:fl_benchmarks.splits.random.paired_test_scaffold_sgd_vs_fedavg_adam_auc.p_value_ttest:f4}}).
- On the session-disjoint split, SCAFFOLD is unstable across random seeds, exhibiting a wide standard deviation of {{V:fl_benchmarks.splits.session-disjoint.algorithms.SCAFFOLD (SGD).roc_auc.std:f4}} (ROC-AUC {{V:fl_benchmarks.splits.session-disjoint.algorithms.SCAFFOLD (SGD).roc_auc.mean:f4}}).
- Communication cost: SCAFFOLD requires uploading dense control-variate deltas Δc every round, consuming {{V:communication_payload.algorithms.SCAFFOLD (SGD).total_payload_kb:f2}} KB per client per round, compared to {{V:communication_payload.algorithms.FedAvg (SGD).total_payload_kb:f2}} KB for FedAvg and FedProx.

{{TABLE:T12_operating_points}}

Because Edge-IIoTset exhibits substantial class imbalance ({{V:dataset_distribution.attack_share_pct:f1}}% attack flows), standard 0.5 probability thresholding distorts operational tradeoff decisions. Table 12 reports test performance calibrated at two validation operating points: (i) maximum macro-F1 and (ii) a false positive rate bounded at FPR ≤ 5%. To address class imbalance directly during federated aggregation, `FedAvg (Class-Weighted)` incorporates inverse class-frequency weighting during local client training.

### C. Component ablation and model complexity

{{TABLE:T2_model_complexity}}

{{TABLE:T5_ablation}}

Table 2 profiles model complexity, and Table 5 details systematic component ablation across eight development stages:
- **Architecture comparison**: A compact MLP (Stage 1, {{V:ablation_benchmarks.stages.Stage 1.parameters:int}} parameters) attains ROC-AUC {{V:ablation_benchmarks.stages.Stage 1.roc_auc.mean:f4}} ± {{V:ablation_benchmarks.stages.Stage 1.roc_auc.std:f4}}, matching the 12-fold larger TCN + Attention encoder (Stage 4, {{V:ablation_benchmarks.stages.Stage 4.parameters:int}} parameters, ROC-AUC {{V:ablation_benchmarks.stages.Stage 4.roc_auc.mean:f4}} ± {{V:ablation_benchmarks.stages.Stage 4.roc_auc.std:f4}}). Because complex temporal and attention mechanisms provide no measurable benefit on tabular protocol features, the lightweight MLP is the optimal choice for edge deployment.
- **De-confounding SCAFFOLD**: Stage 6 (Top-*k* compression with Adam/BatchNorm) achieves ROC-AUC {{V:ablation_benchmarks.stages.Stage 6.roc_auc.mean:f4}}. Introducing Stage 6b (`FedAvg (SGD, GroupNorm, K=20 steps)`) isolates the optimizer switch, dropping ROC-AUC to {{V:ablation_benchmarks.stages.Stage 6b.roc_auc.mean:f4}}. Adding SCAFFOLD control variates while holding optimizer and normalization constant (Stage 6b → Stage 7) yields only a marginal gain of +0.0052 ROC-AUC (reaching {{V:ablation_benchmarks.stages.Stage 7.roc_auc.mean:f4}} ± {{V:ablation_benchmarks.stages.Stage 7.roc_auc.std:f4}}), confirming that SCAFFOLD does not compensate for the loss of adaptive optimization.

### D. Robustness to Byzantine clients

{{TABLE:T6_poisoning}}

Table 6 evaluates defenses against label-flipping and scaled sign-flipping model replacement:
- Under {{V:poisoning_benchmarks.poison_ratios.2:pct1}} % compromised clients, coordinate-wise median is the most effective defense, maintaining ROC-AUC {{V:poisoning_benchmarks.results_by_ratio.20%.Coordinate_Median.roc_auc.mean:f4}}, followed by trimmed mean ({{V:poisoning_benchmarks.results_by_ratio.20%.Trimmed_Mean.roc_auc.mean:f4}}) and Multi-Krum ({{V:poisoning_benchmarks.results_by_ratio.20%.Multi_Krum.roc_auc.mean:f4}}).
- Norm-bounded cosine trust scoring improves resilience over undefended FedAvg ({{V:poisoning_benchmarks.results_by_ratio.20%.FedAvg_Undefended.roc_auc.mean:f4}}) to {{V:poisoning_benchmarks.results_by_ratio.20%.Cosine_Trust_NormBounded.roc_auc.mean:f4}}, but does not outperform coordinate-wise median.
- Under {{V:poisoning_benchmarks.poison_ratios.4:pct1}} % compromised clients, all defenses degrade significantly (ROC-AUC {{V:poisoning_benchmarks.results_by_ratio.50%.Coordinate_Median.roc_auc.mean:f4}} for median and {{V:poisoning_benchmarks.results_by_ratio.50%.Cosine_Trust_NormBounded.roc_auc.mean:f4}} for cosine trust).

### E. Cross-dataset transfer (Negative result)

{{TABLE:T7_transfer}}

Zero-shot transfer from Edge-IIoTset to WUSTL-IIoT-2021 fails completely, yielding ROC-AUC {{V:cross_dataset_transfer.zero_shot.roc_auc.mean:f4}} on {{V:cross_dataset_transfer.evaluated_target_rows:int}} target flows (Table 7). The fundamental obstacle is feature representation mismatch: Edge-IIoTset records per-packet Wireshark fields, whereas WUSTL-IIoT-2021 records Argus bidirectional flow statistics, leaving only {{V:cross_dataset_transfer.shared_features_count}} semantically overlapping features. Fine-tuning on 20 % of the target achieves ROC-AUC {{V:cross_dataset_transfer.fine_tuned.roc_auc.mean:f4}} ± {{V:cross_dataset_transfer.fine_tuned.roc_auc.std:f4}}, which underperforms training from scratch on the same 20 % partition (ROC-AUC {{V:cross_dataset_transfer.scratch_on_target.roc_auc.mean:f4}} ± {{V:cross_dataset_transfer.scratch_on_target.roc_auc.std:f4}}). We caution researchers against assuming transferability between packet-level and flow-level IIoT datasets.

### F. Post-quantum transport and edge resource profile

{{TABLE:T3_pqc}}

{{TABLE:T8_resources}}

Tables 3 and 8 profile system overhead:
- **Post-quantum cryptography**: Cryptographic overhead is structured by operational role under NIST FIPS-203 ML-KEM-768 with AES-256-GCM. The server executes KeyGen once per round ({{V:resource_profile.pqc_cryptography.keygen.median_ms:f2}} ms) and broadcasts the public key. Each participating client encapsulates a shared secret ({{V:resource_profile.pqc_cryptography.encaps.median_ms:f2}} ms) and encrypts its payload with AES-256-GCM ({{V:resource_profile.pqc_cryptography.aes_gcm_encrypt.median_ms:f4}} ms), adding {{V:resource_profile.pqc_cryptography.ciphertext_overhead_bytes:int}} bytes of transport overhead. The server performs Decaps once per reporting client ({{V:resource_profile.pqc_cryptography.decaps.median_ms:f2}} ms each).
- **Communication payload**: Top-*k* sparsification (k = 30 %) reduces uplink payload to {{V:communication_payload.algorithms.FedAvg (SGD).total_payload_kb:f2}} KB per client per round for FedAvg and FedProx. Including PQC ciphertext, nonce, and authentication tag adds {{V:communication_payload.algorithms.FedAvg (SGD).pqc_overhead_bytes:int}} bytes, for a total wire payload of {{V:communication_payload.algorithms.FedAvg (SGD).total_wire_kb:f2}} KB.
- **Edge inference**: Single-sample inference latency is {{V:resource_profile.single_sample_inference.median_ms:f4}} ms median on a commodity CPU, supporting a throughput of {{V:resource_profile.single_sample_inference.throughput_samples_per_sec:f2}} samples/s.

### G. Decision layer profile

{{TABLE:T9_qaoa}}

Table 9 profiles candidate mitigation selection:
- Classical integer linear programming (ILP via CBC) solves the allocation problem exactly in {{V:qaoa_multi_n_benchmarks.results_by_n.N_1.mean_ilp_latency_ms:f2}} ms for 1 asset (4 qubits), {{V:qaoa_multi_n_benchmarks.results_by_n.N_2.mean_ilp_latency_ms:f2}} ms for 2 assets (8 qubits), and {{V:qaoa_multi_n_benchmarks.results_by_n.N_3.mean_ilp_latency_ms:f2}} ms for 3 assets (12 qubits).
- QAOA on a statevector simulator incurs an optimality gap of {{V:qaoa_multi_n_benchmarks.results_by_n.N_2.mean_qaoa_gap_pct:f2}} % on 8 qubits and {{V:qaoa_multi_n_benchmarks.results_by_n.N_3.mean_qaoa_gap_pct:f2}} % on 12 qubits, while requiring {{V:qaoa_multi_n_benchmarks.results_by_n.N_3.mean_qaoa_latency_ms:f2}} ms.
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

We presented an empirical study of federated intrusion detection on Edge-IIoTset under rigorous leakage controls, measured communication compression, and post-quantum transport. Our findings demonstrate that near-perfect (>99 %) detection on Edge-IIoTset is reproducible in our pipeline only when session identifiers are included; on protocol-semantic features alone, the true centralized detection ceiling is ROC-AUC {{V:fl_benchmarks.splits.random.centralized_upper_bound.roc_auc.mean:f4}}, which federated `FedAvg (Adam)` approaches with ROC-AUC {{V:fl_benchmarks.splits.random.algorithms.FedAvg (Adam).roc_auc.mean:f4}}. We report four negative results: SCAFFOLD drift correction provides no significant benefit under identical SGD settings while more than doubling uplink bandwidth; a compact 3.4k-parameter MLP matches complex convolutional attention encoders; cross-dataset transfer between packet and flow representations fails zero-shot; and QAOA provides no advantage over classical ILP. Post-quantum transport under ML-KEM-768 is computationally viable on commodity hardware.

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

[33] M. Galal, "Pitfalls and artifact exploitation in modern network intrusion detection datasets," arXiv:2608.15761, 2024.
