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
