**Table 7.** Cross-dataset transfer Edge-IIoTset → WUSTL-IIoT-2021 — *provenance: measured; 3 semantically shared features (tcp.len, http.content_length, tcp.connection.synack); 50,000 of 1,194,464 target flows; source model centrally trained on the shared-feature subset (not the FL checkpoint)*

| Setting | Accuracy | Macro-F1 | ROC-AUC | PR-AUC |
|---|---:|---:|---:|---:|
| Zero-shot (source scaler, no target labels) | 0.0717 ± 0.0001 | 0.0669 ± 0.0001 | 0.6602 ± 0.3625 | 0.4053 ± 0.3634 |
| Fine-tuned on 20 % of target | 0.5857 ± 0.4692 | 0.3158 ± 0.2272 | 0.6945 ± 0.2666 | 0.3612 ± 0.3965 |
| From scratch on the same 20 % of target | 0.9276 ± 0.0016 | 0.4831 ± 0.0016 | 0.8389 ± 0.3278 | 0.6307 ± 0.2641 |

Edge-IIoTset is packet-level; WUSTL-IIoT-2021 is flow-level. Only 3 semantically shared features exist; zero-shot transfer is reported as a negative result.
