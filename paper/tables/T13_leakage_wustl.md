**Table 13.** Systematic Data Leakage, Chronological Generalization, and Identifier-Shortcut Audit on WUSTL-IIoT-2021 — *provenance: measured; full dataset: 1,194,464 rows; evaluation sample: 15,000 flows*

### Part 1: Leakage and Shortcut Feature Group Ablation Across Three Evaluation Splits

| Split | Model | Feature Configuration | Features Count | Accuracy | Macro-F1 | ROC-AUC | PR-AUC | MCC |
|---|---|---|---:|---:|---:|---:|---:|---:|
| random | Centralized MLP | Full (all groups + semantic) | 54 | 0.9995 ± 0.0002 | 0.9983 ± 0.0007 | 0.9988 ± 0.0019 | 0.9901 ± 0.0040 | 0.9966 ± 0.0013 |
| random | Centralized MLP | Minus G1 (hosts/ports: SrcAddr, DstAddr, Sport, Dport) | 50 | 0.9991 ± 0.0003 | 0.9966 ± 0.0010 | 0.9989 ± 0.0020 | 0.9950 ± 0.0049 | 0.9931 ± 0.0020 |
| random | Centralized MLP | Minus G2 (IP-ID counters: sIpId, dIpId) | 52 | 0.9995 ± 0.0003 | 0.9980 ± 0.0011 | 0.9988 ± 0.0019 | 0.9867 ± 0.0118 | 0.9961 ± 0.0022 |
| random | Centralized MLP | Minus G3 (timestamps: StartTime, LastTime) | 52 | 0.9995 ± 0.0002 | 0.9983 ± 0.0007 | 0.9989 ± 0.0019 | 0.9922 ± 0.0091 | 0.9966 ± 0.0013 |
| random | Centralized MLP | Minus G4 (host fingerprints: sTtl, dTtl, sTos) | 51 | 0.9997 ± 0.0002 | 0.9988 ± 0.0009 | 0.9989 ± 0.0019 | 0.9917 ± 0.0060 | 0.9975 ± 0.0017 |
| random | Centralized MLP | Semantic only (36 flow statistics + one-hot Proto) | 43 | 0.9960 ± 0.0011 | 0.9855 ± 0.0040 | 0.9985 ± 0.0018 | 0.9839 ± 0.0166 | 0.9712 ± 0.0079 |
| random | Centralized MLP | Identifiers only (G1–G4) | 11 | 0.9993 ± 0.0005 | 0.9975 ± 0.0020 | 0.9998 ± 0.0001 | 0.9963 ± 0.0038 | 0.9951 ± 0.0039 |
| random | FedAvg (Adam) | Full (all groups + semantic) | 54 | 0.9985 ± 0.0007 | 0.9943 ± 0.0026 | 0.9955 ± 0.0061 | 0.9906 ± 0.0044 | 0.9886 ± 0.0052 |
| random | FedAvg (Adam) | Minus G1 (hosts/ports: SrcAddr, DstAddr, Sport, Dport) | 50 | 0.9964 ± 0.0010 | 0.9864 ± 0.0041 | 0.9915 ± 0.0075 | 0.9862 ± 0.0075 | 0.9732 ± 0.0079 |
| random | FedAvg (Adam) | Minus G2 (IP-ID counters: sIpId, dIpId) | 52 | 0.9983 ± 0.0007 | 0.9938 ± 0.0028 | 0.9950 ± 0.0058 | 0.9882 ± 0.0040 | 0.9876 ± 0.0056 |
| random | FedAvg (Adam) | Minus G3 (timestamps: StartTime, LastTime) | 52 | 0.9985 ± 0.0006 | 0.9946 ± 0.0021 | 0.9946 ± 0.0059 | 0.9892 ± 0.0035 | 0.9891 ± 0.0042 |
| random | FedAvg (Adam) | Minus G4 (host fingerprints: sTtl, dTtl, sTos) | 51 | 0.9984 ± 0.0008 | 0.9940 ± 0.0030 | 0.9931 ± 0.0086 | 0.9879 ± 0.0085 | 0.9881 ± 0.0059 |
| random | FedAvg (Adam) | Semantic only (36 flow statistics + one-hot Proto) | 43 | 0.9897 ± 0.0038 | 0.9599 ± 0.0167 | 0.9907 ± 0.0076 | 0.9718 ± 0.0111 | 0.9219 ± 0.0311 |
| random | FedAvg (Adam) | Identifiers only (G1–G4) | 11 | 0.9984 ± 0.0013 | 0.9940 ± 0.0047 | 0.9956 ± 0.0054 | 0.9901 ± 0.0059 | 0.9881 ± 0.0094 |
| session-disjoint | Centralized MLP | Full (all groups + semantic) | 54 | 0.9995 ± 0.0003 | 0.9980 ± 0.0010 | 0.9972 ± 0.0021 | 0.9936 ± 0.0052 | 0.9961 ± 0.0020 |
| session-disjoint | Centralized MLP | Minus G1 (hosts/ports: SrcAddr, DstAddr, Sport, Dport) | 50 | 0.9988 ± 0.0008 | 0.9956 ± 0.0029 | 0.9972 ± 0.0022 | 0.9967 ± 0.0021 | 0.9913 ± 0.0058 |
| session-disjoint | Centralized MLP | Minus G2 (IP-ID counters: sIpId, dIpId) | 52 | 0.9995 ± 0.0002 | 0.9983 ± 0.0007 | 0.9972 ± 0.0021 | 0.9939 ± 0.0040 | 0.9967 ± 0.0014 |
| session-disjoint | Centralized MLP | Minus G3 (timestamps: StartTime, LastTime) | 52 | 0.9992 ± 0.0019 | 0.9972 ± 0.0065 | 0.9972 ± 0.0021 | 0.9939 ± 0.0041 | 0.9944 ± 0.0126 |
| session-disjoint | Centralized MLP | Minus G4 (host fingerprints: sTtl, dTtl, sTos) | 51 | 0.9994 ± 0.0002 | 0.9978 ± 0.0008 | 0.9972 ± 0.0022 | 0.9943 ± 0.0043 | 0.9956 ± 0.0016 |
| session-disjoint | Centralized MLP | Semantic only (36 flow statistics + one-hot Proto) | 43 | 0.9957 ± 0.0013 | 0.9842 ± 0.0047 | 0.9970 ± 0.0021 | 0.9913 ± 0.0063 | 0.9687 ± 0.0093 |
| session-disjoint | Centralized MLP | Identifiers only (G1–G4) | 11 | 0.9992 ± 0.0009 | 0.9973 ± 0.0033 | 0.9997 ± 0.0006 | 0.9915 ± 0.0182 | 0.9946 ± 0.0066 |
| session-disjoint | FedAvg (Adam) | Full (all groups + semantic) | 54 | 0.9983 ± 0.0019 | 0.9937 ± 0.0067 | 0.9961 ± 0.0027 | 0.9924 ± 0.0034 | 0.9875 ± 0.0130 |
| session-disjoint | FedAvg (Adam) | Minus G1 (hosts/ports: SrcAddr, DstAddr, Sport, Dport) | 50 | 0.9963 ± 0.0027 | 0.9863 ± 0.0103 | 0.9947 ± 0.0053 | 0.9882 ± 0.0077 | 0.9731 ± 0.0198 |
| session-disjoint | FedAvg (Adam) | Minus G2 (IP-ID counters: sIpId, dIpId) | 52 | 0.9987 ± 0.0008 | 0.9953 ± 0.0027 | 0.9965 ± 0.0023 | 0.9923 ± 0.0035 | 0.9906 ± 0.0054 |
| session-disjoint | FedAvg (Adam) | Minus G3 (timestamps: StartTime, LastTime) | 52 | 0.9973 ± 0.0030 | 0.9905 ± 0.0105 | 0.9961 ± 0.0021 | 0.9870 ± 0.0228 | 0.9812 ± 0.0204 |
| session-disjoint | FedAvg (Adam) | Minus G4 (host fingerprints: sTtl, dTtl, sTos) | 51 | 0.9988 ± 0.0004 | 0.9955 ± 0.0016 | 0.9959 ± 0.0030 | 0.9922 ± 0.0024 | 0.9910 ± 0.0032 |
| session-disjoint | FedAvg (Adam) | Semantic only (36 flow statistics + one-hot Proto) | 43 | 0.9914 ± 0.0038 | 0.9674 ± 0.0150 | 0.9949 ± 0.0038 | 0.9793 ± 0.0121 | 0.9362 ± 0.0284 |
| session-disjoint | FedAvg (Adam) | Identifiers only (G1–G4) | 11 | 0.9977 ± 0.0033 | 0.9914 ± 0.0127 | 0.9951 ± 0.0112 | 0.9907 ± 0.0166 | 0.9832 ± 0.0243 |
| chronological | Centralized MLP | Full (all groups + semantic) | 54 | 0.9999 ± 0.0001 | 0.9000 ± 0.2236 | N/A* | 0.0000 ± 0.0000 | 0.0000 ± 0.0000 |
| chronological | Centralized MLP | Minus G1 (hosts/ports: SrcAddr, DstAddr, Sport, Dport) | 50 | 0.9997 ± 0.0004 | 0.7999 ± 0.2740 | N/A* | 0.0000 ± 0.0000 | 0.0000 ± 0.0000 |
| chronological | Centralized MLP | Minus G2 (IP-ID counters: sIpId, dIpId) | 52 | 0.9999 ± 0.0001 | 0.9000 ± 0.2236 | N/A* | 0.0000 ± 0.0000 | 0.0000 ± 0.0000 |
| chronological | Centralized MLP | Minus G3 (timestamps: StartTime, LastTime) | 52 | 0.9999 ± 0.0001 | 0.9000 ± 0.2236 | N/A* | 0.0000 ± 0.0000 | 0.0000 ± 0.0000 |
| chronological | Centralized MLP | Minus G4 (host fingerprints: sTtl, dTtl, sTos) | 51 | 0.9999 ± 0.0003 | 0.9000 ± 0.2237 | N/A* | 0.0000 ± 0.0000 | 0.0000 ± 0.0000 |
| chronological | Centralized MLP | Semantic only (36 flow statistics + one-hot Proto) | 43 | 0.9995 ± 0.0005 | 0.6999 ± 0.2740 | N/A* | 0.0000 ± 0.0000 | 0.0000 ± 0.0000 |
| chronological | Centralized MLP | Identifiers only (G1–G4) | 11 | 1.0000 ± 0.0000 | 1.0000 ± 0.0000 | N/A* | 0.0000 ± 0.0000 | 0.0000 ± 0.0000 |
| chronological | FedAvg (Adam) | Full (all groups + semantic) | 54 | 0.9999 ± 0.0003 | 0.9000 ± 0.2237 | N/A* | 0.0000 ± 0.0000 | 0.0000 ± 0.0000 |
| chronological | FedAvg (Adam) | Minus G1 (hosts/ports: SrcAddr, DstAddr, Sport, Dport) | 50 | 0.9995 ± 0.0010 | 0.7999 ± 0.2740 | N/A* | 0.0000 ± 0.0000 | 0.0000 ± 0.0000 |
| chronological | FedAvg (Adam) | Minus G2 (IP-ID counters: sIpId, dIpId) | 52 | 0.9999 ± 0.0001 | 0.9000 ± 0.2236 | N/A* | 0.0000 ± 0.0000 | 0.0000 ± 0.0000 |
| chronological | FedAvg (Adam) | Minus G3 (timestamps: StartTime, LastTime) | 52 | 0.9999 ± 0.0001 | 0.9000 ± 0.2236 | N/A* | 0.0000 ± 0.0000 | 0.0000 ± 0.0000 |
| chronological | FedAvg (Adam) | Minus G4 (host fingerprints: sTtl, dTtl, sTos) | 51 | 0.9999 ± 0.0003 | 0.9000 ± 0.2237 | N/A* | 0.0000 ± 0.0000 | 0.0000 ± 0.0000 |
| chronological | FedAvg (Adam) | Semantic only (36 flow statistics + one-hot Proto) | 43 | 0.9994 ± 0.0005 | 0.5998 ± 0.2237 | N/A* | 0.0000 ± 0.0000 | 0.0000 ± 0.0000 |
| chronological | FedAvg (Adam) | Identifiers only (G1–G4) | 11 | 0.9999 ± 0.0001 | 0.9000 ± 0.2236 | N/A* | 0.0000 ± 0.0000 | 0.0000 ± 0.0000 |

### Part 2: Session-Disjoint Per-Split ROC-AUC Means (5 Group Partitions × 5 Seeds = 25 Runs)

| Model | Feature Configuration | Split 0 | Split 1 | Split 2 | Split 3 | Split 4 | Overall Mean ± SD |
|---|---|---:|---:|---:|---:|---:|---:|
| Centralized MLP | Full (all groups + semantic) | 0.9953 | 0.9955 | 0.9997 | 0.9997 | 0.9956 | 0.9972 ± 0.0021 |
| Centralized MLP | Minus G1 (hosts/ports: SrcAddr, DstAddr, Sport, Dport) | 0.9952 | 0.9955 | 0.9999 | 0.9999 | 0.9956 | 0.9972 ± 0.0022 |
| Centralized MLP | Minus G2 (IP-ID counters: sIpId, dIpId) | 0.9953 | 0.9955 | 0.9998 | 0.9997 | 0.9956 | 0.9972 ± 0.0021 |
| Centralized MLP | Minus G3 (timestamps: StartTime, LastTime) | 0.9953 | 0.9955 | 0.9998 | 0.9997 | 0.9956 | 0.9972 ± 0.0021 |
| Centralized MLP | Minus G4 (host fingerprints: sTtl, dTtl, sTos) | 0.9953 | 0.9955 | 0.9998 | 0.9997 | 0.9956 | 0.9972 ± 0.0022 |
| Centralized MLP | Semantic only (36 flow statistics + one-hot Proto) | 0.9951 | 0.9955 | 0.9995 | 0.9996 | 0.9954 | 0.9970 ± 0.0021 |
| Centralized MLP | Identifiers only (G1–G4) | 1.0000 | 1.0000 | 1.0000 | 0.9986 | 1.0000 | 0.9997 ± 0.0006 |
| FedAvg (Adam) | Full (all groups + semantic) | 0.9951 | 0.9940 | 0.9981 | 0.9996 | 0.9939 | 0.9961 ± 0.0027 |
| FedAvg (Adam) | Minus G1 (hosts/ports: SrcAddr, DstAddr, Sport, Dport) | 0.9921 | 0.9953 | 0.9913 | 0.9994 | 0.9955 | 0.9947 ± 0.0053 |
| FedAvg (Adam) | Minus G2 (IP-ID counters: sIpId, dIpId) | 0.9953 | 0.9955 | 0.9979 | 0.9996 | 0.9942 | 0.9965 ± 0.0023 |
| FedAvg (Adam) | Minus G3 (timestamps: StartTime, LastTime) | 0.9953 | 0.9950 | 0.9973 | 0.9984 | 0.9947 | 0.9961 ± 0.0021 |
| FedAvg (Adam) | Minus G4 (host fingerprints: sTtl, dTtl, sTos) | 0.9950 | 0.9929 | 0.9987 | 0.9994 | 0.9934 | 0.9959 ± 0.0030 |
| FedAvg (Adam) | Semantic only (36 flow statistics + one-hot Proto) | 0.9914 | 0.9950 | 0.9960 | 0.9992 | 0.9932 | 0.9949 ± 0.0038 |
| FedAvg (Adam) | Identifiers only (G1–G4) | 0.9859 | 0.9951 | 0.9977 | 0.9994 | 0.9975 | 0.9951 ± 0.0112 |

### Part 3: Operating Points for FedAvg (Adam) on Semantic-Only Features Across All Three Splits

| Split | Operating Point | Normal Recall | Attack Recall | FPR | Precision | Macro-F1 | MCC | ROC-AUC | FPR ≤ 5% Reached |
|---|---|---:|---:|---:|---:|---:|---:|---:|:---:|
| random | Max Macro-F1 | 0.9946 | 0.9406 | 0.0054 | 0.9321 | 0.9657 | 0.9313 | 0.9961 | True |
| random | FPR ≤ 5% | 0.9946 | 0.9406 | 0.0054 | 0.9321 | 0.9657 | 0.9313 | 0.9961 | True |
| session-disjoint | Max Macro-F1 | 0.9993 | 0.9340 | 0.0007 | 0.9900 | 0.9791 | 0.9588 | 0.9914 | True |
| session-disjoint | FPR ≤ 5% | 0.9968 | 0.9434 | 0.0032 | 0.9569 | 0.9732 | 0.9464 | 0.9914 | True |
| chronological | Max Macro-F1 | 0.9997 | 0.0000 | 0.0003 | 0.0000 | 0.4999 | 0.0000 | N/A* | True |
| chronological | FPR ≤ 5% | 0.9993 | 0.0000 | 0.0007 | 0.0000 | 0.4998 | 0.0000 | N/A* | True |

### Part 4: Chronological Split Metadata & Raw String Artifact Audit

- **Full Dataset Size:** 1,194,464 rows (StartTime parse success: 100.00%)
- **Chronological Cutoff (80th Percentile):** `2019-08-19 15:24:37`
- **Pre-Cutoff Training Pool:** 955,609 rows (Attack rate: 9.11%)
- **Post-Cutoff Test Pool:** 238,855 rows (Attack rate: 0.00%, Total attack flows: 0)
- **Chronological Split Finding:** *Test period has fewer than 50 attack rows (0 attack rows in the final 20% of data).*
- **Attack Types Exclusively Pre-Cutoff:** Backdoor, CommInj, DoS, Reconn
- **Raw Text Artifact Audit:** Identified 20 raw string values occurring exclusively in one class with ≥ 100 rows.

**Top Exclusive Single-Class Categorical Values in Raw Dataset:**
| Column | Value | Exclusive Class | Row Count |
|---|---|---|---:|
| `SrcAddr` | `209.240.235.92` | attack_only | 46,615 |
| `SrcAddr` | `192.168.0.10` | attack_only | 26,797 |
| `SrcAddr` | `192.168.0.44` | normal_only | 8,317 |
| `SrcAddr` | `20.1.249.77` | attack_only | 7,220 |
| `DstAddr` | `192.168.0.1` | normal_only | 6,938 |
| `SrcAddr` | `49.48.134.64` | attack_only | 6,320 |
| `DstAddr` | `192.168.0.255` | normal_only | 3,876 |
| `SrcAddr` | `01:80:c2:00:00:0e` | normal_only | 2,529 |
| `DstAddr` | `6c:b0:ce:22:b0:57` | normal_only | 2,529 |
| `DstAddr` | `255.255.255.255` | normal_only | 1,994 |

\* *Note: ROC-AUC and PR-AUC are undefined on the chronological test split due to zero positive attack instances in the post-cutoff test period.*
