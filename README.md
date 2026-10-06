# 🛡️ Cloud Guardian: Quantum-Resilient Privacy-Preserving Federated Edge Learning & Incident Response

> **Empirical Ground-Truth Reproduction & Research Artifacts**  
> **System Status**: Verified 9-Layer Architecture, Multi-Seed FL Pipeline, NIST FIPS-203 ML-KEM-768 Post-Quantum Key Establishment & AES-256-GCM Payload Encryption.

---

## 📌 Executive Overview

**Cloud Guardian** is a 9-layer security and decision framework designed for industrial Internet of Things (IIoT) and cyber-physical systems (CPS). It couples decentralized federated threat detection with combinatorial incident response under post-quantum cryptographic security models.

### Key Architectural Components:
- **Layer 2 (Federated Edge Threat Detection)**: Evaluates Multi-Layer Perceptrons (MLP) and 1-D convolutional feature encoders with multi-head self-attention trained via **FedAvg (Adam)**, **FedAvg (SGD)**, **FedProx (SGD)**, and **SCAFFOLD (SGD)** across non-IID Dirichlet partitions on **Edge-IIoTset**, with cross-dataset transfer evaluated on **WUSTL-IIoT-2021**.
- **Post-Quantum Security & Privacy Wrapper**: Combines **Top-$k$ update sparsification** with client residual accumulation, and **NIST FIPS-203 ML-KEM-768** key encapsulation with HKDF-SHA256 and authenticated AES-256-GCM payload encryption.
- **Byzantine Robustness**: Benchmarks coordinate-wise Median, Trimmed Mean, Multi-Krum, and norm-bounded Cosine Trust scoring against simultaneous label-flip and scaled sign-flip model replacement attacks.
- **Layer 5 & 6 (Adaptive Constraints & Combinatorial Optimization)**: Formulates incident-response allocation as an exact Integer Linear Program (ILP via PuLP CBC) and as a QUBO solved via QAOA statevector simulation.

---

## 📄 Research Manuscript & Empirical Tables

All empirical results, methodology, threat models, and comprehensive analyses are documented in:
- **Research Manuscript**: [`RESEARCH_PAPER_IEEE.md`](RESEARCH_PAPER_IEEE.md)  
  *Title: "How Much of Edge-IIoTset Is Leakage? An Honest Baseline for Quantum-Resistant Federated Intrusion Detection in IIoT"*
- **All Empirical Tables**: [`paper/tables/ALL_TABLES.md`](paper/tables/ALL_TABLES.md)  
  *Contains Tables 1 through 10 generated directly from the automated results repository.*

---

## ⚡ Reproduction Commands

To reproduce the experiments from scratch, execute each phase independently using Python in the project virtual environment.  
**Critical Execution Constraint**: Run strictly **one phase at a time** (sequential execution) to prevent system memory crashes. Execute the `resources` phase last, as it derives energy metrics from the measured federated round time.

### 1. Execute Benchmark Phases Sequentially
```bash
# 1. Federated Learning Benchmark (Random & Temporal splits across seeds)
python run_experiments.py --phase fl

# 2. Systematic Component Ablation (Stages 1 through 8, including Stage 6b)
python run_experiments.py --phase ablation

# 3. Byzantine Poisoning Robustness (Median, Trimmed Mean, Krum, Trust)
python run_experiments.py --phase poison

# 4. Cross-Dataset Transfer Benchmark (Edge-IIoTset -> WUSTL-IIoT-2021)
python run_experiments.py --phase transfer

# 5. Quantum Optimization Benchmark (QAOA statevector simulator vs. exact ILP)
python run_experiments.py --phase qaoa

# 6. Data Leakage Experiment (Semantic vs. Semantic + Identifiers across splits)
python run_experiments.py --phase leakage

# 7. Communication Payload Measurement (Top-k sparse weights + SCAFFOLD control variates)
python run_experiments.py --phase payload

# 8. Resource Profiling (Single-sample inference latency, memory, energy derivation)
python run_experiments.py --phase resources
```

*Every phase stores its results in `results/phases/<phase>.json` and automatically rebuilds the single source of truth at `results/RESULTS.json`.*

### 2. Table Generation, Manuscript Build & Automated Verification
```bash
# Generate Markdown tables from results/RESULTS.json
python generate_paper_tables.py

# Validate placeholder paths in paper template (dry run)
python build_paper.py --dry-run

# Render the final IEEE manuscript from template and results
python build_paper.py

# Verify that every numeric token in tables and prose is traceable
python check_paper_numbers.py

# Run unit and integration test suite
python -m pytest tests -q
```

---

## 🏗️ 9-Layer System Architecture

```text
Layer 0 — Preprocessing & Variance Thresholding (preprocessor.py)
   ↓
Layer 1 — Telemetry Ingestion & Protocol Extraction (data_loader.py)
   ↓
Layer 2 — Federated ML Threat Detection (federated_detector.py / scaffold_fl.py)
   ↓
Layer 3 — Context Aggregation & SLA Tracking (context_aggregator.py)
   ↓
Layer 4 — Confidence Evaluation & Action Gating (confidence_evaluator.py)
   ↓
Layer 5 — Adaptive Constraint Synthesizer (adaptive_constraints.py)
   ↓
Layer 6 — Decision Optimization Engine: ILP / QUBO / QAOA (decision_engine.py / baseline_greedy.py)
   ↓
Layer 7 — Multi-Attribute Response Utility Model (response_utility.py)
   ↓
Layer 8 — Execution & Role-Based Rationale Disclosure (explainability.py / executor.py)
   ↓
Layer 9 — EMA Post-Incident Feedback Learning (feedback_learner.py)
```

---

## 📁 Repository Structure

```text
quantum-cloud-ir/
├── layer0_preprocessing/       # Preprocessing, standard scaling, variance thresholding
├── layer1_telemetry/           # Telemetry loaders, dataset ingestion, WUSTL semantic map
├── layer2_detection/           # MLP / TCN architectures, SCAFFOLD, PQC ML-KEM-768, trust scorer
├── layer3_context/             # Context aggregator (C-I-A, SLA, velocity)
├── layer4_confidence/          # Confidence tiering & allowed action gating
├── layer5_constraints/         # Adaptive constraint synthesizer
├── layer6_optimization/        # QUBO formulation, QAOA quantum & PuLP ILP solvers
├── layer7_utility/             # Multi-attribute response utility model
├── layer8_orchestration/       # Execution logging & RBAC explainability
├── layer9_feedback/            # Feedback learning engine
├── attacks/                    # Adversarial attacks (label-flip, sign-flip model replacement)
├── utils/                      # Seeding, environment capture, dataset integrity, metrics
├── results/                    # Single source of truth (RESULTS.json, phases/, environment.json)
├── paper/                      # PAPER_TEMPLATE.md, prose_constants.json, paper/tables/*.md
├── tests/                      # Verification test suite (PQC, Top-k bytes, trust wiring)
├── run_experiments.py          # Canonical experiment driver
├── generate_paper_tables.py    # Paper table generator
├── build_paper.py              # Template renderer
├── check_paper_numbers.py      # Automated table and prose verification
├── verify_system.py            # Behavioral 10/10 system verification suite
├── DATASETS.md                 # Dataset provenance, URLs, and SHA-256 checksums
├── CHANGELOG_AUDIT.md          # Comprehensive audit resolution log
├── RESEARCH_PAPER_IEEE.md      # Rendered IEEE research manuscript
├── requirements.txt            # Pinned dependency specifications
└── README.md                   # Primary documentation
```