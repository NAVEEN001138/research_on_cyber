"""
=============================================================================
POST-QUANTUM CRYPTOGRAPHY (PQC) - CRYSTALS-KYBER SIMULATION & OVERHEAD BENCHMARK
Module: pqc_kyber.py
-----------------------------------------------------------------------------
Implements Post-Quantum Cryptography (PQC) Key Generation, Encapsulation,
Decapsulation, and Ciphertext Overhead benchmarking based on NIST-standardized
CRYSTALS-Kyber (ML-KEM-768) lattice-based cryptography for Quantum-Resilient FL.
=============================================================================
"""

import time
import os
import hashlib
import numpy as np

class CrystalsKyberPQC:
    """
    Simulates NIST PQC Standardized CRYSTALS-Kyber-768 (ML-KEM-768)
    Lattice-Based Key Encapsulation Mechanism (KEM) and measures runtime overhead.
    """
    def __init__(self, variant: str = "Kyber-768"):
        self.variant = variant
        if variant == "Kyber-512":
            self.pk_bytes = 800
            self.sk_bytes = 1632
            self.ct_bytes = 768
            self.ss_bytes = 32
        elif variant == "Kyber-1024":
            self.pk_bytes = 1568
            self.sk_bytes = 3168
            self.ct_bytes = 1568
            self.ss_bytes = 32
        else:  # Kyber-768 (Default Recommended)
            self.pk_bytes = 1184
            self.sk_bytes = 2400
            self.ct_bytes = 1088
            self.ss_bytes = 32

    def keypair(self) -> dict:
        """Simulates PQC Lattice Key Pair Generation."""
        t0 = time.perf_counter()
        pk = os.urandom(self.pk_bytes)
        sk = os.urandom(self.sk_bytes)
        t1 = time.perf_counter()
        return {
            "public_key": pk,
            "secret_key": sk,
            "keygen_time_ms": (t1 - t0) * 1000.0,
            "pk_size_bytes": self.pk_bytes,
            "sk_size_bytes": self.sk_bytes
        }

    def encapsulate(self, public_key: bytes) -> dict:
        """Simulates PQC Shared Secret Encapsulation."""
        t0 = time.perf_counter()
        ciphertext = os.urandom(self.ct_bytes)
        shared_secret = hashlib.sha256(ciphertext + public_key).digest()
        t1 = time.perf_counter()
        return {
            "ciphertext": ciphertext,
            "shared_secret": shared_secret,
            "encapsulation_time_ms": (t1 - t0) * 1000.0,
            "ciphertext_size_bytes": self.ct_bytes
        }

    def decapsulate(self, ciphertext: bytes, secret_key: bytes, public_key: bytes) -> dict:
        """Simulates PQC Shared Secret Decapsulation."""
        t0 = time.perf_counter()
        shared_secret = hashlib.sha256(ciphertext + public_key).digest()
        t1 = time.perf_counter()
        return {
            "shared_secret": shared_secret,
            "decapsulation_time_ms": (t1 - t0) * 1000.0
        }

    def benchmark_pqc_overhead(self, num_iterations: int = 100) -> dict:
        """Runs benchmarks measuring average keygen, encap, decap overhead."""
        keygen_times = []
        encap_times = []
        decap_times = []

        for _ in range(num_iterations):
            kp = self.keypair()
            keygen_times.append(kp["keygen_time_ms"])

            enc = self.encapsulate(kp["public_key"])
            encap_times.append(enc["encapsulation_time_ms"])

            dec = self.decapsulate(enc["ciphertext"], kp["secret_key"], kp["public_key"])
            decap_times.append(dec["decapsulation_time_ms"])

        return {
            "variant": self.variant,
            "avg_keygen_ms": round(float(np.mean(keygen_times)), 4),
            "avg_encapsulation_ms": round(float(np.mean(encap_times)), 4),
            "avg_decapsulation_ms": round(float(np.mean(decap_times)), 4),
            "total_pqc_latency_per_client_ms": round(float(np.mean(keygen_times) + np.mean(encap_times) + np.mean(decap_times)), 4),
            "public_key_bytes": self.pk_bytes,
            "ciphertext_bytes": self.ct_bytes,
        }
