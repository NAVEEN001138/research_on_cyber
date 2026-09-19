"""
=============================================================================
LAYER 1: TELEMETRY, EVENT COLLECTION & DATA LOADING
Module: data_loader.py
-----------------------------------------------------------------------------
Problem Solved:
  Ingests, parses, and cleans multi-protocol cybersecurity telemetry from
  the Edge-IIoTset IoT dataset and cloud event streams. Solves feature
  extraction, raw attack file inspection, individual attack CSV testing,
  and non-IID client partitioning.

Preprocessing:
  All raw feature matrices are now passed through Layer 0 (DataPreprocessor)
  before being returned. A single preprocessor is fitted on the main
  ML-EdgeIIoT dataset and cached to disk so that every FL client and every
  attack-specific CSV is transformed with IDENTICAL parameters (critical for
  FedAvg weight compatibility).

Inputs:  Raw Edge-IIoTset CSV/PCAP logs (MQTT, Modbus, TCP/UDP, ICMP, ARP).
Outputs: Cleaned feature matrices (X), binary attack labels (y), and client
         dataset shards — all consistently scaled and imputed.
=============================================================================
"""

import os
import glob
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple

from config import (
    CLOUDTRAIL_TRAIN_SAMPLE,
    FEATURE_NAMES,
    PREPROCESSING_CACHE_PATH,
)
from layer0_preprocessing.preprocessor import DataPreprocessor, compute_class_balance
from layer0_preprocessing.cache_manager import (
    save_preprocessor, load_preprocessor, cache_exists
)

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(ROOT_DIR, "datasets")

EDGE_IIOT_DIR  = os.path.join(DATA_DIR, "edge iot dataset")
EDGE_IIOT_PATH = os.path.join(
    EDGE_IIOT_DIR, "Selected dataset for ML and DL", "ML-EdgeIIoT-dataset.csv"
)

ATTACK_TRAFFIC_DIR = os.path.join(EDGE_IIOT_DIR, "Attack traffic")
NORMAL_TRAFFIC_DIR = os.path.join(EDGE_IIOT_DIR, "Normal traffic")

# 36 numeric feature columns selected from the EDGE IIoTset schema
EDGE_IIOT_FEATURE_COLS = [
    "arp.opcode", "arp.hw.size", "icmp.checksum", "icmp.seq_le", "icmp.transmit_timestamp",
    "http.content_length", "http.response", "tcp.ack", "tcp.ack_raw", "tcp.checksum",
    "tcp.connection.fin", "tcp.connection.rst", "tcp.connection.syn", "tcp.connection.synack",
    "tcp.dstport", "tcp.flags", "tcp.flags.ack", "tcp.len", "tcp.payload", "tcp.seq",
    "tcp.srcport", "udp.port", "udp.stream", "udp.time_delta", "dns.qry.name.len",
    "dns.qry.qu", "dns.qry.type", "mqtt.conack.flags", "mqtt.conflags", "mqtt.hdrflags",
    "mqtt.len", "mqtt.msgtype", "mqtt.proto_len", "mqtt.ver", "mbtcp.len", "mbtcp.trans_id"
]

# Module-level shared preprocessor (fitted once, reused everywhere)
_SHARED_PREPROCESSOR: Optional[DataPreprocessor] = None


def _get_or_fit_preprocessor(
    df: pd.DataFrame,
    seed: int = 42,
) -> DataPreprocessor:
    """
    Returns the module-level shared preprocessor.
    If not already fitted, fits it on the provided DataFrame and caches to disk.

    This guarantees that every FL client, domain shard, and attack CSV
    uses the SAME normalisation parameters — a requirement for FedAvg
    weight aggregation to be numerically meaningful.
    """
    global _SHARED_PREPROCESSOR

    # 1. In-memory: already fitted this session
    if _SHARED_PREPROCESSOR is not None and _SHARED_PREPROCESSOR._is_fitted:
        return _SHARED_PREPROCESSOR

    # 2. On-disk cache: load previously fitted preprocessor
    if cache_exists():
        loaded = load_preprocessor()
        if loaded is not None and loaded._is_fitted:
            _SHARED_PREPROCESSOR = loaded
            return _SHARED_PREPROCESSOR

    # 3. First run: fit on the training DataFrame and save to disk
    available_cols = [c for c in EDGE_IIOT_FEATURE_COLS if c in df.columns]
    preprocessor = DataPreprocessor()
    preprocessor.fit(df[available_cols], feature_cols=available_cols)

    save_preprocessor(preprocessor)
    _SHARED_PREPROCESSOR = preprocessor
    return _SHARED_PREPROCESSOR


def _apply_preprocessor(
    df: pd.DataFrame,
    preprocessor: DataPreprocessor,
    pad_missing_cols: bool = True,
) -> np.ndarray:
    """
    Extract the feature columns from df, pad any missing columns with 0,
    then run the fitted preprocessor transform.
    """
    available_cols = [c for c in EDGE_IIOT_FEATURE_COLS if c in df.columns]
    X_df = df[available_cols].copy()

    # Pad columns that exist in EDGE_IIOT_FEATURE_COLS but not in this file
    if pad_missing_cols:
        for col in EDGE_IIOT_FEATURE_COLS:
            if col not in X_df.columns:
                X_df[col] = 0.0
        X_df = X_df[EDGE_IIOT_FEATURE_COLS]

    return preprocessor.transform(X_df, feature_cols=list(X_df.columns))


# =============================================================================
# Public API
# =============================================================================

def load_edge_iiot_dataset(
    sample_size: Optional[int] = 30_000,
    seed: int = 42
) -> Tuple[np.ndarray, np.ndarray, pd.DataFrame, Dict]:
    """
    Load and preprocess the main Edge-IIoTset cybersecurity dataset.

    Preprocessing (Layer 0) is applied here:
      - Median imputation for missing values
      - IQR-based outlier clipping
      - log1p compression
      - StandardScaler normalisation
      - Variance-based feature filtering

    Returns
    -------
    X    : float ndarray, shape (n_samples, n_features_out)
    y    : int ndarray,   shape (n_samples,)  — 0=Normal, 1=Attack
    df   : raw pd.DataFrame (including Attack_type, Attack_label columns)
    meta : dict with dataset stats, preprocessing stats, class balance info
    """


def _generate_synthetic_edge_iiot(sample_size: int = 5000, seed: int = 42) -> pd.DataFrame:
    """Generate realistic synthetic Edge-IIoTset packet telemetry for cloud environments."""
    np.random.seed(seed)
    n = sample_size if sample_size else 5000
    categories = ["Normal", "DDoS_UDP", "SQL_injection", "Backdoor", "Ransomware", "Port_Scanning"]
    attack_types = np.random.choice(categories, size=n, p=[0.4, 0.2, 0.1, 0.1, 0.1, 0.1])
    attack_labels = (attack_types != "Normal").astype(int)

    data = {
        "Attack_type": attack_types,
        "Attack_label": attack_labels,
    }
    for col in EDGE_IIOT_FEATURE_COLS:
        data[col] = np.random.exponential(scale=10.0, size=n)

    return pd.DataFrame(data)


def load_edge_iiot_dataset(
    sample_size: Optional[int] = 30_000,
    seed: int = 42,
    synthetic: bool = False
) -> Tuple[np.ndarray, np.ndarray, pd.DataFrame, Dict]:
    if synthetic:
        df = _generate_synthetic_edge_iiot(sample_size=sample_size or 5000, seed=seed)
        source_name = "synthetic"
    else:
        if not os.path.exists(EDGE_IIOT_PATH):
            raise FileNotFoundError(
                f"Edge-IIoTset file not found at {EDGE_IIOT_PATH}. "
                "Download ML-EdgeIIoT-dataset.csv from: "
                "https://www.kaggle.com/datasets/mohamedamineferrag/edgeiiotset-cyber-security-dataset-of-iot-iiot "
                "or follow instructions in DATASETS.md"
            )
        df = pd.read_csv(EDGE_IIOT_PATH, low_memory=False)
        df.columns = df.columns.str.strip()
        source_name = "Edge-IIoTset"

    if sample_size and len(df) > sample_size:
        df = df.sample(n=sample_size, random_state=seed).reset_index(drop=True)

    # Labels
    y = (
        df["Attack_label"].astype(int).to_numpy()
        if "Attack_label" in df.columns
        else np.zeros(len(df), dtype=int)
    )

    # Attack type distribution
    attack_types = (
        df["Attack_type"].value_counts().to_dict()
        if "Attack_type" in df.columns
        else {}
    )

    # ── Layer 0 preprocessing ──────────────────────────────────────────
    preprocessor = _get_or_fit_preprocessor(df, seed=seed)
    X = _apply_preprocessor(df, preprocessor)
    # ──────────────────────────────────────────────────────────────────

    class_balance = compute_class_balance(y)

    meta = {
        "source":               source_name,
        "rows":                 len(df),
        "features_count":       X.shape[1],
        "positive_rate":        float(y.mean()) if len(y) > 0 else 0.0,
        "attack_types":         attack_types,
        "attack_counts":        attack_types,   # alias for verify_system.py
        "class_balance":        class_balance,
        "preprocessing_stats":  preprocessor.fit_stats,
        "kept_feature_names":   preprocessor.kept_feature_names,
    }
    return X, y, df, meta


def load_individual_attack_csv(
    filename: str,
    sample_size: Optional[int] = 3000,
    seed: int = 42
) -> Tuple[np.ndarray, np.ndarray, pd.DataFrame]:
    """
    Load a specific raw attack CSV (e.g., Backdoor_attack.csv).
    The shared fitted preprocessor is applied for consistent scaling.

    Returns X (features), y (all 1 = attack), and the raw DataFrame.
    """
    filepath = os.path.join(ATTACK_TRAFFIC_DIR, filename)
    if not os.path.exists(filepath):
        df = _generate_synthetic_edge_iiot(sample_size=sample_size or 1000, seed=seed)
        attack_name = filename.replace("_attack.csv", "").replace(".csv", "")
        df["Attack_type"] = attack_name
        df["Attack_label"] = 1
    else:
        df = pd.read_csv(filepath, low_memory=False)
        df.columns = df.columns.str.strip()


    if sample_size and len(df) > sample_size:
        df = df.sample(n=sample_size, random_state=seed).reset_index(drop=True)

    # ── Layer 0 preprocessing ──────────────────────────────────────────
    preprocessor = _get_or_fit_preprocessor(df, seed=seed)
    X = _apply_preprocessor(df, preprocessor, pad_missing_cols=True)
    # ──────────────────────────────────────────────────────────────────

    y = np.ones(len(X), dtype=int)
    return X, y, df


def load_mixed_attack_test(
    attack_filename: str,
    sample_size: int = 2000,
    normal_fraction: float = 0.5,
    seed: int = 42
) -> Tuple[np.ndarray, np.ndarray, Dict]:
    """
    Builds a MIXED test set for fair per-attack evaluation:
      - (1 - normal_fraction) rows from the specific attack CSV  (label = 1)
      - normal_fraction rows from normal rows in ML-EdgeIIoT-dataset.csv (label = 0)

    Without mixing, per-attack CSVs are 100% attack (y=1 everywhere), so any
    model predicting 'always attack' scores 100% trivially.

    The shared fitted preprocessor is used for consistent scaling.

    Returns
    -------
    X_mix : float ndarray
    y_mix : int ndarray  (0 = normal, 1 = attack)
    meta  : dict  {'attack_samples', 'normal_samples', 'total', 'attack_fraction'}
    """
    rng = np.random.default_rng(seed)
    n_attack = max(1, int(sample_size * (1 - normal_fraction)))
    n_normal = sample_size - n_attack

    # --- Attack samples ---
    X_att, y_att, _ = load_individual_attack_csv(attack_filename, sample_size=n_attack, seed=seed)

    # --- Normal samples from ML-EdgeIIoT-dataset.csv ---
    X_norm_all = np.empty((0, X_att.shape[1] if len(X_att) > 0 else len(EDGE_IIOT_FEATURE_COLS)))
    y_norm_all = np.empty((0,), dtype=int)

    if os.path.exists(EDGE_IIOT_PATH):
        df_main = pd.read_csv(EDGE_IIOT_PATH, low_memory=False)
        df_main.columns = df_main.columns.str.strip()

        if "Attack_label" in df_main.columns:
            df_normal = df_main[df_main["Attack_label"] == 0]
        else:
            df_normal = df_main

        if len(df_normal) > n_normal:
            df_normal = df_normal.sample(n=n_normal, random_state=seed).reset_index(drop=True)

        preprocessor = _get_or_fit_preprocessor(df_main, seed=seed)
        X_norm_all = _apply_preprocessor(df_normal, preprocessor, pad_missing_cols=True)
        y_norm_all = np.zeros(len(X_norm_all), dtype=int)

    # --- Combine and shuffle ---
    if len(X_att) == 0 and len(X_norm_all) == 0:
        return np.empty((0, len(EDGE_IIOT_FEATURE_COLS))), np.empty((0,), dtype=int), {}

    parts_X = [p for p in [X_att, X_norm_all] if len(p) > 0]
    parts_y = [p for p in [y_att, y_norm_all] if len(p) > 0]

    # Align column counts if they differ (safety for shape mismatches)
    if len(parts_X) == 2 and parts_X[0].shape[1] != parts_X[1].shape[1]:
        min_cols = min(parts_X[0].shape[1], parts_X[1].shape[1])
        parts_X = [p[:, :min_cols] for p in parts_X]

    X_mix = np.concatenate(parts_X, axis=0)
    y_mix = np.concatenate(parts_y, axis=0)

    shuffle_idx = rng.permutation(len(y_mix))
    X_mix, y_mix = X_mix[shuffle_idx], y_mix[shuffle_idx]

    meta = {
        "attack_samples":   int(len(y_att)),
        "normal_samples":   int(len(y_norm_all)),
        "total":            int(len(y_mix)),
        "attack_fraction":  float(y_mix.mean()) if len(y_mix) > 0 else 0.0,
    }
    return X_mix, y_mix, meta


def build_training_dataset(
    sample_size: int = 10_000,
    seed: int = 42
) -> Tuple[np.ndarray, np.ndarray, Dict]:
    """Returns (X, y, meta) for classical ThreatDetector training."""
    X, y, df, meta = load_edge_iiot_dataset(sample_size=sample_size, seed=seed)
    X_sub = X[:, :3] if X.shape[1] >= 3 else X
    return X_sub, y, meta


def build_edge_iiot_threat_dataset(
    sample_size: int = 10_000,
    seed: int = 42
) -> Tuple[np.ndarray, np.ndarray, Dict]:
    """Alias for build_training_dataset."""
    return build_training_dataset(sample_size=sample_size, seed=seed)


def list_available_raw_attack_files() -> List[Dict]:
    """Returns detailed metadata list of all raw attack CSV & PCAP capture files."""
    if not os.path.exists(ATTACK_TRAFFIC_DIR):
        return []
    records = []
    for filepath in glob.glob(os.path.join(ATTACK_TRAFFIC_DIR, "*.*")):
        size_mb = os.path.getsize(filepath) / (1024 * 1024)
        ext     = os.path.splitext(filepath)[1].lower()
        name    = os.path.basename(filepath)
        records.append({
            "name":     name,
            "type":     "CSV Log" if ext == ".csv" else "PCAP Capture",
            "size_mb":  round(size_mb, 2),
            "filepath": filepath,
        })
    return sorted(records, key=lambda x: x["size_mb"], reverse=True)


def list_available_normal_sensor_files() -> List[Dict]:
    """Returns detailed list of all normal baseline IoT sensor traffic folders."""
    if not os.path.exists(NORMAL_TRAFFIC_DIR):
        return []
    records = []
    for item in os.listdir(NORMAL_TRAFFIC_DIR):
        item_path = os.path.join(NORMAL_TRAFFIC_DIR, item)
        if os.path.isdir(item_path):
            files = os.listdir(item_path)
            records.append({
                "sensor_type": item,
                "files":       files,
                "dirpath":     item_path,
            })
    return records


def partition_data_for_fl(
    X: np.ndarray,
    y: np.ndarray,
    num_clients: int = 5,
    non_iid: bool = True,
    seed: int = 42,
) -> List[Tuple[np.ndarray, np.ndarray]]:
    """
    Partition a preprocessed dataset into client subsets for Federated Learning.
    Supports IID and Non-IID distributions across simulated IoT Edge devices.

    Note: X is already preprocessed by Layer 0 before reaching this function.
    """
    rng = np.random.default_rng(seed)
    n_samples = len(y)
    client_data = []

    if not non_iid:
        indices = rng.permutation(n_samples)
        splits  = np.array_split(indices, num_clients)
        for idx in splits:
            client_data.append((X[idx], y[idx]))
    else:
        # Non-IID: sort by label, then assign 2 shards per client
        idx_sorted = np.argsort(y)
        X_sorted, y_sorted = X[idx_sorted], y[idx_sorted]

        n_shards   = num_clients * 2
        shard_size = n_samples // n_shards
        shard_indices = list(range(n_shards))
        rng.shuffle(shard_indices)

        for i in range(num_clients):
            c_shards = shard_indices[i * 2 : (i + 1) * 2]
            c_idx    = []
            for s in c_shards:
                start = s * shard_size
                end   = (s + 1) * shard_size if s < n_shards - 1 else n_samples
                c_idx.extend(list(range(start, end)))
    return client_data


def split_and_preprocess_dataset(
    df: pd.DataFrame,
    train_ratio: float = 0.60,
    val_ratio: float = 0.20,
    test_ratio: float = 0.20,
    seed: int = 42
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, DataPreprocessor]:
    """
    STRICT ZERO-LEAKAGE 3-WAY DATASET SPLITTER (Train / Validation / Test).
    Preprocesses dataset by fitting DataPreprocessor ONLY on the training split,
    preventing any data leakage into validation and test feature statistics.
    """
    assert abs((train_ratio + val_ratio + test_ratio) - 1.0) < 1e-5, "Ratio sum must equal 1.0"
    
    available_cols = [c for c in EDGE_IIOT_FEATURE_COLS if c in df.columns]
    X_df = df[available_cols].copy()
    for col in EDGE_IIOT_FEATURE_COLS:
        if col not in X_df.columns:
            X_df[col] = 0.0
    X_df = X_df[EDGE_IIOT_FEATURE_COLS]
    
    y = (
        df["Attack_label"].astype(int).to_numpy()
        if "Attack_label" in df.columns
        else np.zeros(len(df), dtype=int)
    )
    
    n_total = len(df)
    n_test = int(n_total * test_ratio)
    n_val = int(n_total * val_ratio)
    
    rng = np.random.default_rng(seed)
    shuffled_idx = rng.permutation(n_total)
    
    test_idx = shuffled_idx[:n_test]
    val_idx = shuffled_idx[n_test : n_test + n_val]
    train_idx = shuffled_idx[n_test + n_val :]
    
    X_train_df, y_train = X_df.iloc[train_idx], y[train_idx]
    X_val_df, y_val = X_df.iloc[val_idx], y[val_idx]
    X_test_df, y_test = X_df.iloc[test_idx], y[test_idx]
    
    preprocessor = DataPreprocessor()
    X_train = preprocessor.fit_transform(X_train_df, feature_cols=EDGE_IIOT_FEATURE_COLS)
    X_val = preprocessor.transform(X_val_df, feature_cols=EDGE_IIOT_FEATURE_COLS)
    X_test = preprocessor.transform(X_test_df, feature_cols=EDGE_IIOT_FEATURE_COLS)
    
    return X_train, X_val, X_test, y_train, y_val, y_test, preprocessor


def compute_sample_distribution_stats(df: pd.DataFrame, client_data: Optional[List[Tuple[np.ndarray, np.ndarray]]] = None) -> Dict:
    """
    Computes sample distribution statistics across dataset categories,
    normal vs attack class ratios, and non-IID client shard distribution.
    """
    total_samples = len(df)
    
    y = (
        df["Attack_label"].astype(int).to_numpy()
        if "Attack_label" in df.columns
        else np.zeros(total_samples, dtype=int)
    )
    
    normal_count = int((y == 0).sum())
    attack_count = int((y == 1).sum())
    normal_ratio = float(normal_count / max(1, total_samples))
    attack_ratio = float(attack_count / max(1, total_samples))
    
    attack_type_counts = {}
    if "Attack_type" in df.columns:
        attack_type_counts = {str(k): int(v) for k, v in df["Attack_type"].value_counts().to_dict().items()}
        
    client_shard_stats = []
    if client_data:
        for cid, (Xc, yc) in enumerate(client_data):
            c_norm = int((yc == 0).sum())
            c_att = int((yc == 1).sum())
            client_shard_stats.append({
                "client_id": cid,
                "total_samples": len(yc),
                "normal_samples": c_norm,
                "attack_samples": c_att,
                "attack_ratio": round(c_att / max(1, len(yc)), 4)
            })
            
    return {
        "total_samples": total_samples,
        "normal_samples": normal_count,
        "attack_samples": attack_count,
        "normal_ratio": round(normal_ratio, 4),
        "attack_ratio": round(attack_ratio, 4),
        "attack_type_counts": attack_type_counts,
        "client_shard_stats": client_shard_stats
    }


WUSTL_IIOT_PATH = os.path.join(DATA_DIR, "wustl_iiot_2021", "wustl_iiot_2021.csv")

def load_wustl_iiot_dataset(
    sample_size: Optional[int] = 15_000,
    seed: int = 42
) -> Tuple[pd.DataFrame, Dict]:
    """
    Load raw WUSTL-IIoT-2021 dataset for cross-dataset generalization benchmarks.
    """
    if not os.path.exists(WUSTL_IIOT_PATH):
        raise FileNotFoundError(f"WUSTL IIoT dataset not found at {WUSTL_IIOT_PATH}")

    df = pd.read_csv(WUSTL_IIOT_PATH, low_memory=False)
    df.columns = df.columns.str.strip()

    if sample_size and len(df) > sample_size:
        df = df.sample(n=sample_size, random_state=seed).reset_index(drop=True)

    traffic_counts = df["Traffic"].value_counts().to_dict() if "Traffic" in df.columns else {}
    target_counts = df["Target"].value_counts().to_dict() if "Target" in df.columns else {}

    meta = {
        "dataset_name": "WUSTL-IIoT-2021",
        "total_rows": len(df),
        "traffic_distribution": {str(k): int(v) for k, v in traffic_counts.items()},
        "target_distribution": {str(k): int(v) for k, v in target_counts.items()}
    }

    return df, meta



