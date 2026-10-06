**Table 10.** Data leakage analysis: Protocol-semantic features (19) vs. Semantic + session identifiers (36) — *provenance: measured*

| Split | Model | Feature Set | Dim | Accuracy | Macro-F1 | ROC-AUC | PR-AUC | MCC |
|---|---|---|---:|---:|---:|---:|---:|---:|
| random | Centralized | Semantic (protocol-only) | 19 | 0.8909 ± 0.0035 | 0.7409 ± 0.0029 | 0.8822 ± 0.0042 | 0.9685 ± 0.0009 | 0.5243 ± 0.0103 |
| random | Centralized | Semantic + Session Identifiers | 36 | 0.9815 ± 0.0172 | 0.9623 ± 0.0375 | 0.9942 ± 0.0040 | 0.9986 ± 0.0009 | 0.9282 ± 0.0684 |
| random | FedAvg | Semantic (protocol-only) | 19 | 0.7948 ± 0.1803 | 0.6095 ± 0.0887 | 0.8164 ± 0.0143 | 0.9522 ± 0.0038 | 0.3883 ± 0.0790 |
| random | FedAvg | Semantic + Session Identifiers | 36 | 0.7682 ± 0.2127 | 0.5797 ± 0.1106 | 0.7396 ± 0.0296 | 0.9366 ± 0.0081 | 0.3218 ± 0.0554 |
| temporal | Centralized | Semantic (protocol-only) | 19 | 0.8957 ± 0.0034 | 0.7342 ± 0.0205 | 0.8766 ± 0.0003 | 0.9696 ± 0.0003 | 0.5138 ± 0.0242 |
| temporal | Centralized | Semantic + Session Identifiers | 36 | 0.9901 ± 0.0058 | 0.9800 ± 0.0120 | 0.9971 ± 0.0016 | 0.9990 ± 0.0010 | 0.9603 ± 0.0236 |
| temporal | FedAvg | Semantic (protocol-only) | 19 | 0.7965 ± 0.1328 | 0.6312 ± 0.0498 | 0.8149 ± 0.0315 | 0.9552 ± 0.0072 | 0.4133 ± 0.0499 |
| temporal | FedAvg | Semantic + Session Identifiers | 36 | 0.7443 ± 0.1735 | 0.5528 ± 0.0531 | 0.7922 ± 0.0533 | 0.9541 ± 0.0135 | 0.2911 ± 0.0541 |

**Top 15 Feature Importances (Random Forest on Semantic + Identifiers):**
1. `tcp.dstport`: 0.2656
2. `tcp.srcport`: 0.2067
3. `tcp.seq`: 0.1495
4. `tcp.ack`: 0.0709
5. `tcp.flags`: 0.0590
6. `mqtt.msgtype`: 0.0512
7. `mqtt.hdrflags`: 0.0488
8. `tcp.len`: 0.0359
9. `mqtt.len`: 0.0310
10. `tcp.ack_raw`: 0.0221
11. `tcp.checksum`: 0.0117
12. `tcp.connection.rst`: 0.0109
13. `tcp.flags.ack`: 0.0088
14. `tcp.connection.syn`: 0.0044
15. `tcp.connection.synack`: 0.0043
