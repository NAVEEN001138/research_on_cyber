**Table 10.** Systematic Data Leakage Ablation across Feature Configurations — *provenance: measured*

| Split | Model | Feature Configuration | Features Count | Accuracy | Macro-F1 | ROC-AUC | PR-AUC | MCC |
|---|---|---|---:|---:|---:|---:|---:|---:|
| random | Centralized | Full (19 semantic + 17 identifiers) | 36 | 0.9469 ± 0.0034 | 0.8976 ± 0.0050 | 0.9835 ± 0.0021 | 0.9969 ± 0.0004 | 0.7976 ± 0.0098 |
| random | Centralized | Minus IPs / Ports | 33 | 0.9137 ± 0.0011 | 0.7986 ± 0.0037 | 0.9234 ± 0.0040 | 0.9847 ± 0.0009 | 0.6364 ± 0.0053 |
| random | Centralized | Minus Seq / Ack numbers | 32 | 0.9375 ± 0.0129 | 0.8768 ± 0.0193 | 0.9761 ± 0.0052 | 0.9955 ± 0.0010 | 0.7576 ± 0.0402 |
| random | Centralized | Minus Stream / Checksum | 33 | 0.9466 ± 0.0052 | 0.8942 ± 0.0149 | 0.9852 ± 0.0014 | 0.9972 ± 0.0003 | 0.7917 ± 0.0249 |
| random | Centralized | All Identifiers Removed (19 Semantic) | 19 | 0.8924 ± 0.0019 | 0.7379 ± 0.0073 | 0.8840 ± 0.0020 | 0.9691 ± 0.0004 | 0.5272 ± 0.0109 |
| random | Centralized | Identifiers Only (17 features) | 17 | 0.8935 ± 0.0046 | 0.7570 ± 0.0315 | 0.9349 ± 0.0081 | 0.9875 ± 0.0016 | 0.5456 ± 0.0373 |
| random | FedAvg | Full (19 semantic + 17 identifiers) | 36 | 0.9125 ± 0.0114 | 0.7853 ± 0.0390 | 0.9598 ± 0.0082 | 0.9912 ± 0.0024 | 0.6309 ± 0.0558 |
| random | FedAvg | Minus IPs / Ports | 33 | 0.8973 ± 0.0075 | 0.7307 ± 0.0326 | 0.9080 ± 0.0094 | 0.9803 ± 0.0026 | 0.5546 ± 0.0375 |
| random | FedAvg | Minus Seq / Ack numbers | 32 | 0.9071 ± 0.0143 | 0.7667 ± 0.0550 | 0.9526 ± 0.0085 | 0.9901 ± 0.0026 | 0.6021 ± 0.0748 |
| random | FedAvg | Minus Stream / Checksum | 33 | 0.9146 ± 0.0117 | 0.7950 ± 0.0455 | 0.9628 ± 0.0070 | 0.9920 ± 0.0021 | 0.6415 ± 0.0586 |
| random | FedAvg | All Identifiers Removed (19 Semantic) | 19 | 0.8780 ± 0.0055 | 0.6574 ± 0.0357 | 0.8730 ± 0.0085 | 0.9658 ± 0.0018 | 0.4402 ± 0.0328 |
| random | FedAvg | Identifiers Only (17 features) | 17 | 0.8701 ± 0.0106 | 0.6176 ± 0.0563 | 0.8944 ± 0.0161 | 0.9780 ± 0.0037 | 0.3811 ± 0.0740 |
| session-disjoint | Centralized | Full (19 semantic + 17 identifiers) | 36 | 0.8915 ± 0.0292 | 0.7987 ± 0.0627 | 0.7709 ± 0.1183 | 0.8908 ± 0.0582 | 0.6312 ± 0.1069 |
| session-disjoint | Centralized | Minus IPs / Ports | 33 | 0.9113 ± 0.0002 | 0.8406 ± 0.0004 | 0.9339 ± 0.0036 | 0.9803 ± 0.0011 | 0.7073 ± 0.0006 |
| session-disjoint | Centralized | Minus Seq / Ack numbers | 32 | 0.8925 ± 0.0316 | 0.8077 ± 0.0582 | 0.9307 ± 0.0138 | 0.9807 ± 0.0036 | 0.6405 ± 0.1102 |
| session-disjoint | Centralized | Minus Stream / Checksum | 33 | 0.8763 ± 0.0104 | 0.7639 ± 0.0186 | 0.7112 ± 0.0372 | 0.8542 ± 0.0202 | 0.5751 ± 0.0418 |
| session-disjoint | Centralized | All Identifiers Removed (19 Semantic) | 19 | 0.8318 ± 0.0000 | 0.6216 ± 0.0000 | 0.6971 ± 0.0261 | 0.8947 ± 0.0151 | 0.3669 ± 0.0000 |
| session-disjoint | Centralized | Identifiers Only (17 features) | 17 | 0.8583 ± 0.0070 | 0.7251 ± 0.0256 | 0.6595 ± 0.0041 | 0.8290 ± 0.0016 | 0.5004 ± 0.0328 |
| session-disjoint | FedAvg | Full (19 semantic + 17 identifiers) | 36 | 0.8576 ± 0.0384 | 0.6806 ± 0.1091 | 0.6789 ± 0.1690 | 0.8202 ± 0.0986 | 0.4858 ± 0.1583 |
| session-disjoint | FedAvg | Minus IPs / Ports | 33 | 0.8586 ± 0.0399 | 0.6903 ± 0.1193 | 0.6806 ± 0.2030 | 0.8362 ± 0.1219 | 0.4836 ± 0.1735 |
| session-disjoint | FedAvg | Minus Seq / Ack numbers | 32 | 0.8453 ± 0.0113 | 0.6527 ± 0.0448 | 0.8242 ± 0.0616 | 0.9443 ± 0.0266 | 0.4391 ± 0.0573 |
| session-disjoint | FedAvg | Minus Stream / Checksum | 33 | 0.8905 ± 0.0469 | 0.7698 ± 0.1315 | 0.8170 ± 0.2172 | 0.8979 ± 0.1281 | 0.6186 ± 0.1902 |
| session-disjoint | FedAvg | All Identifiers Removed (19 Semantic) | 19 | 0.8306 ± 0.0028 | 0.6119 ± 0.0216 | 0.6581 ± 0.0302 | 0.8689 ± 0.0174 | 0.3612 ± 0.0127 |
| session-disjoint | FedAvg | Identifiers Only (17 features) | 17 | 0.8034 ± 0.0051 | 0.4837 ± 0.0341 | 0.5661 ± 0.0272 | 0.7663 ± 0.0167 | 0.1309 ± 0.0868 |

**Top 15 Feature Importances (Random Forest on Full 36 Features):**
1. `tcp.dstport`: 0.2487
2. `tcp.srcport`: 0.2119
3. `tcp.seq`: 0.1530
4. `tcp.ack`: 0.0720
5. `tcp.flags`: 0.0575
6. `mqtt.msgtype`: 0.0547
7. `mqtt.hdrflags`: 0.0506
8. `tcp.len`: 0.0340
9. `mqtt.len`: 0.0339
10. `tcp.ack_raw`: 0.0222
11. `tcp.checksum`: 0.0118
12. `tcp.connection.rst`: 0.0116
13. `tcp.flags.ack`: 0.0096
14. `tcp.connection.synack`: 0.0046
15. `tcp.connection.syn`: 0.0042
