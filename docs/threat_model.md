# Threat Model & Cryptographic Security Architecture

This document defines the formal operational threat model, adversary capabilities, cryptographic primitives, and security boundaries governing the Cloud Guardian framework.

---

## 1. Threat Model & Trust Assumptions

We evaluate Cloud Guardian under a multi-party threat environment encompassing the central aggregator, edge IoT clients, and network adversaries:

### A. Central Aggregation Server: Honest-but-Curious (Semi-Honest)
- **Assumption**: The central server correctly executes the federated aggregation protocol (e.g., FedAvg, FedProx, or SCAFFOLD averaging) without deviating from specified algorithm steps.
- **Threat**: The server may attempt to inspect individual client parameter updates ($\Delta w_k$) to infer private edge telemetry, proprietary SCADA network topology, or sensitive local industrial configurations (membership inference and reconstruction attacks).
- **Defense**: Post-quantum key encapsulation (ML-KEM-768) and point-to-point AES-256-GCM encryption guarantee that parameter updates in transit cannot be intercepted by network adversaries. At the server, client updates are processed under cosine similarity trust scoring; formal multiparty secure aggregation (e.g. Bonawitz pairwise masking) is identified as future work and not claimed here.

### B. Edge Client Nodes: Byzantine Malicious Subset ($f < K/2$)
- **Assumption**: Up to $f$ out of $K$ edge client nodes may be compromised or actively controlled by a malicious Byzantine adversary.
- **Threat Capabilities**:
  1. **Data Poisoning (Label Flipping)**: Malicious clients flip training labels on local telemetry (e.g. mapping attack traffic to normal classes) to degrade global detection sensitivity.
  2. **Model Replacement / Scaled Gradient Attacks**: Malicious clients compute adversarial updates $\Delta w_{\text{mal}} = -\lambda \Delta w$ ($\lambda=5$) to poison the global model direction.
- **Defense**: The central server applies **Cosine-Similarity Adaptive Trust Scoring**, benchmarking incoming update vectors against a robust coordinate-wise median reference vector, dynamically penalizing and filtering deviating gradients.

### C. Network Adversary: Passive Eavesdropper with Future Quantum Capability (HNDL)
- **Threat**: A passive adversary eavesdrops on communication channels between edge devices and the central aggregator, recording encrypted model update traffic today with the objective of decrypting it when cryptanalytically relevant quantum computers (CRQCs) become available ("Harvest-Now, Decrypt-Later" / HNDL attack).
- **Defense**: Classical Diffie-Hellman / RSA key exchanges are completely eliminated. All ephemeral session keys are established using **NIST FIPS-203 ML-KEM-768** (Module Lattice-based Key Encapsulation Mechanism), offering 192-bit post-quantum security margin. Symmetric payloads are encrypted with **AES-256-GCM**.

---

## 2. Cryptographic Protocol & Replay Protection

For each federated round $r \in \{1, \dots, R\}$ and participating client $k$:

1. **Key Establishment**:
   - The central server generates an ephemeral ML-KEM-768 keypair $(\text{ek}_r, \text{dk}_r) \leftarrow \text{MLKEM768.keygen()}$ and broadcasts the public encapsulation key $\text{ek}_r$.
   - Client $k$ encapsulates a 32-byte shared secret:
     $$(c_{k,r}, ss_{k,r}) \leftarrow \text{MLKEM768.encaps}(\text{ek}_r)$$
   - Both parties derive an ephemeral 256-bit AES key via HKDF-SHA256:
     $$K_{k,r} \leftarrow \text{HKDF-SHA256}(ss_{k,r}, \text{info}=\texttt{"fl-round-"}\|r, L=32)$$

2. **Payload Confidentiality & Replay Protection**:
   - The sparse model update $\Delta w_{k,r}$ is serialized to binary format $M_{k,r}$.
   - Client $k$ draws a fresh 12-byte random nonce $\text{nonce}_{k,r} \leftarrow \{0, 1\}^{96}$.
   - The payload is encrypted with AES-256-GCM, binding the training round $r$ into the Additional Authenticated Data (AAD):
     $$C_{k,r} \leftarrow \text{AES-GCM-Encrypt}(K_{k,r}, \text{nonce}_{k,r}, M_{k,r}, \text{AAD}=\texttt{"fl-round-"}\|r)$$
   - The client transmits $(c_{k,r}, \text{nonce}_{k,r}, C_{k,r})$ to the server.
   - Any replay of $C_{k,r}$ in subsequent rounds $r' \neq r$ produces an immediate `InvalidTag` authentication failure.

---

## 3. Explicit Out-of-Scope Security Claims & Limitations

To maintain scientific rigor, the following boundaries are explicitly established:
1. **Client Identity Authentication**: Post-quantum digital signatures (NIST FIPS-204 ML-DSA or FIPS-205 SLH-DSA) for client authentication are currently out of scope; client authentication is assumed to be established out-of-band via existing industrial PKI/TLS.
2. **Dropout Recovery in Multi-Party Computation**: Pairwise blinding mask protocols with secret-sharing dropout recovery (e.g., Bonawitz et al.) are not implemented in this release; hence, the paper makes no claims of Bonawitz secure aggregation.
3. **Formal Differential Privacy Guarantee**: Standard parameter perturbation (adding Gaussian noise to model updates) does not provide formal differential privacy bounds ($\varepsilon, \delta$); formal DP-SGD via Opacus with per-sample clipping is evaluated separately where specified.
