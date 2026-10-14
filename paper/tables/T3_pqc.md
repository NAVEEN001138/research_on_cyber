**Table 3.** Role-based ML-KEM-768 + AES-256-GCM overhead — *provenance: measured; 1,000 iterations after 50 warm-up; kyber-py pure-Python FIPS-203 reference implementation*

| Operation | Role | Frequency | Median (ms) | P95 (ms) | Std (ms) | Overhead |
|---|---|---|---:|---:|---:|---|
| ML-KEM-768 KeyGen | Server | 1 × per FL round (reused across clients) | 3.2078 | 4.6541 | 0.6490 | pk 1184 B / sk 2400 B |
| ML-KEM-768 Encaps | Client | 1 × per client uplink | 4.2132 | 6.1116 | 0.8393 | ct 1088 B |
| ML-KEM-768 Decaps | Server | 1 × per client uplink | 5.7636 | 8.4183 | 1.1600 | ss 32 B |
| AES-256-GCM encrypt | Client | 1 × per client uplink | 0.0648 | 0.1033 | 0.0235 | payload 25,000 B |
| AES-256-GCM decrypt | Server | 1 × per client uplink | 0.0237 | 0.0334 | 0.0056 | nonce 12 B + tag 16 B |
| **KEM total (keygen+encaps+decaps)** | Server + Client | Combined cycle | **13.1846** | — | — | ciphertext overhead per round 1,116 B |

*Key reuse policy: The server generates one ML-KEM-768 keypair per round and broadcasts its public key. Each participating client encapsulates once, and the server decapsulates once per reporting client.*
