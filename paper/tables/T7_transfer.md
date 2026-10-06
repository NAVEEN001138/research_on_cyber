**Table 7.** Cross-dataset transfer Edge-IIoTset → WUSTL-IIoT-2021 — *provenance: measured; 3 semantically shared features (tcp.len, http.content_length, tcp.connection.synack); 50,000 of 1,194,464 target flows; source model centrally trained on the shared-feature subset (not the FL checkpoint)*

| Setting | Accuracy | Macro-F1 | ROC-AUC | PR-AUC |
|---|---:|---:|---:|---:|
| Zero-shot (source scaler, no target labels) | 0.0717 ± 0.0000 | 0.0669 ± 0.0000 | 0.2595 ± 0.1345 | 0.1620 ± 0.0907 |
| Fine-tuned on 20 % of target | 0.7781 ± 0.3955 | 0.6010 ± 0.3552 | 0.8894 ± 0.2177 | 0.6606 ± 0.3302 |
| From scratch on the same 20 % of target | 0.9378 ± 0.0213 | 0.5695 ± 0.1969 | 0.9854 ± 0.0031 | 0.7668 ± 0.0686 |

Edge-IIoTset is packet-level; WUSTL-IIoT-2021 is flow-level. Only 3 semantically shared features exist; zero-shot transfer is reported as a negative result.
