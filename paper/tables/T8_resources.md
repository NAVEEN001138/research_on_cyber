**Table 8.** Edge resource profile (CPU only) — *provenance per row*

| Metric | Value | Provenance | Method |
|---|---:|---|---|
| Single-sample inference latency, median | 0.9275 ms | measured | batch = 1, 200 warm-up, 2000 timed |
| Single-sample inference latency, P95 / P99 | 1.3658 / 1.8506 ms | measured | same run |
| Throughput at batch = 1 | 1078.11 samples/s | measured | 1000 / median latency |
| Process RSS | 425.98 MB | measured | psutil.Process().memory_info().rss |
| Trainable parameters | 43,138 | measured | sum(p.numel()) |
| Serialized float32 size | 168.51 KB | measured | params × 4 |
| Median FL round time (SCAFFOLD, random split) | 3.84 s | measured | from Table 4 run |
| Energy per round | 134.28 J | **estimated** | round time × assumed 35.0 W TDP |
| Uplink payload per round (FedAvg / FedProx, Top-k 30%) | 117.66 KB | measured | sparse weights + indices (120,486 B) |
| Uplink payload per round (SCAFFOLD, Top-k 30%) | 295.23 KB | measured | sparse Δw (117.66 KB) + dense Δc (177.57 KB) |
| PQC + AEAD transport overhead per round | 1.09 KB | measured | ML-KEM-768 (1,088 B) + nonce (12 B) + tag (16 B) |
