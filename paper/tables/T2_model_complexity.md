**Table 2.** Model complexity (input dim = 19) — *provenance: measured (parameter count and FLOPs profiled in code)*

| Model | Trainable parameters | Size (KB, float32) | GFLOPs / sample |
|---|---:|---:|---:|
| MLP | 3,426 | 13.38 | 0.000007 |
| CNN 1D | 8,674 | 33.88 | 0.000258 |
| TCN NoAttention | 26,498 | 103.51 | 0.001093 |
| TCN Attention | 43,138 | 168.51 | 0.001716 |
