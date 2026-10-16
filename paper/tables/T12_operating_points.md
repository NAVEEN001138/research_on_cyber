**Table 12.** Operating points and threshold calibration under class imbalance (Edge-IIoTset Random Split) — *provenance: measured; carved 20% validation split for calibration*

| Algorithm | Operating Point | Normal Recall | Attack Recall | FPR | Precision | Macro-F1 | MCC | ROC-AUC |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| FedAvg (Adam) | Max Macro-F1 | 0.4025 | 0.9850 | 0.5975 | 0.8983 | 0.7412 | 0.5324 | 0.8705 |
| FedAvg (Adam) | FPR ≤ 5% | 0.9936 | 0.3881 | 0.0064 | 0.9970 | 0.4678 | 0.2960 | 0.8705 |
| FedAvg (SGD) | Max Macro-F1 | 0.2903 | 0.9917 | 0.7097 | 0.8821 | 0.6843 | 0.4596 | 0.8145 |
| FedAvg (SGD) | FPR ≤ 5% (unreachable; min FPR=0.0822) | 0.9407 | 0.3849 | 0.0593 | 0.9720 | 0.4554 | 0.2514 | 0.8145 |
| FedProx (SGD) | Max Macro-F1 | 0.2903 | 0.9917 | 0.7097 | 0.8821 | 0.6843 | 0.4596 | 0.8145 |
| FedProx (SGD) | FPR ≤ 5% (unreachable; min FPR=0.0822) | 0.9407 | 0.3849 | 0.0593 | 0.9720 | 0.4554 | 0.2514 | 0.8145 |
| SCAFFOLD (SGD) | Max Macro-F1 | 0.4004 | 0.9850 | 0.5996 | 0.8979 | 0.7401 | 0.5306 | 0.8581 |
| SCAFFOLD (SGD) | FPR ≤ 5% | 0.9619 | 0.4759 | 0.0381 | 0.9853 | 0.5226 | 0.3244 | 0.8581 |
| FedAvg (Class-Weighted) | Max Macro-F1 | 0.4025 | 0.9850 | 0.5975 | 0.8983 | 0.7412 | 0.5324 | 0.8673 |
| FedAvg (Class-Weighted) | FPR ≤ 5% | 0.9936 | 0.4260 | 0.0064 | 0.9972 | 0.4946 | 0.3184 | 0.8673 |
