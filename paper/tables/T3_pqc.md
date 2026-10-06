**Table 3.** ML-KEM-768 + AES-256-GCM overhead — *provenance: measured; 1,000 iterations after 50 warm-up; kyber-py pure-Python FIPS-203 reference implementation (upper bound on latency)*

| Operation | Median (ms) | P95 (ms) | Std (ms) | Bytes |
|---|---:|---:|---:|---:|
| ML-KEM-768 KeyGen | 3.2078 | 4.6541 | 0.6490 | pk 1184 / sk 2400 |
| ML-KEM-768 Encaps | 4.2132 | 6.1116 | 0.8393 | ct 1088 |
| ML-KEM-768 Decaps | 5.7636 | 8.4183 | 1.1600 | ss 32 |
| AES-256-GCM encrypt | 0.0648 | 0.1033 | 0.0235 | payload 25,000 |
| AES-256-GCM decrypt | 0.0237 | 0.0334 | 0.0056 | nonce 12 + tag 16 |
| **KEM total (keygen+encaps+decaps)** | **13.1846** | — | — | ciphertext overhead per round 1,116 |
