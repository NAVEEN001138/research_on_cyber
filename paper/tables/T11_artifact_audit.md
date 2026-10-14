**Table 11.** Edge-IIoTset `dns.qry.name.len` formatting artifact audit — *provenance: measured; 157,800 rows; citation: Galal, arXiv:2608.15761*

### Part 1: Formatting artifact distribution in ML-EdgeIIoT-dataset.csv

| Raw String Representation | Normal Traffic Rows | Attack Traffic Rows | Total Rows | Attack Share (%) |
|---|---:|---:|---:|---:|
| String `"0"` | 24,272 | 0 | 24,272 | 0.00 |
| String `"0.0"` | 0 | 133,272 | 133,272 | 100.00 |
| Other string values | 29 | 227 | 256 | 88.67 |

### Part 2: Impact on Classifier Performance

| Preprocessing Recipe | Feature Representation | Test Accuracy | Test ROC-AUC | Diagnostic Finding |
|---|---|---:|---:|---|
| String One-Hot (Official Edge-IIoTset Recipe) | String categorical one-hot | 0.9998 | 1.0000 | Achieves ~1.0 ROC-AUC (99.98% accuracy) purely by memorizing the string formatting anomaly ('0' for normal vs '0.0' for attack). |
| Numeric Parsing (Strict float32) | `pd.to_numeric` | 0.8460 | 0.5007 | Collapses both '0' and '0.0' to identical 0.0, destroying the artifact and dropping ROC-AUC to chance (~0.50). |
