"""
=============================================================================
DATASET INTEGRITY & PROVENANCE VERIFIER
Module: utils/dataset_integrity.py
-----------------------------------------------------------------------------
Verifies cryptographic SHA-256 hashes of dataset files against DATASETS.md
specifications on first load and caches verification to avoid repeated I/O.
=============================================================================
"""

import os
import json
import hashlib
from typing import Optional

DATASET_HASHES = {
    "ML-EdgeIIoT-dataset.csv": {
        "expected_bytes": 82184390,
        "sha256": "53101fad091af20bee815860962a5016b802ee45d456a141042f6183094c3c1a"
    },
    "DNN-EdgeIIoT-dataset.csv": {
        "expected_bytes": 1217413981,
        "sha256": "1d3ef6c7cc22784a528a117f1158f5cad750273679437e18a39c360ee6b79fd7"
    },
    "wustl_iiot_2021.csv": {
        "expected_bytes": 409800698,
        "sha256": "f897b24578cc6fdeb3e7a0e9ff63efd5bbdc926a545abbda725e0dbb348c6bca"
    }
}

CACHE_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "datasets", ".hashes_verified.json")


def verify_dataset_hash(file_path: str) -> bool:
    """
    Verifies that the file at file_path matches its expected SHA-256 hash.
    Caches verified results in datasets/.hashes_verified.json.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Dataset file not found: {file_path}. See DATASETS.md for download instructions.")

    filename = os.path.basename(file_path)
    if filename not in DATASET_HASHES:
        # Not a managed dataset file
        return True

    expected = DATASET_HASHES[filename]

    # Check cache
    cache = {}
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, "r") as f:
                cache = json.load(f)
            if filename in cache and cache[filename].get("status") == "VERIFIED":
                if os.path.getsize(file_path) == expected["expected_bytes"]:
                    return True
        except Exception:
            pass

    # Compute hash
    hasher = hashlib.sha256()
    with open(file_path, "rb") as f:
        while chunk := f.read(65536 * 16):
            hasher.update(chunk)
    actual_hash = hasher.hexdigest()

    if actual_hash != expected["sha256"]:
        raise ValueError(
            f"Dataset hash mismatch for {filename}!\n"
            f"Expected: {expected['sha256']}\n"
            f"Actual:   {actual_hash}\n"
            f"Please verify your file integrity per DATASETS.md."
        )

    # Save to cache
    cache[filename] = {
        "status": "VERIFIED",
        "sha256": actual_hash,
        "size_bytes": os.path.getsize(file_path)
    }
    os.makedirs(os.path.dirname(CACHE_FILE), exist_ok=True)
    with open(CACHE_FILE, "w") as f:
        json.dump(cache, f, indent=2)

    return True
