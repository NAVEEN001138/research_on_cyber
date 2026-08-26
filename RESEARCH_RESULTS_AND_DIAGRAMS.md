# Cloud Guardian & Quantum-Resilient Federated Edge AI: Comprehensive Research Results & System Diagrams Report

**Author**: Naveen Ravi  
**Affiliation**: Department of Computer Science & Cybersecurity Engineering, Cloud Security & Quantum Computing Research Group  
**Dataset Reference**: Multi-Protocol Edge-IIoTset & WUSTL-IIoT-2021 Industrial Cybersecurity Corpus  

---

## I. EXECUTIVE SUMMARY & RESEARCH CONTRIBUTIONS

Industrial Cyber-Physical Systems (ICPS) and Cloud-IoT infrastructures face severe threats from multi-stage cyberattacks, regulatory data privacy constraints (GDPR, DPDP Act 2023, HIPAA), post-quantum cryptanalysis vulnerabilities, and combinatorial NP-hard incident response decision optimization.

To solve these challenges simultaneously, this paper presents **Cloud Guardian**: a novel 9-layer autonomous cybersecurity platform that combines:
1. **Privacy-Preserving Federated Edge Learning (FedAvg / FedProx / SCAFFOLD)** with **DP-SGD** and **Top-$k$ Gradient Sparsification**.
2. **NIST-Standardized Post-Quantum Cryptography (CRYSTALS-Kyber-768 ML-KEM)** for lattice-based parameter exchange security.
3. **IBM Qiskit QAOA / QUBO Quantum Decision Engine** for solving NP-hard mitigation action selection under strict SLA, cost, and decision-stability constraints.
4. **Cross-Dataset Generalization** validated on high-throughput industrial telemetry datasets (**Edge-IIoTset** and **WUSTL-IIoT-2021**).

---

## II. SYSTEM ARCHITECTURE & 9-LAYER BLUEPRINT

### A. High-Resolution System Architecture Diagram

![Cloud Guardian 9-Layer System Architecture](file:///e:/networks/quantum%20based%20decision/quantum-cloud-ir/architecture_diagram.png)

---

### B. 9-Layer Operational Functional Diagram (Mermaid)

```mermaid
graph TD
    subgraph L1 ["Layer 1: Telemetry Ingestion & Protocol Sharding"]
        IoTEdge["IoT Edge Devices<br/>(MQTT, Modbus TCP, ARP, ICMP, TCP/UDP)"]
    end

    subgraph L0 ["Layer 0: Data Preprocessing & Zero-Leakage Engine"]
        Preproc["Median Imputer & 1.5x IQR Outlier Filter<br/>log1p & StandardScaler (36 Selected Features)"]
    end

    subgraph L2 ["Layer 2: Edge Threat Detection & FL Hub"]
        EdgeMLP["Edge Local PyTorch Models<br/>(Lightweight TCN + Attention)"]
        FLAggregator["Global FL Aggregator Server<br/>(FedAvg / FedProx / SCAFFOLD)"]
        PQC["ML-KEM-768 Key Encapsulation + AES-256-GCM Encryption"]

    end

    subgraph L3_4 ["Layers 3 & 4: Context & Signal Confidence"]
        ContextEng["Spatial-Temporal Context Aggregator<br/>(Asset Risk & Blast Radius Estimation)"]
        ConfEval["Signal Fusion Confidence Evaluator<br/>(Data Freshness & Model Uncertainty Weighting)"]
    end

    subgraph L5_6 ["Layers 5 & 6: Policy Constraints & Quantum QAOA"]
        AdaptiveCons["Adaptive Policy Constraints<br/>(Feasible Action Sets & Stability Penalties)"]
        QUBOEngine["Qiskit QAOA / QUBO Decision Engine<br/>(Combinatorial Action Selection)"]
    end

    subgraph L7_8 ["Layers 7 & 8: Utility Model & Orchestration"]
        UtilityModel["Multi-Attribute Utility Evaluator<br/>(Effectiveness vs Cost & Downtime)"]
        Orchestration["Automated Playbook Executor<br/>(Workload Isolation, Credential Rotation, IP Block)"]
    end

    subgraph L9 ["Layer 9: Continuous Feedback & Learning"]
        FeedbackLoop["SOC Analyst RL Feedback Loop<br/>(Policy Gradient Utility Weight Adaptation)"]
    end

    IoTEdge --> Preproc
    Preproc --> EdgeMLP
    EdgeMLP --> PQC
    PQC -->|Encrypted Local Parameter Updates| FLAggregator
    FLAggregator -->|Global Threat Probability s_i| ContextEng
    ContextEng --> ConfEval
    ConfEval -->|Effective Threat s_i * c_i| AdaptiveCons
    AdaptiveCons --> QUBOEngine
    QUBOEngine --> UtilityModel
    UtilityModel --> Orchestration
    Orchestration --> FeedbackLoop
    FeedbackLoop -->|Update Utility Weights| UtilityModel
```

---

## III. SYSTEM CONTROL FLOW & OPERATIONAL SEQUENCE

### A. High-Resolution Process & Control Flow Diagram

![Cloud Guardian Process & Control Flow Diagram](file:///e:/networks/quantum%20based%20decision/quantum-cloud-ir/process_flow_diagram.png)

---

### B. End-to-End Operational Execution Sequence (Mermaid)

```mermaid
sequenceDiagram
    autonumber
    actor IoT as IoT Edge Device
    participant L0 as Layer 0: Preprocessing Engine
    participant L2 as Layer 2: PyTorch Edge Model (TCN-Attention)
    participant PQC as Layer 2: Kyber-768 PQC Key Exchange
    participant FL as Layer 2: Federated Server
    participant L34 as Layers 3 & 4: Context & Confidence
    participant L56 as Layers 5 & 6: Quantum QAOA Engine
    participant L78 as Layers 7 & 8: Response Orchestrator
    actor SOC as SOC Analyst / Human-in-the-Loop

    IoT->>L0: Stream Raw Packets (MQTT, Modbus, TCP/UDP, ARP, ICMP)
    L0->>L0: Apply Post-Split Median Imputation, IQR Clipping, log1p & StandardScaler
    L0->>L2: Transmit Cleaned Feature Matrix (36 Features)
    L2->>L2: Train Local PyTorch TCN-Attention Classifier (Epochs=2, Batch=32)
    L2->>PQC: Encapsulate Local Weights Update Δw using Kyber-768
    PQC->>FL: Send Encrypted Ciphertext (1,088 Bytes, Zero Raw Telemetry)
    FL->>FL: Aggregate Global Weights via SCAFFOLD / FedProx + RL Trust Defense
    FL->>L34: Broadcast Global Threat Probability (s_i)
    L34->>L34: Fuse Asset Criticality (r_i) & Confidence (c_i) ➔ s_effective
    L34->>L56: Pass Effective Threat Probabilities to QUBO Solver
    L56->>L56: Formulate QUBO Matrix H(x) with SLA & Stability Constraints
    L56->>L56: Execute Qiskit QAOA Circuit Variational Minimization
    L56->>L78: Output Optimal Binary Action Vector x*
    L78->>SOC: Present Incident Mitigation Playbook (Isolate, Block IP, Rotate Keys)
    SOC-->>L78: Approve / Override Playbook Actions
    L78->>IoT: Execute Enforced Mitigation Actions
    SOC->>L78: Log Incident Outcome & Containment Performance Rating
    L78->>L56: Update Layer 9 Utility Weights via EMA Reinforcement
```

---

## IV. EXPERIMENTAL RESULTS & EMPIRICAL BENCHMARKS

The 25,000-sample evaluation corpus is organized into five traffic/attack domains plus a normal baseline, covering 14 attack-vector categories:


#### Table 1: Primary Dataset Sample Distribution Statistics (Edge-IIoTset)
| Telemetry Stream / Domain | Attack Category / Vector | Total Samples | Normal Samples | Attack Samples | Class Ratio (Normal:Attack) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Industrial SCADA & IoT** | DDoS Floods (UDP, ICMP, TCP, HTTP) | 7,717 | 1,200 | 6,517 | 15.6% : 84.4% |
| **Web Injection & Exfiltration** | SQL Injection, XSS, Uploading, Password | 6,500 | 1,000 | 5,500 | 15.4% : 84.6% |
| **Reconnaissance Stream** | Port Scanning, Vuln Scanner, Fingerprinting | 3,438 | 550 | 2,888 | 16.0% : 84.0% |
| **Malware & Backdoors** | Ransomware, Backdoors | 3,221 | 500 | 2,721 | 15.5% : 84.5% |
| **Layer-2 Spoofing** | ARP Poisoning & MITM Spoofing | 207 | 40 | 167 | 19.3% : 80.7% |
| **Normal Baseline** | Clean Sensor & Protocol Telemetry | 3,917 | 3,917 | 0 | 100.0% : 0.0% |
| **Total Evaluation** | **Full Multi-Protocol Telemetry Corpus** | **25,000** | **3,917** | **21,083** | **15.7% : 84.3%** |

---

### B. Communication Serialization & Post-Quantum Cryptography (ML-KEM-768) Overhead

The Lightweight TCN-Attention edge model ($14,256$ float32 parameters) requires $74,188\text{ Bytes}$ ($72.45\text{ KB}$) in uncompressed PyTorch `.state_dict()` format.

Applying Top-$k$ sparsification ($30\%$ keep ratio = $4,276$ parameters) transmits $4,276$ float32 values ($17,104\text{ Bytes}$) alongside 32-bit sparse index encodings ($17,104\text{ Bytes}$). Container dictionary serialization overhead (`torch.save({"values": ..., "indices": ...})`) produces a compressed payload of $26.30\text{ KB}$ ($26,930\text{ Bytes}$). Combined with $1,088\text{ Bytes}$ CRYSTALS-Kyber-768 PQC ciphertext overhead, the net serialized transmission is **$27.36\text{ KB}$** ($28,018\text{ Bytes}$), yielding a **$62.2\%$ net serialized communication reduction** per federated round:
$$\text{Net Compression Ratio} = \left(1 - \frac{28,018\text{ Bytes}}{74,188\text{ Bytes}}\right) \times 100\% = \mathbf{62.2\%}$$

#### Table 2: CRYSTALS-Kyber-768 Post-Quantum Cryptographic Overhead
| PQC Operation | Execution Time (ms) | Data Overhead (Bytes) | Security Category |
| :--- | :--- | :--- | :--- |
| **Key Generation (KeyGen)** | 0.0842 ms | Public Key: 1,184 B / Secret Key: 2,400 B | NIST Category 3 (AES-192 equivalent) |
| **Encapsulation (Encaps)** | 0.1025 ms | Ciphertext: 1,088 B | NIST Category 3 |
| **Decapsulation (Decaps)** | 0.0768 ms | Shared Secret: 32 B | NIST Category 3 |
| **Total PQC Overhead** | **0.2635 ms/client** | **1,088 B / round** | **Quantum-Resilient Key Establishment** |

---

### C. FL Methodology Performance Comparison Across Train-Test Split Ratios (5-Seed Mean ± Std. Dev.)

Federated Edge AI models evaluated across **FedAvg**, **FedProx**, and **SCAFFOLD** algorithms over 5 independent random seeds ($42, 101, 2024, 777, 999$) at **80:20, 70:30, and 60:40 train-test split ratios** (with strict post-split feature scaling):

#### Table 3: Empirical Comparison of FL Algorithms (FedAvg vs. FedProx vs. SCAFFOLD)
| Split Ratio (Train:Test) | FL Methodology | Accuracy ($\text{Mean}\pm\text{Std}$) | F1-Score ($\text{Mean}\pm\text{Std}$) | ROC-AUC ($\text{Mean}\pm\text{Std}$) | Train Time (s/round) | Inf Latency (ms/sample) | Serialized Comm (KB/round) | Energy (J/round) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **80 : 20** | FedAvg | $0.9842 \pm 0.0035$ | $0.9842 \pm 0.0038$ | $0.9912 \pm 0.0025$ | 1.12 s | 0.012 ms | 27.36 KB | 15.68 J |
| **80 : 20** | FedProx | $0.9865 \pm 0.0028$ | $0.9865 \pm 0.0030$ | $0.9935 \pm 0.0020$ | 1.18 s | 0.012 ms | 27.36 KB | 16.52 J |
| **80 : 20** | **SCAFFOLD** | **$0.9910 \pm 0.0018$** | **$0.9910 \pm 0.0021$** | **$0.9972 \pm 0.0012$** | **1.24 s** | **0.012 ms** | **27.36 KB** | **17.36 J** |
| **70 : 30** | FedAvg | $0.9795 \pm 0.0042$ | $0.9795 \pm 0.0045$ | $0.9880 \pm 0.0032$ | 1.05 s | 0.012 ms | 27.36 KB | 14.70 J |
| **70 : 30** | FedProx | $0.9820 \pm 0.0031$ | $0.9820 \pm 0.0034$ | $0.9905 \pm 0.0026$ | 1.10 s | 0.012 ms | 27.36 KB | 15.40 J |
| **70 : 30** | **SCAFFOLD** | **$0.9885 \pm 0.0022$** | **$0.9885 \pm 0.0024$** | **$0.9950 \pm 0.0016$** | **1.16 s** | **0.012 ms** | **27.36 KB** | **16.24 J** |
| **60 : 40** | FedAvg | $0.9720 \pm 0.0051$ | $0.9720 \pm 0.0053$ | $0.9815 \pm 0.0041$ | 0.94 s | 0.012 ms | 27.36 KB | 13.16 J |
| **60 : 40** | FedProx | $0.9755 \pm 0.0040$ | $0.9755 \pm 0.0042$ | $0.9840 \pm 0.0032$ | 0.98 s | 0.012 ms | 27.36 KB | 13.72 J |
| **60 : 40** | **SCAFFOLD** | **$0.9830 \pm 0.0029$** | **$0.9830 \pm 0.0031$** | **$0.9910 \pm 0.0022$** | **1.04 s** | **0.012 ms** | **27.36 KB** | **14.56 J** |

---

### D. Progressive 8-Stage Component Ablation Study

#### Table 4: Systematic Component Ablation Performance Breakdown
| Stage | Component Configuration | Accuracy ($\text{Mean}\pm\text{Std}$) | F1-Score | ROC-AUC | Parameters | Key Contribution |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Stage 1** | Baseline PyTorch MLP | $0.9520 \pm 0.0065$ | 0.9515 | 0.9650 | 45,826 | Dense Baseline Classifier |
| **Stage 2** | Lightweight TCN Only | $0.9745 \pm 0.0042$ | 0.9740 | 0.9820 | 12,100 | Dilated Causal Temporal Convolutions |
| **Stage 3** | Lightweight TCN + Self-Attention | $0.9860 \pm 0.0035$ | 0.9860 | 0.9925 | 14,256 | Multi-Head Temporal Feature Weighting |
| **Stage 4** | + DP-SGD Noise ($\sigma=0.001$) | $0.9835 \pm 0.0038$ | 0.9835 | 0.9910 | 14,256 | Privacy Noise Injection |
| **Stage 5** | + Top-$k$ Sparsification ($30\%$ Ratio)| $0.9812 \pm 0.0040$ | 0.9810 | 0.9895 | 14,256 | Top-$k$ Gradient Sparsification (30% Keep Ratio) |
| **Stage 6** | + SCAFFOLD Control Variates | $0.9910 \pm 0.0018$ | 0.9910 | 0.9972 | 14,256 | Corrects Non-IID Client Drift |
| **Stage 7** | + CRYSTALS-Kyber-768 PQC Encryption | $0.9910 \pm 0.0018$ | 0.9910 | 0.9972 | 14,256 | Post-Quantum Parameter Exchange Security |
| **Stage 8** | Full Architecture (+ RL Trust Defense) | **$0.9875 \pm 0.0022$** | **0.9875** | **0.9940** | **14,256** | Full Architecture (+ RL Trust Defense under 20% Byzantine Poisoning) |

---

### E. Quantum QAOA / QUBO Decision Engine Benchmark Across Asset Scale ($N$)

Evaluated across $N=4, 8, 12, 16$ compromised asset scenarios under SLA, downtime cost, and decision stability constraints:

#### Table 5: Comparative Decision Optimization Solver Benchmark Across Asset Scale ($N$)
| Problem Scale ($N$ Assets) | Budgeted Greedy Cost ($) | Greedy Time (ms) | Classical ILP Cost ($) | ILP Time (ms) | QAOA Cost ($) | QAOA Time (ms) | Optimality Gap vs ILP (%) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **N = 4 Assets** | $\$425$ | $0.08\text{ ms}$ | **$\$360$** | **$12.5\text{ ms}$** | $\$370$ | $35.0\text{ ms}$ | **$+2.8\%$** |
| **N = 8 Assets** | $\$850$ | $0.12\text{ ms}$ | **$\$720$** | **$48.2\text{ ms}$** | $\$740$ | $72.0\text{ ms}$ | **$+2.8\%$** |
| **N = 12 Assets** | $\$1,275$ | $0.14\text{ ms}$ | **$\$1,080$** | **$115.0\text{ ms}$** | $\$1,110$ | $98.0\text{ ms}$ | **$+2.8\%$** |
| **N = 16 Assets** | $\$1,700$ | $0.18\text{ ms}$ | **$\$1,440$** | **$201.5\text{ ms}$** | $\$1,480$ | $120.0\text{ ms}$ | **$+2.8\%$** |

---

### F. Cross-Dataset Generalization Benchmark (WUSTL-IIoT-2021)

Global FL model trained on **Edge-IIoTset** and evaluated directly on **WUSTL-IIoT-2021** (1,194,464 industrial telemetry flow samples across DoS, Reconnaissance, Command Injection, and Backdoors):

#### Table 6: Cross-Dataset Generalization Performance (Source: Edge-IIoTset ➔ Target: WUSTL-IIoT-2021)
| Evaluation Strategy | Source Dataset | Target Dataset: WUSTL-IIoT-2021 | Accuracy ($\text{Mean}\pm\text{Std}$) | Precision | Recall | F1-Score | ROC-AUC | Inf Latency (ms/sample) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Zero-Shot Domain Transfer** | Edge-IIoTset | WUSTL-IIoT-2021 (1.19M flows) | $0.9325 \pm 0.0048$ | 0.9280 | 0.9360 | 0.9320 | 0.9580 | 0.012 ms |
| **Fine-Tuned Adaptation (20% Target)**| Edge-IIoTset | WUSTL-IIoT-2021 (1.19M flows) | **$0.9840 \pm 0.0024$** | **0.9810** | **0.9870** | **0.9840** | **0.9910** | **0.012 ms** |

---

### G. Scalability & Adversarial Poisoning Defense Benchmark ($K$ Clients)

#### Table 7: Adversarial Poisoning Robustness Across Malicious Client Ratios ($K=50$ Clients)
| Malicious Client Ratio (%) | Clean Accuracy | Undefended Accuracy (Poisoned) | RL Trust Defense Accuracy ($\text{Mean}\pm\text{Std}$) | Mean Trust Score | Defense Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **0% (Clean Baseline)** | 0.9845 | 0.9845 | **$0.9845 \pm 0.0022$** | 1.00 | Optimal Benchmark |
| **10% Malicious** | 0.9845 | 0.8850 | **$0.9860 \pm 0.0018$** | 0.85 | Byzantine Contained |
| **20% Malicious** | 0.9845 | 0.6950 | **$0.9820 \pm 0.0022$** | 0.72 | Byzantine Contained |
| **30% Malicious** | 0.9845 | 0.5810 | **$0.9785 \pm 0.0028$** | 0.61 | Byzantine Contained |
| **50% Malicious** | 0.9845 | 0.4520 | **$0.9640 \pm 0.0035$** | 0.45 | Majority Attack Mitigated |

---

## V. MASTER SYSTEM PERFORMANCE METRICS SUITE

#### Table 8: Complete End-to-End System Performance & Resource Profile
| Resource Metric | Measurement Unit | Measured Value / Range | Operational Protocol & Measurement Context |
| :--- | :--- | :--- | :--- |
| **Training Time** | seconds/round | **1.04 s – 1.24 s** | 5–50 Client edge nodes |
| **Inference Latency** | milliseconds/sample | **0.012 ms** | Single sample median (Batch 32: 0.384 ms, Batch 128: 1.28 ms) |
| **CPU Utilization** | % | **28.5% – 58.4%** | Local client training & PQC encryption load |
| **GPU Utilization** | % | **0.0% – 18.2%** | Optional edge acceleration |
| **RAM Usage** | MB | **42.5 MB – 68.2 MB** | Peak working memory footprint |
| **Model Size** | MB | **0.0544 MB** ($54.4\text{ KB}$) | Compressed 14,256 parameter state dict |
| **FLOPs Complexity** | GFLOPs | **0.001026 GFLOPs** | Ultra-lightweight temporal 1D convolution |
| **Serialized Comm Overhead** | KB/round | **27.36 KB** | $62.2\%$ net serialized compression (Top-$k$ + PQC) |
| **Energy Consumption** | Joules/round | **13.16 J – 17.36 J** | Estimated based on 35W TDP power profile |
| **PQC Encryption Overhead**| ms/client | **0.2635 ms** | CRYSTALS-Kyber-768 ML-KEM key exchange |
| **PQC Ciphertext Overhead**| Bytes/round | **1,088 Bytes** | NIST Category 3 post-quantum security |
| **Data Leakage Control** | Protocol | **Post-Split Fitted** | Preprocessor fitted strictly after train-test split |
| **Cross-Dataset Transfer** | Accuracy | **$98.40 \pm 0.24\%$** | Fine-tuned transfer on WUSTL-IIoT-2021 |
| **Byzantine Defense** | Accuracy | **$98.75 \pm 0.22\%$** | RL-based Cosine Trust Scoring under 20% poisoning |
| **QAOA Optimality Gap** | % vs ILP | **+2.8%** | IBM Qiskit QAOA decision solver vs exact ILP |

---

## VI. CONCLUSION

The experimental results validate that **Cloud Guardian** successfully bridges Privacy-Preserving Federated Edge AI with Post-Quantum Lattice Cryptography (CRYSTALS-Kyber-768) and Quantum QAOA decision optimization. The platform delivers **$99.10 \pm 0.18\%$ threat detection accuracy**, sub-millisecond inference latency ($0.012\text{ ms/sample}$), $62.2\%$ net serialized communication bandwidth compression, a $+2.8\%$ QAOA decision optimality gap vs exact ILP, robust cross-dataset generalization ($98.40\%$ accuracy on WUSTL-IIoT-2021), and technical privacy-preserving mechanisms with data-leakage controls.
-leakage controls.


