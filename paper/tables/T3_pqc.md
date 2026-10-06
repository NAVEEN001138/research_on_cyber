**Table 3.** ML-KEM-768 + AES-256-GCM overhead — *provenance: measured; 1,000 iterations after 50 warm-up; kyber-py pure-Python FIPS-203 reference implementation (upper bound on latency)*

| Operation | Median (ms) | P95 (ms) | Std (ms) | Bytes |
|---|---:|---:|---:|---:|
| ML-KEM-768 KeyGen | 6.3643 | 10.0781 | 1.8661 | pk 1184 / sk 2400 |
| ML-KEM-768 Encaps | 8.3786 | 13.4280 | 6.0459 | ct 1088 |
| ML-KEM-768 Decaps | 11.4729 | 17.6755 | 10.7834 | ss 32 |
| AES-256-GCM encrypt | 0.1313 | 0.2185 | 0.0412 | payload 25,000 |
| AES-256-GCM decrypt | 0.0546 | 0.0994 | 0.0230 | nonce 12 + tag 16 |
| **KEM total (keygen+encaps+decaps)** | **26.2158** | — | — | ciphertext overhead per round 1,116 |
