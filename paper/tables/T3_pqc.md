**Table 3.** ML-KEM-768 + AES-256-GCM overhead — *provenance: measured; 1,000 iterations after 50 warm-up; kyber-py pure-Python FIPS-203 reference implementation (upper bound on latency)*

| Operation | Median (ms) | P95 (ms) | Std (ms) | Bytes |
|---|---:|---:|---:|---:|
| ML-KEM-768 KeyGen | 6.9356 | 14.8360 | 3.9552 | pk 1184 / sk 2400 |
| ML-KEM-768 Encaps | 9.1984 | 19.8715 | 5.3159 | ct 1088 |
| ML-KEM-768 Decaps | 12.3634 | 26.1204 | 7.1908 | ss 32 |
| AES-256-GCM encrypt | 0.1537 | 0.2842 | 0.0884 | payload 25,000 |
| AES-256-GCM decrypt | 0.0628 | 0.1476 | 0.0654 | nonce 12 + tag 16 |
| **KEM total (keygen+encaps+decaps)** | **28.4974** | — | — | ciphertext overhead per round 1,116 |
