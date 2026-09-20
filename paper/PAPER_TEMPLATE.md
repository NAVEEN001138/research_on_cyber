# Quantum-Resistant, Communication-Efficient Federated Intrusion Detection for Industrial IoT: An Honest Baseline on Edge-IIoTset

**Naveen Ravi**

---

### Abstract

Federated learning (FL) lets industrial IoT (IIoT) sites train a shared intrusion detector without centralising raw telemetry, but a deployable design must also survive future quantum adversaries on the wire, tolerate non-IID sites and Byzantine participants, and fit edge bandwidth budgets. This paper presents *Cloud Guardian*, a nine-layer FL intrusion-detection framework in which model updates are transported under NIST FIPS-203 ML-KEM-768 key encapsulation with AES-256-GCM payload encryption, compressed by top-*k* sparsification with error feedback, and aggregated by FedAvg, FedProx or SCAFFOLD with cosine-similarity trust weighting. Our second contribution is methodological. After removing flow-identifier and payload features that let prior Edge-IIoTset models memorise attack sessions, and fitting all preprocessing on the training partition only, a {{V:fl_benchmarks.features_count}}-feature protocol-semantic representation bounds detection at a centrally-trained ROC-AUC of {{V:fl_benchmarks.splits.random.centralized_upper_bound.roc_auc.mean:f4}} (macro-F1 {{V:fl_benchmarks.splits.random.centralized_upper_bound.macro_f1.mean:f4}}); federated SCAFFOLD reaches ROC-AUC {{V:fl_benchmarks.splits.random.algorithms.SCAFFOLD.roc_auc.mean:f4}} ± {{V:fl_benchmarks.splits.random.algorithms.SCAFFOLD.roc_auc.std:f4}} over {{LEN:fl_benchmarks.seeds}} seeds with K = {{V:fl_benchmarks.num_clients}} Dirichlet-partitioned clients. ML-KEM-768 key establishment costs {{V:resource_profile.pqc_cryptography._derived_total_kem_median_ms:f2}} ms per client per round in a pure-Python reference implementation, and the sparsified update is {{V:fl_benchmarks._derived_payload_reduction_pct_vs_float32:f1}} % smaller than the raw float32 parameter vector. Under {{V:poisoning_benchmarks.poison_ratios.4:pct1}} % malicious clients, cosine-trust aggregation retains ROC-AUC {{V:poisoning_benchmarks.results_by_ratio.50%.Cosine_Trust.roc_auc.mean:f4}} against {{V:poisoning_benchmarks.results_by_ratio.50%.FedAvg_Undefended.roc_auc.mean:f4}} for undefended FedAvg, compared side by side with coordinate-wise median, trimmed mean and Multi-Krum. Zero-shot transfer to the flow-level WUSTL-IIoT-2021 dataset fails (ROC-AUC {{V:cross_dataset_transfer.zero_shot.roc_auc.mean:f4}}) because only {{V:cross_dataset_transfer.shared_features_count}} features are semantically shared; we report this as a negative result. Every number in this paper is generated from a single machine-produced results file and verified by an automated checker.

**Index Terms** — Federated learning, intrusion detection, Industrial IoT, post-quantum cryptography, ML-KEM, Byzantine robustness, Edge-IIoTset, reproducibility.

---

## I. INTRODUCTION

Industrial cyber-physical systems expose Modbus/TCP, MQTT, DNS, HTTP and ARP telemetry at many geographically separated sites. Centralising that telemetry for intrusion detection raises three practical obstacles: (i) raw packet captures may contain personal or commercially sensitive data whose cross-site transfer carries regulatory and contractual risk; (ii) the update traffic of any distributed learner is a long-lived secret — an adversary that records it today can decrypt it once a cryptanalytically relevant quantum computer exists ("harvest now, decrypt later") [21]; and (iii) sites differ in the traffic they see, so a federated detector must cope with statistical heterogeneity and, in the worst case, with compromised participants.

A large body of work reports near-perfect accuracy on the Edge-IIoTset benchmark [1]. Much of it, as Arp et al. warn for security ML in general [22], is inflated by *data snooping*: features such as TCP ports, sequence and acknowledgement numbers, checksums and raw payload bytes identify the capture session rather than the attack behaviour, and random row-level splits place packets of the same session on both sides of the train/test boundary. We take the opposite position. We remove every flow-identifier and content feature, fit all preprocessing on the training partition only, add a time-ordered hold-out, and report the centralised upper bound next to every federated number so the reader can see how much of the gap is due to federation and how much to the representation.

**Contributions.**
1. A complete FL intrusion-detection pipeline for IIoT with post-quantum transport (ML-KEM-768 + HKDF + AES-256-GCM), top-*k* update compression with error feedback, three aggregation rules (FedAvg, FedProx, SCAFFOLD) and cosine-similarity trust weighting, evaluated on Edge-IIoTset with Dirichlet non-IID partitions and {{LEN:fl_benchmarks.seeds}} seeds (Section VI-B).
2. A leakage-controlled evaluation protocol for Edge-IIoTset with an explicit feature exclusion list, train-only preprocessing, random and temporal hold-outs, and imbalance-aware metrics (Section V).
3. A Byzantine-robustness study that places the proposed trust weighting next to coordinate-wise median, trimmed mean and Multi-Krum under label-flip plus scaled sign-flip attacks at {{V:poisoning_benchmarks.poison_ratios.1:pct1}}–{{V:poisoning_benchmarks.poison_ratios.4:pct1}} % malicious clients (Section VI-D).
4. A negative cross-dataset result (Edge-IIoTset → WUSTL-IIoT-2021) with an analysis of why packet-level and flow-level feature spaces do not transfer (Section VI-E).
5. A fully traceable reporting pipeline: one experiment driver writes one results file; every table and every number in the text is rendered from it and verified by `check_paper_numbers.py`.

The decision-optimisation layer of the framework (QUBO formulation of incident response, solved by QAOA or ILP) is described for completeness in Section IV-G and profiled at simulator-feasible sizes in Section VI-G; its full evaluation is deferred to a companion paper.

---

## II. RELATED WORK

**Federated intrusion detection for IoT/IIoT.** DÏoT [24] introduced federated self-learning anomaly detection on IoT gateways; Rahman et al. [26] compared centralised, on-device and federated IDS training for IoT; Popoola et al. [25] applied federated deep learning to zero-day botnet detection on IoT-edge devices. These works establish that FL is viable for IoT IDS but evaluate with random splits on identifier-rich features and do not consider quantum-safe transport or Byzantine participants.

**Edge-IIoTset.** Ferrag et al. [1] released Edge-IIoTset with 14 attack classes over a realistic IIoT testbed and reported centralised and federated baselines. Subsequent papers frequently report >99 % accuracy; we show (Section VI-A) that on protocol-semantic features alone the centralised ceiling is far lower, which we attribute to session-identifier leakage in the commonly used feature set, consistent with the pitfalls catalogued by Arp et al. [22].

**Heterogeneity-aware aggregation.** FedAvg [4] is the baseline; FedProx [5] adds a proximal term; SCAFFOLD [6] corrects client drift with control variates. Dirichlet partitioning [19] is the standard way to control non-IID severity. We evaluate all three rules under the same partitions and report paired significance tests rather than point estimates.

**Communication efficiency.** Top-*k* gradient sparsification with error feedback [18], [27] reduces uplink traffic without changing the fixed point. We measure the *serialized* payload including indices and non-trainable buffers rather than counting kept values.

**Byzantine robustness.** Krum/Multi-Krum [12], coordinate-wise median and trimmed mean [13], and FLTrust [14] are the reference defences. Our cosine-similarity trust weighting is a lightweight heuristic in the FLTrust family; we do not claim it dominates these methods and report it beside them.

**Post-quantum transport for FL.** NIST standardised ML-KEM in FIPS 203 [7] following the Kyber design [29]; Mosca [21] frames the harvest-now-decrypt-later risk. Most FL security papers still assume classical TLS. We use ML-KEM-768 per round with HKDF [9] and AES-256-GCM [8], and we measure its cost with a FIPS-203 reference implementation.

**Secure aggregation and differential privacy.** Bonawitz et al. [11] and DP-SGD [10] provide cryptographic and statistical privacy for updates respectively. We implement neither in this paper and say so explicitly (Section VII); the Gaussian perturbation we apply to updates carries no formal privacy guarantee.

---

## III. THREAT MODEL AND SYSTEM OVERVIEW

### A. Threat model

We consider three adversaries (full statement in the repository's `docs/threat_model.md`):

- **Honest-but-curious aggregator.** Executes the protocol faithfully but may inspect individual updates. We provide transport confidentiality only; server-side secure aggregation is out of scope.
- **Byzantine clients.** Up to *f* < *K*/2 clients may flip local labels and submit scaled, sign-flipped updates Δw<sub>mal</sub> = −λ·Δw. Clients are assumed to be authenticated out of band; post-quantum *authentication* (e.g., ML-DSA) is out of scope.
- **Passive network adversary with future quantum capability.** Records all traffic and may later run Shor's algorithm. Key establishment therefore uses ML-KEM-768; each round's AES-GCM associated data binds the round number and client id, which rejects replay across rounds.

### B. Nine-layer architecture

Layer 0 preprocesses telemetry (train-fitted scaling); Layer 1 shards it into clients; Layer 2 performs federated detection with the security wrapper; Layers 3–4 aggregate context and gate actions by confidence; Layer 5 synthesises adaptive constraints; Layer 6 solves response selection as a QUBO/ILP; Layer 7 scores response utility; Layer 8 executes and explains; Layer 9 feeds outcomes back. This paper evaluates Layers 0–2 in depth and profiles Layer 6.

---

## IV. METHODOLOGY

### A. Feature representation and leakage control

From the {{V:dataset_distribution.total_columns}} columns of `ML-EdgeIIoT-dataset.csv` we retain {{V:fl_benchmarks.features_count}} protocol-semantic numeric fields (ARP opcode and hardware size, HTTP content length and response flag, TCP connection-state flags and segment length, DNS query fields, MQTT header/flag/length/type/version fields). We exclude, by name, every host address, port, sequence/acknowledgement number, checksum, stream index, inter-arrival time, frame timestamp, ICMP sequence/timestamp, Modbus transaction id, and every raw content field (TCP payload, HTTP file data and URI query, DNS query name, MQTT topic and message). Four columns that are constant across the whole file are also dropped. The exclusion list is a code constant with a comment explaining each group.

Rows are split first; the `StandardScaler` is then fitted on the training rows only and applied to both partitions. We report two hold-outs: a stratified random 80/20 split, and a *temporal* split in which the last 20 % of rows in `frame.time` order form the test set. Because the corpus is {{V:dataset_distribution.attack_share_pct:f1}} % attack, we report accuracy only alongside macro-F1, ROC-AUC (from softmax scores), PR-AUC, MCC and the confusion matrix; a run whose ROC-AUC is below 0.55 is flagged by the pipeline as a constant-class predictor.

### B. Local model

The edge classifier is a 1-D convolutional encoder over the feature vector with two dilated residual blocks (32 and 64 channels, kernel 3, dilations 1 and 2), followed by four-head self-attention over the 64-dimensional channel positions, mean pooling, a 32-unit dense layer and a two-way softmax. Inputs are per-flow feature vectors, not packet sequences, so the convolution operates over feature positions; we therefore do *not* describe the model as temporal. It has {{V:fl_benchmarks.model_profiles.TCN_Attention.parameters:int}} trainable parameters ({{V:fl_benchmarks.model_profiles.TCN_Attention.model_size_bytes:kb}} KB in float32). Baselines with identical training are an MLP ({{V:fl_benchmarks.model_profiles.MLP.parameters:int}} parameters), a plain 1-D CNN and the same encoder without attention (Table 2).

### C. Federated optimisation

K = {{V:fl_benchmarks.num_clients}} clients receive Dirichlet(α = 0.5) label-skewed shards [19]; C = {{V:fl_benchmarks.participation_rate}} of them participate per round for {{V:fl_benchmarks.num_rounds}} rounds, each running {{V:fl_benchmarks.local_epochs}} local epochs of Adam (lr {{V:fl_benchmarks.learning_rate}}, batch {{V:fl_benchmarks.batch_size}}). We compare FedAvg [4], FedProx [5] (μ = 0.01, proximal term to the *current* global weights) and SCAFFOLD [6]. Because the local optimiser is Adam, SCAFFOLD's control variates use the gradient-average form (Option I of [6]) rather than the weight-difference form that assumes SGD. Control variates are computed from the unsparsified local model; sparsification is applied to the transmitted weight delta only, and control-variate deltas are transmitted dense and counted in the payload.

### D. Update compression

Each client transmits Δw = w<sub>local</sub> − w<sub>global</sub> after top-*k* magnitude sparsification with *k* = 30 % per tensor and client-side error feedback [27]; non-trainable BatchNorm buffers are sent dense. The payload we report is the byte length of `torch.save` on the actual sparse structure (float32 values, int32 indices, tensor keys and shapes), not the count of retained values.

### E. Quantum-resistant transport

Per round *r*, the server publishes an ephemeral ML-KEM-768 encapsulation key. Each client encapsulates a 32-byte shared secret, derives K<sub>k,r</sub> = HKDF-SHA256(ss, info = "fl-round-"‖r) and encrypts its serialized update with AES-256-GCM under a fresh 96-bit nonce, with (r, client id) as associated data. The server decapsulates, derives the same key, verifies the tag and decrypts. We use `kyber-py` 1.2.0, a pure-Python FIPS-203 implementation, which is not constant-time and is slower than liboqs; the latencies in Table 3 are therefore an upper bound. Wrong-key decapsulation, tag verification on tampered ciphertext and round-trip correctness are unit-tested.

### F. Byzantine-robust aggregation

The server maintains a trust score per client, updated by the cosine similarity between the client's update and a robust reference (the coordinate-wise median of the previous round's updates), and aggregates with weights proportional to sample count × trust. This is a heuristic in the FLTrust family, not reinforcement learning. We evaluate it against undefended FedAvg, coordinate-wise median, trimmed mean (β = 0.2) and Multi-Krum [12], [13] under simultaneous label flipping and scaled sign-flip model replacement (λ = 5) at {{V:poisoning_benchmarks.poison_ratios.1:pct1}}, {{V:poisoning_benchmarks.poison_ratios.2:pct1}}, {{V:poisoning_benchmarks.poison_ratios.3:pct1}} and {{V:poisoning_benchmarks.poison_ratios.4:pct1}} % malicious clients.

### G. Response selection as a QUBO (Layer 6)

Given assets *i* with threat score *s<sub>i</sub>* and candidate actions *a* with effectiveness β<sub>a</sub> and cost c<sub>ia</sub>, binary variables x<sub>ia</sub> minimise Σ<sub>ia</sub>(−β<sub>a</sub>s<sub>i</sub> + c<sub>ia</sub>)x<sub>ia</sub> subject to one action per asset (quadratic one-hot penalty) and a budget (hard inequality in the ILP; one-sided quadratic penalty in the QUBO — the QUBO relaxation also penalises under-spend, a known limitation). We solve with CBC via PuLP (exact), a budgeted greedy heuristic, and QAOA (p = 1 layer, statevector simulator with 2048 shots, COBYLA with at most 8 iterations) on 4, 8 and 12 qubits; instances above the simulator limit raise an error rather than returning a placeholder.

---

## V. EXPERIMENTAL SETUP

All experiments ran on a single machine: {{ENV:cpu_model}} ({{ENV:physical_cores}} physical cores, {{ENV:ram_gb}} GB RAM, no GPU), {{ENV:os}}, Python {{ENV:python_version}}, PyTorch {{ENV:torch_version}}, Qiskit {{ENV:qiskit_version}}, {{ENV:torch_threads}} intra-op threads. Seeds {{V:fl_benchmarks.seeds.0}}, {{V:fl_benchmarks.seeds.1}}, {{V:fl_benchmarks.seeds.2}}, {{V:fl_benchmarks.seeds.3}}, {{V:fl_benchmarks.seeds.4}} are applied to Python, NumPy and PyTorch. The FL benchmark uses a stratified {{V:fl_benchmarks.sample_size:int}}-row sample of the {{V:fl_benchmarks.dataset_total_rows:int}}-row ML file; the ablation and poisoning phases use their own samples as stated in each table caption. Statistics are mean ± standard deviation over seeds with 95 % *t*-intervals; SCAFFOLD vs FedAvg is compared by paired *t*-test and Wilcoxon signed-rank test across seeds. Latency is measured at batch size 1 after 200 warm-up calls over 2000 timed calls (median, P95, P99). Energy is *estimated* as median round time × an assumed {{V:resource_profile.energy_consumption.assumed_tdp_watts:f1}} W TDP and is labelled as such. All results are produced by `run_experiments.py`, written to `results/RESULTS.json`, rendered into this document by `generate_paper_tables.py`/`build_paper.py`, and verified by `check_paper_numbers.py`.

{{TABLE:T1_dataset}}

---

## VI. RESULTS

### A. Model complexity

{{TABLE:T2_model_complexity}}

### B. Federated detection performance

{{TABLE:T4_fl_benchmark}}

Table 4 is the central result. Three observations follow directly from it. First, the *centralised* bound on the leakage-controlled representation is ROC-AUC {{V:fl_benchmarks.splits.random.centralized_upper_bound.roc_auc.mean:f4}} (macro-F1 {{V:fl_benchmarks.splits.random.centralized_upper_bound.macro_f1.mean:f4}}) on the random split and {{V:fl_benchmarks.splits.temporal.centralized_upper_bound.roc_auc.mean:f4}} on the temporal split; the widely reported >99 % accuracies on Edge-IIoTset are not reachable without the identifier features we excluded, and we regard the present numbers as the honest ceiling for protocol-semantic detection on this corpus. Second, federated SCAFFOLD attains ROC-AUC {{V:fl_benchmarks.splits.random.algorithms.SCAFFOLD.roc_auc.mean:f4}} ± {{V:fl_benchmarks.splits.random.algorithms.SCAFFOLD.roc_auc.std:f4}} (random) and {{V:fl_benchmarks.splits.temporal.algorithms.SCAFFOLD.roc_auc.mean:f4}} ± {{V:fl_benchmarks.splits.temporal.algorithms.SCAFFOLD.roc_auc.std:f4}} (temporal), against {{V:fl_benchmarks.splits.random.algorithms.FedAvg.roc_auc.mean:f4}} and {{V:fl_benchmarks.splits.temporal.algorithms.FedAvg.roc_auc.mean:f4}} for FedAvg; the paired *t*-test on accuracy gives p = {{V:fl_benchmarks.splits.random.paired_test_scaffold_vs_fedavg.p_value_ttest:f4}} (random) and p = {{V:fl_benchmarks.splits.temporal.paired_test_scaffold_vs_fedavg.p_value_ttest:f4}} (temporal). Third, the per-round learning curves stored with each trial show whether a seed left the majority-class basin; macro-F1 rather than accuracy should be read to detect the seeds that did not.

### C. Component ablation

{{TABLE:T5_ablation}}

### D. Robustness to Byzantine clients

{{TABLE:T6_poisoning}}

At {{V:poisoning_benchmarks.poison_ratios.4:pct1}} % malicious clients, undefended FedAvg reaches ROC-AUC {{V:poisoning_benchmarks.results_by_ratio.50%.FedAvg_Undefended.roc_auc.mean:f4}}, coordinate-wise median {{V:poisoning_benchmarks.results_by_ratio.50%.Coordinate_Median.roc_auc.mean:f4}}, trimmed mean {{V:poisoning_benchmarks.results_by_ratio.50%.Trimmed_Mean.roc_auc.mean:f4}}, Multi-Krum {{V:poisoning_benchmarks.results_by_ratio.50%.Multi_Krum.roc_auc.mean:f4}} and cosine trust {{V:poisoning_benchmarks.results_by_ratio.50%.Cosine_Trust.roc_auc.mean:f4}}. The reader should compare the defences by ROC-AUC and macro-F1, since the attack pushes models toward the majority class and accuracy alone rewards that failure mode.

### E. Cross-dataset transfer (negative result)

{{TABLE:T7_transfer}}

Zero-shot transfer from Edge-IIoTset to WUSTL-IIoT-2021 yields ROC-AUC {{V:cross_dataset_transfer.zero_shot.roc_auc.mean:f4}} on {{V:cross_dataset_transfer.evaluated_target_rows:int}} target flows. The two corpora do not share a feature space: Edge-IIoTset rows are per-packet Wireshark fields while WUSTL-IIoT-2021 rows are Argus flow statistics, and only {{V:cross_dataset_transfer.shared_features_count}} fields have a defensible common meaning. Fine-tuning on 20 % of the target reaches ROC-AUC {{V:cross_dataset_transfer.fine_tuned.roc_auc.mean:f4}} ± {{V:cross_dataset_transfer.fine_tuned.roc_auc.std:f4}}, which must be read against a model trained from scratch on the same 20 %: {{V:cross_dataset_transfer.scratch_on_target.roc_auc.mean:f4}} ± {{V:cross_dataset_transfer.scratch_on_target.roc_auc.std:f4}}. We report this as a negative result and caution against cross-dataset claims between packet-level and flow-level IIoT corpora.

### F. Post-quantum transport and edge resource profile

{{TABLE:T3_pqc}}

{{TABLE:T8_resources}}

One ML-KEM-768 key establishment (keygen + encaps + decaps) costs {{V:resource_profile.pqc_cryptography._derived_total_kem_median_ms:f2}} ms median per client per round in the pure-Python reference implementation and adds {{V:resource_profile.pqc_cryptography.ciphertext_overhead_bytes:int}} bytes of ciphertext; AES-256-GCM encryption of the {{V:resource_profile.pqc_cryptography.payload_bytes:int}}-byte test payload takes {{V:resource_profile.pqc_cryptography.aes_gcm_encrypt.median_ms:f4}} ms. Against a median SCAFFOLD round time of {{V:fl_benchmarks.splits.random.algorithms.SCAFFOLD.median_round_time_sec:f2}} s, the cryptographic overhead is negligible even before switching to an optimised library. The sparsified update is {{V:fl_benchmarks.splits.random.algorithms.SCAFFOLD.mean_comm_payload_bytes:kb}} KB per client per round, {{V:fl_benchmarks._derived_payload_reduction_pct_vs_float32:f1}} % below the {{V:fl_benchmarks.model_profiles.TCN_Attention.model_size_bytes:kb}} KB raw float32 vector once indices and dense buffers are counted.

### G. Decision layer profile

{{TABLE:T9_qaoa}}

---

## VII. LIMITATIONS

- **No formal privacy guarantee.** The Gaussian perturbation applied to updates is not DP-SGD [10]; no (ε, δ) is claimed. Secure aggregation [11] is not implemented; the server sees individual decrypted updates.
- **No post-quantum authentication.** ML-KEM provides confidentiality; client authentication is assumed out of band.
- **Reference-implementation cryptography.** `kyber-py` is not constant-time and is 1–2 orders of magnitude slower than liboqs; the reported latencies are upper bounds.
- **Simulation on one machine.** All clients run sequentially on a single CPU; no device or network heterogeneity, dropout or straggler behaviour is modelled. Energy is a TDP-proxy estimate.
- **Representation ceiling.** Excluding identifier features lowers attainable accuracy on Edge-IIoTset substantially; richer behavioural features (e.g., windowed packet sequences per device) are future work.
- **Trust heuristic.** Cosine trust weighting is not proven robust under adaptive attackers and is reported next to, not above, established defences.
- **Decision layer.** QAOA is evaluated on a statevector simulator at ≤ 12 qubits only; larger instances are solved exactly by ILP and no quantum advantage is claimed.

---

## VIII. CONCLUSION

We presented a federated IIoT intrusion-detection framework with quantum-resistant transport, measured communication compression and Byzantine-robust aggregation, and we evaluated it under a leakage-controlled protocol on Edge-IIoTset with a temporal hold-out and a centralised reference. The honest ceiling of protocol-semantic detection on this corpus is ROC-AUC {{V:fl_benchmarks.splits.random.centralized_upper_bound.roc_auc.mean:f4}}; federated SCAFFOLD reaches {{V:fl_benchmarks.splits.random.algorithms.SCAFFOLD.roc_auc.mean:f4}} while transmitting {{V:fl_benchmarks.splits.random.algorithms.SCAFFOLD.mean_comm_payload_bytes:kb}} KB per client per round under ML-KEM-768/AES-GCM at a cost of {{V:resource_profile.pqc_cryptography._derived_total_kem_median_ms:f2}} ms per round. We showed that cross-dataset transfer between packet-level and flow-level IIoT corpora does not work zero-shot, and we released the pipeline that renders and verifies every number in this paper. Future work is real DP-SGD with a privacy accountant, pairwise-masked secure aggregation, ML-DSA authentication, windowed sequence features, and a hardware evaluation of the decision layer.

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
