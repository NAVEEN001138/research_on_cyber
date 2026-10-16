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
| session-disjoint | Centralized | Full (19 semantic + 17 identifiers) | 36 | 0.9200 ± 0.0435 | 0.8377 ± 0.0626 | 0.9170 ± 0.1166 | 0.9619 ± 0.0681 | 0.6906 ± 0.1066 |
| session-disjoint | Centralized | Minus IPs / Ports | 33 | 0.8873 ± 0.0408 | 0.7156 ± 0.0476 | 0.8324 ± 0.1349 | 0.9357 ± 0.0950 | 0.5059 ± 0.0649 |
| session-disjoint | Centralized | Minus Seq / Ack numbers | 32 | 0.9045 ± 0.0481 | 0.8137 ± 0.0664 | 0.9281 ± 0.0893 | 0.9710 ± 0.0504 | 0.6472 ± 0.1174 |
| session-disjoint | Centralized | Minus Stream / Checksum | 33 | 0.9214 ± 0.0434 | 0.8420 ± 0.0605 | 0.9089 ± 0.1302 | 0.9556 ± 0.0802 | 0.6954 ± 0.1090 |
| session-disjoint | Centralized | All Identifiers Removed (19 Semantic) | 19 | 0.8822 ± 0.0379 | 0.7076 ± 0.0444 | 0.8318 ± 0.1205 | 0.9323 ± 0.0862 | 0.4778 ± 0.0532 |
| session-disjoint | Centralized | Identifiers Only (17 features) | 17 | 0.8536 ± 0.0260 | 0.6706 ± 0.0419 | 0.8362 ± 0.1040 | 0.9422 ± 0.0785 | 0.3714 ± 0.0950 |
| session-disjoint | FedAvg | Full (19 semantic + 17 identifiers) | 36 | 0.8928 ± 0.0435 | 0.7276 ± 0.0684 | 0.8773 ± 0.1489 | 0.9408 ± 0.1028 | 0.5390 ± 0.0927 |
| session-disjoint | FedAvg | Minus IPs / Ports | 33 | 0.8804 ± 0.0409 | 0.6726 ± 0.0515 | 0.8219 ± 0.1473 | 0.9273 ± 0.1097 | 0.4651 ± 0.0610 |
| session-disjoint | FedAvg | Minus Seq / Ack numbers | 32 | 0.8953 ± 0.0428 | 0.7349 ± 0.0695 | 0.9180 ± 0.0671 | 0.9768 ± 0.0291 | 0.5502 ± 0.0973 |
| session-disjoint | FedAvg | Minus Stream / Checksum | 33 | 0.8916 ± 0.0417 | 0.7221 ± 0.0612 | 0.8761 ± 0.1544 | 0.9378 ± 0.1086 | 0.5308 ± 0.0819 |
| session-disjoint | FedAvg | All Identifiers Removed (19 Semantic) | 19 | 0.8776 ± 0.0400 | 0.6692 ± 0.0534 | 0.8328 ± 0.1083 | 0.9417 ± 0.0646 | 0.4476 ± 0.0609 |
| session-disjoint | FedAvg | Identifiers Only (17 features) | 17 | 0.8460 ± 0.0410 | 0.5067 ± 0.0620 | 0.8014 ± 0.1268 | 0.9281 ± 0.0989 | 0.1160 ± 0.1299 |

**Top 15 Feature Importances (Random Forest on Full 36 Features):**
1. `tcp.dstport`: 0.2618
2. `tcp.srcport`: 0.2065
3. `tcp.seq`: 0.1527
4. `tcp.ack`: 0.0723
5. `tcp.flags`: 0.0560
6. `mqtt.msgtype`: 0.0523
7. `mqtt.hdrflags`: 0.0497
8. `tcp.len`: 0.0369
9. `mqtt.len`: 0.0319
10. `tcp.ack_raw`: 0.0222
11. `tcp.checksum`: 0.0110
12. `tcp.connection.rst`: 0.0104
13. `tcp.flags.ack`: 0.0083
14. `tcp.connection.syn`: 0.0044
15. `tcp.connection.synack`: 0.0041
