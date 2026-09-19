# Dataset Provenance & Integrity Specifications

This document outlines the official provenance, source repositories, cryptographic SHA-256 checksums, expected byte sizes, and directory layout for all empirical benchmarks in the Cloud Guardian evaluation framework.

---

## 1. Primary Datasets

### A. Edge-IIoTset Cyber Security Dataset (IoT & IIoT)
- **Authors**: Mohamed Amine Ferrag, Leandros Maglaras, et al.
- **Reference**: M. A. Ferrag et al., *"Edge-IIoTset: A New Comprehensive Realistic Cyber Security Dataset of IoT and IIoT Applications for Centralized and Federated Learning,"* IEEE Access, vol. 10, pp. 40281–40306, 2022. DOI: `10.1109/ACCESS.2022.3165809`.
- **Download Source**: [Kaggle Dataset Repository](https://www.kaggle.com/datasets/mohamedamineferrag/edgeiiotset-cyber-security-dataset-of-iot-iiot)
- **Primary Canonical Evaluation File**: `Selected dataset for ML and DL/ML-EdgeIIoT-dataset.csv`
  - **Expected Size**: `82,184,390 bytes` (78.38 MB)
  - **SHA-256 Checksum**: `53101fad091af20bee815860962a5016b802ee45d456a141042f6183094c3c1a`
  - **Rows**: 157,800
  - **Columns**: 63 (including protocol features, Attack_label, Attack_type)
- **Full DNN Variant**: `Selected dataset for ML and DL/DNN-EdgeIIoT-dataset.csv`
  - **Expected Size**: `1,217,413,981 bytes` (1.13 GB)
  - **SHA-256 Checksum**: `1d3ef6c7cc22784a528a117f1158f5cad750273679437e18a39c360ee6b79fd7`
  - **Rows**: 2,219,201

### B. WUSTL-IIoT-2021 Dataset
- **Authors**: Mansoor Zolanvari, M. Ali Teixeira, Raj Jain, et al.
- **Reference**: M. Zolanvari et al., *"Machine Learning-Based Network Vulnerability Analysis of Industrial Internet of Things,"* IEEE Internet of Things Journal, vol. 6, no. 4, pp. 6822–6834, 2019.
- **Download Source**: [Washington University in St. Louis IIoT Dataset Archive](https://www.cse.wustl.edu/~jain/iiot2/index.html)
- **File**: `wustl_iiot_2021/wustl_iiot_2021.csv`
  - **Expected Size**: `409,800,698 bytes` (390.82 MB)
  - **SHA-256 Checksum**: `f897b24578cc6fdeb3e7a0e9ff63efd5bbdc926a545abbda725e0dbb348c6bca`
  - **Rows**: 1,194,764
  - **Columns**: 49

---

## 2. Directory Layout Requirements

The automated data loaders expect the following structure under the repository root:

```text
quantum-cloud-ir/
└── datasets/
    ├── edge iot dataset/
    │   ├── Selected dataset for ML and DL/
    │   │   ├── ML-EdgeIIoT-dataset.csv
    │   │   └── DNN-EdgeIIoT-dataset.csv
    │   ├── Attack traffic/
    │   └── Normal traffic/
    └── wustl_iiot_2021/
        └── wustl_iiot_2021.csv
```

---

## 3. Automated Integrity Verification

On first invocation of `load_edge_iiot_dataset()` or `load_wustl_iiot_dataset()`, the pipeline verifies the SHA-256 checksums against the reference hashes above. Once verified, the verification status is cached in `datasets/.hashes_verified.json`. If a hash mismatch or missing file is encountered, the loader immediately raises a `FileNotFoundError` or `ValueError` pointing to this document.
