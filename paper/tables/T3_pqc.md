**Table 3.** Role-based ML-KEM-768 + AES-256-GCM overhead — *provenance: measured; 1,000 iterations after 50 warm-up; kyber-py pure-Python FIPS-203 reference implementation*

| Operation | Role | Frequency | Median (ms) | P95 (ms) | Std (ms) | Overhead |
|---|---|---|---:|---:|---:|---|
| ML-KEM-768 KeyGen | Server | 1 × per FL round (reused across clients) | 6.8259 | 10.0072 | 1.3838 | pk 1184 B / sk 2400 B |
| ML-KEM-768 Encaps | Client | 1 × per client uplink | 9.1113 | 13.1704 | 1.8549 | ct 1088 B |
| ML-KEM-768 Decaps | Server | 1 × per client uplink | 12.3505 | 17.1974 | 2.3260 | ss 32 B |
| AES-256-GCM encrypt | Client | 1 × per client uplink | 0.1344 | 0.2013 | 0.0396 | payload 25,000 B |
| AES-256-GCM decrypt | Server | 1 × per client uplink | 0.0575 | 0.0927 | 0.0253 | nonce 12 B + tag 16 B |
| **KEM total (keygen+encaps+decaps)** | Server + Client | Combined cycle | **28.2877** | — | — | ciphertext overhead per round 1,116 B |

*Key reuse policy: The server generates one ML-KEM-768 keypair per round and broadcasts its public key. Each participating client encapsulates once, and the server decapsulates once per reporting client.*
