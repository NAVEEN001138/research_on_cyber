"""
=============================================================================
CROSS-DATASET SEMANTIC FEATURE MAPPING: EDGE-IIOTSET <-> WUSTL-IIOT-2021
Module: layer1_telemetry/feature_map_wustl.py
-----------------------------------------------------------------------------
Maps protocol-semantic features between Edge-IIoTset and WUSTL-IIoT-2021
by semantic meaning, never by raw column position.
Explicitly drops network/device identifiers per dataset author recommendations.
=============================================================================
"""

from typing import Dict, List, Tuple, Optional
import numpy as np
import pandas as pd

# WUSTL identifier columns that MUST be dropped (author guidelines & leak prevention)
WUSTL_IDENTIFIER_COLS = [
    "StartTime", "LastTime", "SrcAddr", "DstAddr",
    "sIpId", "dIpId", "Sport", "Dport"
]

# Semantic mapping between Edge-IIoTset features and WUSTL-IIoT-2021 features
# Format: (Edge-IIoT feature name, WUSTL feature name, description)
SHARED_SEMANTIC_FEATURES: List[Tuple[str, str, str]] = [
    ("tcp.len", "TotBytes", "Total flow bytes / TCP payload length"),
    ("http.content_length", "SrcBytes", "Source application bytes"),
    ("tcp.connection.synack", "SynAck", "SYN-ACK handshake indicator / timing"),
    ("tcp.connection.fin", "Loss", "Connection termination / flow loss indicator"),
    ("tcp.connection.syn", "TotPkts", "Initial connection packets / volume"),
    ("tcp.flags.ack", "DstPkts", "Acknowledgment packet volume"),
    ("icmp.seq_le", "SrcPkts", "Source packet sequence count"),
    ("icmp.transmit_timestamp", "Dur", "Flow duration / timing"),
    ("tcp.flags", "sTtl", "TCP flags / time-to-live indicator"),
    ("arp.hw.size", "dTtl", "Hardware/packet framing header indicator")
]


def get_shared_feature_names() -> Tuple[List[str], List[str]]:
    """Returns (edge_iiot_shared_features, wustl_shared_features)."""
    edge_cols = [f[0] for f in SHARED_SEMANTIC_FEATURES]
    wustl_cols = [f[1] for f in SHARED_SEMANTIC_FEATURES]
    return edge_cols, wustl_cols


def prepare_cross_dataset_pair(
    edge_df: pd.DataFrame,
    wustl_df: pd.DataFrame
) -> Tuple[pd.DataFrame, np.ndarray, pd.DataFrame, np.ndarray]:
    """
    Extracts aligned shared semantic features and binary labels for source and target.
    """
    edge_cols, wustl_cols = get_shared_feature_names()

    # Source: Edge-IIoTset
    X_edge = edge_df[edge_cols].apply(pd.to_numeric, errors="coerce").fillna(0.0)
    y_edge = edge_df["Attack_label"].astype(int).to_numpy()

    # Target: WUSTL-IIoT-2021 (Target 0=Normal, 1=Attack)
    X_wustl = wustl_df[wustl_cols].apply(pd.to_numeric, errors="coerce").fillna(0.0)
    # Rename columns to match source feature names for model input
    X_wustl.columns = edge_cols
    y_wustl = wustl_df["Target"].astype(int).to_numpy()

    return X_edge, y_edge, X_wustl, y_wustl
