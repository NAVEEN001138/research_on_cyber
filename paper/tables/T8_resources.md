**Table 8.** Edge resource profile (CPU only) — *provenance per row*

| Metric | Value | Provenance | Method |
|---|---:|---|---|
| Single-sample inference latency, median | 2.3186 ms | measured | batch = 1, 200 warm-up, 2000 timed |
| Single-sample inference latency, P95 / P99 | 2.9656 / 3.6871 ms | measured | same run |
| Throughput at batch = 1 | 431.30 samples/s | measured | 1000 / median latency |
| Process RSS | 426.45 MB | measured | psutil.Process().memory_info().rss |
| Trainable parameters | 43,138 | measured | sum(p.numel()) |
| Serialized float32 size | 168.51 KB | measured | params × 4 |
| Median FL round time (SCAFFOLD, random split) | 5.52 s | measured | from Table 4 run |
| Energy per round | 193.15 J | **estimated** | round time × assumed 35.0 W TDP |
