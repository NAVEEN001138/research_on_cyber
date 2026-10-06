"""
=============================================================================
UNIT TEST: POST-QUANTUM CRYPTOGRAPHY (ML-KEM-768 & AES-256-GCM)
Test: tests/test_pqc.py
-----------------------------------------------------------------------------
Validates that:
1. Shared secrets match: ss_enc == ss_dec for 100 random keypairs.
2. Decapsulation with the wrong secret key yields a different secret (proving
   the secret key is actually used, unlike the archived dummy implementation).
3. AES-256-GCM encrypt/decrypt round-trips correctly with HKDF round keys.
4. Tampered ciphertext or mismatched round numbers trigger InvalidTag verification failure.
=============================================================================
"""

import unittest
import os
from cryptography.exceptions import InvalidTag
from layer2_detection.pqc_kyber import (
    MLKEM768,
    derive_round_key,
    encrypt_payload,
    decrypt_payload
)


class TestMLKEM768(unittest.TestCase):

    def setUp(self):
        self.kem = MLKEM768()

    def test_shared_secrets_match_100_trials(self):
        """Asserts ss_enc == ss_dec across 100 distinct random keypairs."""
        for i in range(100):
            pk, sk = self.kem.keygen()
            self.assertEqual(len(pk), 1184, "ML-KEM-768 public key must be 1184 bytes")
            self.assertEqual(len(sk), 2400, "ML-KEM-768 secret key must be 2400 bytes")

            ct, ss_enc = self.kem.encaps(pk)
            self.assertEqual(len(ct), 1088, "ML-KEM-768 ciphertext must be 1088 bytes")
            self.assertEqual(len(ss_enc), 32, "Shared secret must be 32 bytes")

            ss_dec = self.kem.decaps(ct, sk)
            self.assertEqual(
                ss_enc,
                ss_dec,
                f"Shared secret mismatch at trial {i}!"
            )

    def test_wrong_secret_key_yields_different_secret(self):
        """Asserts that decapsulation with wrong key yields a different secret (implicit rejection)."""
        pk1, sk1 = self.kem.keygen()
        pk2, sk2 = self.kem.keygen()

        # Encapsulate against keypair 1
        ct1, ss1 = self.kem.encaps(pk1)

        # Decapsulate with wrong key sk2
        ss_wrong = self.kem.decaps(ct1, sk2)

        self.assertNotEqual(
            ss1,
            ss_wrong,
            "Decapsulation with wrong secret key MUST NOT return the same shared secret!"
        )

    def test_aes_gcm_roundtrip(self):
        """Asserts AES-256-GCM payload encryption and decryption succeeds with correct key and round."""
        pk, sk = self.kem.keygen()
        ct, ss = self.kem.encaps(pk)
        ss_dec = self.kem.decaps(ct, sk)

        payload = b"FL-Model-Update-Tensor-Bytes-2026"
        round_num = 5

        ciphertext = encrypt_payload(payload, ss, round_num)
        decrypted = decrypt_payload(ciphertext, ss_dec, round_num)

        self.assertEqual(payload, decrypted, "Decrypted payload does not match original!")

    def test_tampered_ciphertext_fails_verification(self):
        """Asserts that flipping a single byte in ciphertext raises InvalidTag."""
        pk, sk = self.kem.keygen()
        ct, ss = self.kem.encaps(pk)

        payload = b"Sensitive-Gradient-Data"
        round_num = 1
        ciphertext = bytearray(encrypt_payload(payload, ss, round_num))

        # Tamper with byte at index 15 (inside ciphertext body)
        ciphertext[15] ^= 0xFF

        with self.assertRaises(InvalidTag):
            decrypt_payload(bytes(ciphertext), ss, round_num)

    def test_mismatched_round_fails_verification(self):
        """Asserts replay attack prevention: encrypting for round r fails when decrypted with round r+1."""
        pk, sk = self.kem.keygen()
        ct, ss = self.kem.encaps(pk)

        payload = b"Round-1-Update"
        ciphertext = encrypt_payload(payload, ss, round_num=1)

        # Attempt to replay in round 2
        with self.assertRaises(InvalidTag):
            decrypt_payload(ciphertext, ss, round_num=2)


if __name__ == "__main__":
    unittest.main()
