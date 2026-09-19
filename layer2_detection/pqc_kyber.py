"""
=============================================================================
POST-QUANTUM CRYPTOGRAPHY (PQC): NIST FIPS-203 ML-KEM-768 & AES-256-GCM
Module: layer2_detection/pqc_kyber.py
-----------------------------------------------------------------------------
Implements genuine Post-Quantum Key Encapsulation using standard FIPS-203
ML-KEM-768 (CRYSTALS-Kyber), HKDF-SHA256 round-key derivation, and
authenticated payload encryption via AES-256-GCM with replay protection (AAD).
=============================================================================
"""

import os
import time
from typing import Tuple, Dict
from kyber_py.ml_kem import ML_KEM_768
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.exceptions import InvalidTag


class MLKEM768:
    """
    NIST FIPS-203 Standardized ML-KEM-768 Key Encapsulation Mechanism.
    Lattice-based cryptography providing Category 3 post-quantum security (equivalent to AES-192).
    """
    def __init__(self):
        self.variant = "ML-KEM-768"
        self.pk_bytes = 1184
        self.sk_bytes = 2400
        self.ct_bytes = 1088
        self.ss_bytes = 32

    @staticmethod
    def keygen() -> Tuple[bytes, bytes]:
        """Generates ML-KEM-768 public key (encapsulation key) and secret key (decapsulation key)."""
        pk, sk = ML_KEM_768.keygen()
        return bytes(pk), bytes(sk)

    @staticmethod
    def encaps(pk: bytes) -> Tuple[bytes, bytes]:
        """
        Encapsulates a 32-byte shared secret using the recipient's public key.
        Returns: (ciphertext, shared_secret)
        """
        shared_secret, ciphertext = ML_KEM_768.encaps(pk)
        return bytes(ciphertext), bytes(shared_secret)

    @staticmethod
    def decaps(ct: bytes, sk: bytes) -> bytes:
        """
        Decapsulates the 32-byte shared secret using the recipient's secret key.
        Per FIPS-203, if ct is invalid or wrong key is provided, an implicit rejection
        pseudo-random shared key is generated (does not match original shared secret).
        """
        shared_secret = ML_KEM_768.decaps(sk, ct)
        return bytes(shared_secret)


def derive_round_key(shared_secret: bytes, round_num: int) -> bytes:
    """
    Derives an ephemeral 256-bit AES symmetric key from the post-quantum shared secret
    bound to the specific federated training round using HKDF-SHA256.
    """
    hkdf = HKDF(
        algorithm=hashes.SHA256(),
        length=32,
        salt=None,
        info=f"fl-round-{round_num}".encode("utf-8")
    )
    return hkdf.derive(shared_secret)


def encrypt_payload(payload_bytes: bytes, shared_secret: bytes, round_num: int) -> bytes:
    """
    Encrypts payload_bytes with AES-256-GCM using key derived from shared_secret.
    Includes a 12-byte random nonce and authenticates the round number in AAD.
    Returns: nonce (12 bytes) + ciphertext + tag (16 bytes)
    """
    aes_key = derive_round_key(shared_secret, round_num)
    nonce = os.urandom(12)
    aad = f"fl-round-{round_num}".encode("utf-8")
    aesgcm = AESGCM(aes_key)
    ciphertext = aesgcm.encrypt(nonce, payload_bytes, aad)
    return nonce + ciphertext


def decrypt_payload(encrypted_blob: bytes, shared_secret: bytes, round_num: int) -> bytes:
    """
    Decrypts encrypted_blob with AES-256-GCM and verifies authentication tag and round AAD.
    Raises InvalidTag if tampered or mismatched.
    """
    if len(encrypted_blob) < 28:
        raise ValueError("Encrypted blob too short for nonce + tag")
    nonce = encrypted_blob[:12]
    ciphertext = encrypted_blob[12:]
    aad = f"fl-round-{round_num}".encode("utf-8")
    aes_key = derive_round_key(shared_secret, round_num)
    aesgcm = AESGCM(aes_key)
    return aesgcm.decrypt(nonce, ciphertext, aad)


def benchmark_pqc_operations(num_iterations: int = 1000, warmup: int = 50) -> dict:
    """
    Empirically benchmarks ML-KEM-768 KeyGen, Encaps, Decaps, and AES-256-GCM
    over specified iterations with warmup. Returns measured timing percentiles.
    """
    kem = MLKEM768()
    dummy_payload = os.urandom(25000)  # ~25 KB representative model update

    # Warmup
    for _ in range(warmup):
        pk, sk = kem.keygen()
        ct, ss = kem.encaps(pk)
        _ = kem.decaps(ct, sk)
        enc = encrypt_payload(dummy_payload, ss, 1)
        _ = decrypt_payload(enc, ss, 1)

    keygen_times = []
    encaps_times = []
    decaps_times = []
    aes_encrypt_times = []
    aes_decrypt_times = []

    for r in range(num_iterations):
        t0 = time.perf_counter()
        pk, sk = kem.keygen()
        t1 = time.perf_counter()
        ct, ss = kem.encaps(pk)
        t2 = time.perf_counter()
        ss_dec = kem.decaps(ct, sk)
        t3 = time.perf_counter()
        enc = encrypt_payload(dummy_payload, ss, r)
        t4 = time.perf_counter()
        dec = decrypt_payload(enc, ss_dec, r)
        t5 = time.perf_counter()

        keygen_times.append((t1 - t0) * 1000.0)
        encaps_times.append((t2 - t1) * 1000.0)
        decaps_times.append((t3 - t2) * 1000.0)
        aes_encrypt_times.append((t4 - t3) * 1000.0)
        aes_decrypt_times.append((t5 - t4) * 1000.0)

    import numpy as np
    def get_stats(arr):
        return {
            "median_ms": round(float(np.median(arr)), 4),
            "p95_ms": round(float(np.percentile(arr, 95)), 4),
            "std_ms": round(float(np.std(arr)), 4),
            "mean_ms": round(float(np.mean(arr)), 4)
        }

    return {
        "provenance": "measured",
        "iterations": num_iterations,
        "warmup": warmup,
        "keygen": get_stats(keygen_times),
        "encaps": get_stats(encaps_times),
        "decaps": get_stats(decaps_times),
        "aes_gcm_encrypt": get_stats(aes_encrypt_times),
        "aes_gcm_decrypt": get_stats(aes_decrypt_times),
        "payload_bytes": len(dummy_payload),
        "ciphertext_overhead_bytes": kem.ct_bytes + 28  # 1088 (KEM) + 12 (nonce) + 16 (tag)
    }
