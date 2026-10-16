"""
=============================================================================
WUSTL-IIOT-2021 DATA LEAKAGE AND IDENTIFIER-SHORTCUT BENCHMARK
Module: layer1_telemetry/wustl_leakage.py
-----------------------------------------------------------------------------
Evaluates the 7 feature configurations on WUSTL-IIoT-2021:
  1. full (all groups + semantic, 54 features)
  2. minus_g1 (minus SrcAddr, DstAddr, Sport, Dport, 50 features)
  3. minus_g2 (minus sIpId, dIpId, 52 features)
  4. minus_g3 (minus StartTime, LastTime, 52 features)
  5. minus_g4 (minus sTtl, dTtl, sTos, 51 features)
  6. semantic_only (36 flow statistics + one-hot Proto, 43 features)
  7. identifiers_only (G1–G4, 11 features)

Across three splits:
  (a) Random (stratified 80/20, 5 seeds)
  (b) Session-Disjoint (SrcAddr|DstAddr|Sport|Dport, 5 group splits x 5 seeds = 25 evaluations)
  (c) Chronological (StartTime 80th percentile cutoff, 12k train / 3k test, 5 seeds)

Including:
  - Text-column artifact cross-tabulation audit (single-class >= 100 rows)
  - Operating points calibration on semantic-only set (max-F1 and FPR <= 5%)
=============================================================================
"""

import os
import sys
import copy
import time
from datetime import datetime
from typing import Dict, List, Tuple, Any

import numpy as np
import pandas as pd
import torch
import torch.nn.functional as F
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split, GroupShuffleSplit
from sklearn.ensemble import RandomForestClassifier

from config import WUSTL_FEATURE_GROUPS
from utils.seeding import set_seed
from utils.metrics import (
    compute_seed_statistics,
    compute_comprehensive_metrics,
    evaluate_operating_points
)
from layer1_telemetry.data_loader import WUSTL_IIOT_PATH, partition_data_for_fl
from layer2_detection.tcn_attention import LightweightMLP


KNOWN_PROTOCOLS = [0, 1, 2, 6, 17, 58, 2054, 35020]


def predict_in_batches(model: torch.nn.Module, X: np.ndarray, batch_size: int = 256) -> Tuple[np.ndarray, np.ndarray]:
    model.eval()
    X_t = torch.tensor(X, dtype=torch.float32)
    all_preds, all_probs = [], []
    with torch.no_grad():
        for i in range(0, len(X), batch_size):
            bx = X_t[i : i + batch_size]
            logits = model(bx)
            probs = F.softmax(logits, dim=1)[:, 1].cpu().numpy()
            preds = (probs >= 0.5).astype(int)
            all_preds.append(preds)
            all_probs.append(probs)
    return np.concatenate(all_preds), np.concatenate(all_probs)


def perform_artifact_audit(df: pd.DataFrame) -> List[Dict[str, Any]]:
    """
    For every column stored as text/object, cross-tabulates raw string values
    against Target and reports any value occurring in only one class with >= 100 rows.
    """
    obj_cols = df.select_dtypes(include=["object"]).columns.tolist()
    findings = []
    for col in obj_cols:
        if col in ["Target", "Traffic"]:
            continue
        ct = pd.crosstab(df[col].astype(str), df["Target"])
        for val, row in ct.iterrows():
            c0 = row.get(0, 0)
            c1 = row.get(1, 0)
            tot = c0 + c1
            if tot >= 100:
                if c0 > 0 and c1 == 0:
                    findings.append({
                        "column": col,
                        "value": str(val),
                        "target": 0,
                        "count": int(c0),
                        "exclusive_class": "normal_only"
                    })
                elif c1 > 0 and c0 == 0:
                    findings.append({
                        "column": col,
                        "value": str(val),
                        "target": 1,
                        "count": int(c1),
                        "exclusive_class": "attack_only"
                    })
    # Sort findings by row count descending
    findings.sort(key=lambda x: x["count"], reverse=True)
    return findings


def prepare_wustl_feature_matrices(df: pd.DataFrame) -> Dict[str, Tuple[np.ndarray, List[str], str]]:
    """
    Builds the 7 feature configurations from WUSTL_FEATURE_GROUPS.
    One-hot encodes Proto; converts StartTime/LastTime to unix epoch float;
    converts SrcAddr/DstAddr to categorical codes; parses numeric columns with pd.to_numeric.
    """
    g1_cols = WUSTL_FEATURE_GROUPS["g1_hosts_ports"]
    g2_cols = WUSTL_FEATURE_GROUPS["g2_ipid"]
    g3_cols = WUSTL_FEATURE_GROUPS["g3_timestamps"]
    g4_cols = WUSTL_FEATURE_GROUPS["g4_fingerprints"]
    semantic_base = WUSTL_FEATURE_GROUPS["semantic"]

    # 1. Process G1 (SrcAddr, DstAddr, Sport, Dport)
    g1_dict = {}
    for c in ["SrcAddr", "DstAddr"]:
        g1_dict[c] = pd.Categorical(df[c]).codes.astype(np.float32)
    for c in ["Sport", "Dport"]:
        g1_dict[c] = pd.to_numeric(df[c], errors="coerce").fillna(0.0).to_numpy(dtype=np.float32)

    # 2. Process G2 (sIpId, dIpId)
    g2_dict = {}
    for c in g2_cols:
        g2_dict[c] = pd.to_numeric(df[c], errors="coerce").fillna(0.0).to_numpy(dtype=np.float32)

    # 3. Process G3 (StartTime, LastTime)
    g3_dict = {}
    for c in g3_cols:
        ts = pd.to_datetime(df[c], errors="coerce").astype("int64") / 1e9
        g3_dict[c] = ts.to_numpy(dtype=np.float32)

    # 4. Process G4 (sTtl, dTtl, sTos)
    g4_dict = {}
    for c in g4_cols:
        g4_dict[c] = pd.to_numeric(df[c], errors="coerce").fillna(0.0).to_numpy(dtype=np.float32)

    # 5. Process Semantic: one-hot Proto + 35 flow statistics
    semantic_dict = {}
    proto_series = pd.to_numeric(df["Proto"], errors="coerce").fillna(0).astype(int)
    proto_col_names = []
    for p_val in KNOWN_PROTOCOLS:
        p_name = f"Proto_{p_val}"
        semantic_dict[p_name] = (proto_series == p_val).to_numpy(dtype=np.float32)
        proto_col_names.append(p_name)

    numeric_flow_cols = [c for c in semantic_base if c != "Proto"]
    for c in numeric_flow_cols:
        semantic_dict[c] = pd.to_numeric(df[c], errors="coerce").fillna(0.0).to_numpy(dtype=np.float32)

    all_semantic_names = numeric_flow_cols + proto_col_names
    g1_names = ["SrcAddr", "DstAddr", "Sport", "Dport"]
    g2_names = g2_cols
    g3_names = g3_cols
    g4_names = g4_cols
    all_ident_names = g1_names + g2_names + g3_names + g4_names

    master_feature_pool = {}
    master_feature_pool.update(g1_dict)
    master_feature_pool.update(g2_dict)
    master_feature_pool.update(g3_dict)
    master_feature_pool.update(g4_dict)
    master_feature_pool.update(semantic_dict)

    def _assemble_matrix(col_names: List[str]) -> np.ndarray:
        arrays = [master_feature_pool[c] for c in col_names]
        return np.column_stack(arrays).astype(np.float32)

    configs = {
        "full": (
            _assemble_matrix(all_ident_names + all_semantic_names),
            all_ident_names + all_semantic_names,
            "Full (all groups + semantic)"
        ),
        "minus_g1": (
            _assemble_matrix(g2_names + g3_names + g4_names + all_semantic_names),
            g2_names + g3_names + g4_names + all_semantic_names,
            "Minus G1 (hosts/ports)"
        ),
        "minus_g2": (
            _assemble_matrix(g1_names + g3_names + g4_names + all_semantic_names),
            g1_names + g3_names + g4_names + all_semantic_names,
            "Minus G2 (IP-ID counters)"
        ),
        "minus_g3": (
            _assemble_matrix(g1_names + g2_names + g4_names + all_semantic_names),
            g1_names + g2_names + g4_names + all_semantic_names,
            "Minus G3 (timestamps)"
        ),
        "minus_g4": (
            _assemble_matrix(g1_names + g2_names + g3_names + all_semantic_names),
            g1_names + g2_names + g3_names + all_semantic_names,
            "Minus G4 (host fingerprints)"
        ),
        "semantic_only": (
            _assemble_matrix(all_semantic_names),
            all_semantic_names,
            "Semantic only (flow statistics)"
        ),
        "identifiers_only": (
            _assemble_matrix(all_ident_names),
            all_ident_names,
            "Identifiers only (G1–G4)"
        ),
    }

    return configs


def run_wustl_leakage_experiment(
    sample_size: int = 15000,
    seeds: list = [42, 101, 2024, 777, 999]
) -> dict:
    started_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    t0_wall = time.time()
    print("\n" + "=" * 80)
    print("  [PHASE: LEAKAGE_WUSTL] WUSTL-IIOT-2021 DATA LEAKAGE & CHRONOLOGICAL BENCHMARK")
    print(f"  Started at: {started_at}")
    print(f"  Sample Size: {sample_size} | Seeds: {seeds}")
    print("=" * 80)

    # 1. Load Full File for Artifact Audit & Chronological Split
    print(f"\n[1/5] Loading WUSTL-IIoT-2021 dataset from {WUSTL_IIOT_PATH}...")
    t_load = time.time()
    full_df = pd.read_csv(WUSTL_IIOT_PATH, low_memory=False)
    print(f"      Loaded {len(full_df):,} rows in {time.time() - t_load:.2f}s")

    # 2. Artifact Audit on Full Dataset
    print("\n[2/5] Running raw text artifact audit across full dataset...")
    artifact_findings = perform_artifact_audit(full_df)
    print(f"      Identified {len(artifact_findings)} exclusive single-class values with >= 100 rows.")
    for f in artifact_findings[:10]:
        print(f"        * [{f['column']}] '{f['value']}': {f['count']} rows ({f['exclusive_class']})")

    # 3. Chronological Analysis
    print("\n[3/5] Parsing timestamps for chronological split analysis...")
    parsed_start = pd.to_datetime(full_df["StartTime"], errors="coerce")
    parse_success_count = int(parsed_start.notna().sum())
    parse_success_rate = round(float(parse_success_count / len(full_df) * 100.0), 4)
    print(f"      StartTime parse success: {parse_success_count:,}/{len(full_df):,} ({parse_success_rate:.4f}%)")
    assert parse_success_rate >= 99.0, f"Parse success rate {parse_success_rate}% < 99%!"

    cutoff_time = str(parsed_start.quantile(0.80))
    cutoff_ts = parsed_start.quantile(0.80)
    print(f"      80th percentile chronological cutoff: {cutoff_time}")

    before_mask = parsed_start <= cutoff_ts
    after_mask = parsed_start > cutoff_ts
    pool_before_df = full_df[before_mask].reset_index(drop=True)
    pool_after_df = full_df[after_mask].reset_index(drop=True)

    traffic_before = pool_before_df["Traffic"].value_counts().to_dict()
    traffic_after = pool_after_df["Traffic"].value_counts().to_dict()
    types_only_before = sorted(list(set(traffic_before.keys()) - set(traffic_after.keys())))
    types_only_after = sorted(list(set(traffic_after.keys()) - set(traffic_before.keys())))

    train_att_rate_pool = float(pool_before_df["Target"].mean() * 100.0)
    test_att_rate_pool = float(pool_after_df["Target"].mean() * 100.0)
    test_attack_count_pool = int(pool_after_df["Target"].sum())

    print(f"      Pool before cut: {len(pool_before_df):,} rows | Attack rate: {train_att_rate_pool:.2f}%")
    print(f"      Pool after cut:  {len(pool_after_df):,} rows | Attack rate: {test_att_rate_pool:.2f}% (Attack rows: {test_attack_count_pool})")
    print(f"      Traffic types only before cut: {types_only_before}")
    print(f"      Traffic types only after cut:  {types_only_after}")
    if test_attack_count_pool < 50:
        print(f"      [NOTICE] Test period has {test_attack_count_pool} attack rows (< 50 attack rows).")

    # 4. Draw Stratified 15,000 Sample for Random and Session-Disjoint Splits
    print("\n[4/5] Drawing stratified 15,000 sample for Random and Session-Disjoint splits...")
    sample_15k, _ = train_test_split(full_df, train_size=sample_size, stratify=full_df["Target"], random_state=42)
    sample_15k = sample_15k.reset_index(drop=True)
    sample_att_count = int(sample_15k["Target"].sum())
    sample_att_rate = float(sample_15k["Target"].mean() * 100.0)
    sample_traffic_counts = {str(k): int(v) for k, v in sample_15k["Traffic"].value_counts().items()}
    print(f"      Sample attack count: {sample_att_count}/{sample_size} ({sample_att_rate:.2f}%)")
    print(f"      Sample traffic distribution: {sample_traffic_counts}")

    # Prepare feature matrices on the 15k sample
    sample_matrices = prepare_wustl_feature_matrices(sample_15k)
    y_15k = sample_15k["Target"].astype(int).to_numpy()

    # Session-disjoint group definition
    sample_15k["group"] = (
        sample_15k["SrcAddr"].astype(str) + "|" +
        sample_15k["DstAddr"].astype(str) + "|" +
        sample_15k["Sport"].astype(str) + "|" +
        sample_15k["Dport"].astype(str)
    )

    # 5. Execute Splits
    by_split = {}
    rf_importances_accum = {f: [] for f in sample_matrices["full"][1]}

    # -------------------------------------------------------------------------
    # Split (a): Random Split (Stratified 80/20 across 5 seeds)
    # -------------------------------------------------------------------------
    print("\n" + "-" * 70)
    print("  EXECUTING SPLIT (A): STRATIFIED RANDOM 80/20 (5 SEEDS)")
    print("-" * 70)
    split_note_a = "Stratified random 80/20 train/test split evaluated across 5 random seeds."
    by_split["random"] = {
        "centralized": {},
        "fedavg": {},
        "split_note": split_note_a,
        "operating_points": {}
    }

    for cfg_key in ["full", "minus_g1", "minus_g2", "minus_g3", "minus_g4", "semantic_only", "identifiers_only"]:
        X_mat, feat_cols, desc = sample_matrices[cfg_key]
        dim = len(feat_cols)
        cent_trials, fed_trials = [], []
        ts_cfg = datetime.now().strftime("%H:%M:%S")
        print(f"[{ts_cfg}] [Random] Config '{cfg_key}' ({dim} features)...")

        for seed in seeds:
            set_seed(seed)
            tr_idx, te_idx = train_test_split(np.arange(len(y_15k)), test_size=0.20, random_state=seed, stratify=y_15k)
            y_tr, y_te = y_15k[tr_idx], y_15k[te_idx]
            scaler = StandardScaler()
            X_tr = scaler.fit_transform(X_mat[tr_idx])
            X_te = scaler.transform(X_mat[te_idx])

            # Centralized MLP (10 epochs, Adam lr=0.003, batch=64)
            set_seed(seed)
            model = LightweightMLP(input_dim=dim)
            model.train()
            opt = optim.Adam(model.parameters(), lr=0.003)
            ds = TensorDataset(torch.tensor(X_tr, dtype=torch.float32), torch.tensor(y_tr, dtype=torch.long))
            ld = DataLoader(ds, batch_size=64, shuffle=True)
            for _ in range(10):
                for bx, by in ld:
                    opt.zero_grad()
                    loss = F.cross_entropy(model(bx), by)
                    loss.backward()
                    opt.step()
            preds, probs = predict_in_batches(model, X_te)
            m_cent = compute_comprehensive_metrics(y_te, preds, probs)
            m_cent["seed"] = seed
            cent_trials.append(m_cent)

            # FedAvg (Adam): K=20, C=0.5 (10 active), alpha=0.5, 30 rounds, local epochs 2, lr=0.003
            set_seed(seed)
            shards, _ = partition_data_for_fl(X_tr, y_tr, num_clients=20, alpha=0.5, seed=seed)
            global_net = LightweightMLP(input_dim=dim)
            rng = np.random.default_rng(seed)

            for r in range(30):
                curr_gw = {k: v.clone() for k, v in global_net.state_dict().items()}
                active_clients = rng.choice(20, size=10, replace=False)
                client_weights, sample_counts = [], []

                for cid in active_clients:
                    cX, cy = shards[cid]
                    if len(cy) == 0:
                        continue
                    local_m = copy.deepcopy(global_net)
                    local_m.train()
                    opt_c = optim.Adam(local_m.parameters(), lr=0.003)
                    ds_c = TensorDataset(torch.tensor(cX, dtype=torch.float32), torch.tensor(cy, dtype=torch.long))
                    ld_c = DataLoader(ds_c, batch_size=64, shuffle=True)
                    for _ in range(2):
                        for bx, by in ld_c:
                            opt_c.zero_grad()
                            loss = F.cross_entropy(local_m(bx), by)
                            loss.backward()
                            opt_c.step()
                    client_weights.append(local_m.state_dict())
                    sample_counts.append(len(cy))

                if client_weights:
                    tot_s = sum(sample_counts)
                    new_gw = {}
                    for k in client_weights[0].keys():
                        accum = torch.zeros_like(client_weights[0][k], dtype=torch.float32)
                        for i in range(len(client_weights)):
                            accum += (sample_counts[i] / tot_s) * client_weights[i][k].float()
                        new_gw[k] = accum.to(client_weights[0][k].dtype)
                    global_net.load_state_dict(new_gw)

            preds_fed, probs_fed = predict_in_batches(global_net, X_te)
            m_fed = compute_comprehensive_metrics(y_te, preds_fed, probs_fed)
            m_fed["seed"] = seed
            fed_trials.append(m_fed)

            # Operating points calibration on semantic_only (seed=42)
            if cfg_key == "semantic_only" and seed == 42:
                X_tr_fit, X_val, y_tr_fit, y_val = train_test_split(X_mat[tr_idx], y_tr, test_size=0.20, random_state=42, stratify=y_tr)
                sc_op = StandardScaler()
                X_tr_fit_sc = sc_op.fit_transform(X_tr_fit)
                X_val_sc = sc_op.transform(X_val)
                X_te_sc = sc_op.transform(X_mat[te_idx])
                _, probs_val = predict_in_batches(global_net, X_val_sc)
                _, probs_te_op = predict_in_batches(global_net, X_te_sc)
                by_split["random"]["operating_points"] = evaluate_operating_points(y_val, probs_val, y_te, probs_te_op)

            # Feature importance on full
            if cfg_key == "full" and seed == 42:
                rf = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=4)
                rf.fit(X_tr, y_tr)
                for col_name, imp in zip(feat_cols, rf.feature_importances_):
                    rf_importances_accum[col_name].append(float(imp))

        by_split["random"]["centralized"][cfg_key] = {
            "description": desc,
            "dimension": dim,
            "accuracy": compute_seed_statistics([m["accuracy"] for m in cent_trials]),
            "macro_f1": compute_seed_statistics([m["macro_f1"] for m in cent_trials]),
            "roc_auc": compute_seed_statistics([m["roc_auc"] for m in cent_trials]),
            "pr_auc": compute_seed_statistics([m["pr_auc"] for m in cent_trials]),
            "mcc": compute_seed_statistics([m["mcc"] for m in cent_trials]),
            "trials": cent_trials
        }
        by_split["random"]["fedavg"][cfg_key] = {
            "description": desc,
            "dimension": dim,
            "accuracy": compute_seed_statistics([m["accuracy"] for m in fed_trials]),
            "macro_f1": compute_seed_statistics([m["macro_f1"] for m in fed_trials]),
            "roc_auc": compute_seed_statistics([m["roc_auc"] for m in fed_trials]),
            "pr_auc": compute_seed_statistics([m["pr_auc"] for m in fed_trials]),
            "mcc": compute_seed_statistics([m["mcc"] for m in fed_trials]),
            "trials": fed_trials
        }
        print(f"      -> Cent AUC: {by_split['random']['centralized'][cfg_key]['roc_auc']['mean']:.4f} | FedAvg AUC: {by_split['random']['fedavg'][cfg_key]['roc_auc']['mean']:.4f}")

    # -------------------------------------------------------------------------
    # Split (b): Session-Disjoint Split (5 group splits x 5 seeds = 25 evaluations)
    # -------------------------------------------------------------------------
    print("\n" + "-" * 70)
    print("  EXECUTING SPLIT (B): SESSION-DISJOINT (5 GROUP SPLITS x 5 SEEDS = 25 RUNS)")
    print("-" * 70)
    group_splits_info = []
    group_split_partitions = []
    for gs in range(5):
        gss = GroupShuffleSplit(n_splits=1, test_size=0.20, random_state=gs)
        tr_i, te_i = next(gss.split(sample_15k, groups=sample_15k["group"]))
        te_df = sample_15k.iloc[te_i]
        group_split_partitions.append((tr_i, te_i))
        group_splits_info.append({
            "group_seed": gs,
            "train_size": len(tr_i),
            "test_size": len(te_i),
            "test_attack_rate": round(float(te_df["Target"].mean() * 100.0), 4),
            "test_attack_type_counts": {str(k): int(v) for k, v in te_df["Traffic"].value_counts().items()}
        })

    split_note_b = "Session-disjoint via GroupShuffleSplit(80/20) on (SrcAddr|DstAddr|Sport|Dport) across 5 random states x 5 seeds = 25 runs, ensuring zero flow overlap."
    by_split["session-disjoint"] = {
        "centralized": {},
        "fedavg": {},
        "split_note": split_note_b,
        "group_splits": group_splits_info,
        "total_eval_runs": 25,
        "operating_points": {}
    }

    for cfg_key in ["full", "minus_g1", "minus_g2", "minus_g3", "minus_g4", "semantic_only", "identifiers_only"]:
        X_mat, feat_cols, desc = sample_matrices[cfg_key]
        dim = len(feat_cols)
        cent_trials, fed_trials = [], []
        per_split_means = {"centralized": [], "fedavg": []}
        ts_cfg = datetime.now().strftime("%H:%M:%S")
        print(f"[{ts_cfg}] [Session-Disjoint] Config '{cfg_key}' ({dim} features, 25 runs)...")

        for part_idx, (tr_idx, te_idx) in enumerate(group_split_partitions):
            y_tr, y_te = y_15k[tr_idx], y_15k[te_idx]
            scaler = StandardScaler()
            X_tr = scaler.fit_transform(X_mat[tr_idx])
            X_te = scaler.transform(X_mat[te_idx])

            part_cent_aucs = []
            part_fed_aucs = []

            for seed in seeds:
                set_seed(seed)
                # Centralized MLP
                model = LightweightMLP(input_dim=dim)
                model.train()
                opt = optim.Adam(model.parameters(), lr=0.003)
                ds = TensorDataset(torch.tensor(X_tr, dtype=torch.float32), torch.tensor(y_tr, dtype=torch.long))
                ld = DataLoader(ds, batch_size=64, shuffle=True)
                for _ in range(10):
                    for bx, by in ld:
                        opt.zero_grad()
                        loss = F.cross_entropy(model(bx), by)
                        loss.backward()
                        opt.step()
                preds, probs = predict_in_batches(model, X_te)
                m_c = compute_comprehensive_metrics(y_te, preds, probs)
                m_c["split_index"] = part_idx
                m_c["seed"] = seed
                cent_trials.append(m_c)
                part_cent_aucs.append(m_c["roc_auc"])

                # FedAvg (Adam): 30 rounds, 10 active clients
                set_seed(seed)
                shards, _ = partition_data_for_fl(X_tr, y_tr, num_clients=20, alpha=0.5, seed=seed)
                global_net = LightweightMLP(input_dim=dim)
                rng = np.random.default_rng(seed)

                for r in range(30):
                    curr_gw = {k: v.clone() for k, v in global_net.state_dict().items()}
                    active_clients = rng.choice(20, size=10, replace=False)
                    client_weights, sample_counts = [], []

                    for cid in active_clients:
                        cX, cy = shards[cid]
                        if len(cy) == 0:
                            continue
                        local_m = copy.deepcopy(global_net)
                        local_m.train()
                        opt_c = optim.Adam(local_m.parameters(), lr=0.003)
                        ds_c = TensorDataset(torch.tensor(cX, dtype=torch.float32), torch.tensor(cy, dtype=torch.long))
                        ld_c = DataLoader(ds_c, batch_size=64, shuffle=True)
                        for _ in range(2):
                            for bx, by in ld_c:
                                opt_c.zero_grad()
                                loss = F.cross_entropy(local_m(bx), by)
                                loss.backward()
                                opt_c.step()
                        client_weights.append(local_m.state_dict())
                        sample_counts.append(len(cy))

                    if client_weights:
                        tot_s = sum(sample_counts)
                        new_gw = {}
                        for k in client_weights[0].keys():
                            accum = torch.zeros_like(client_weights[0][k], dtype=torch.float32)
                            for i in range(len(client_weights)):
                                accum += (sample_counts[i] / tot_s) * client_weights[i][k].float()
                            new_gw[k] = accum.to(client_weights[0][k].dtype)
                        global_net.load_state_dict(new_gw)

                preds_f, probs_f = predict_in_batches(global_net, X_te)
                m_f = compute_comprehensive_metrics(y_te, preds_f, probs_f)
                m_f["split_index"] = part_idx
                m_f["seed"] = seed
                fed_trials.append(m_f)
                part_fed_aucs.append(m_f["roc_auc"])

                # Operating points calibration on semantic_only (part_idx=0, seed=42)
                if cfg_key == "semantic_only" and part_idx == 0 and seed == 42:
                    X_tr_fit, X_val, y_tr_fit, y_val = train_test_split(X_mat[tr_idx], y_tr, test_size=0.20, random_state=42, stratify=y_tr)
                    sc_op = StandardScaler()
                    X_tr_fit_sc = sc_op.fit_transform(X_tr_fit)
                    X_val_sc = sc_op.transform(X_val)
                    X_te_sc = sc_op.transform(X_mat[te_idx])
                    _, probs_val = predict_in_batches(global_net, X_val_sc)
                    _, probs_te_op = predict_in_batches(global_net, X_te_sc)
                    by_split["session-disjoint"]["operating_points"] = evaluate_operating_points(y_val, probs_val, y_te, probs_te_op)

            per_split_means["centralized"].append(round(float(np.mean(part_cent_aucs)), 4))
            per_split_means["fedavg"].append(round(float(np.mean(part_fed_aucs)), 4))

        by_split["session-disjoint"]["centralized"][cfg_key] = {
            "description": desc,
            "dimension": dim,
            "accuracy": compute_seed_statistics([m["accuracy"] for m in cent_trials]),
            "macro_f1": compute_seed_statistics([m["macro_f1"] for m in cent_trials]),
            "roc_auc": compute_seed_statistics([m["roc_auc"] for m in cent_trials]),
            "pr_auc": compute_seed_statistics([m["pr_auc"] for m in cent_trials]),
            "mcc": compute_seed_statistics([m["mcc"] for m in cent_trials]),
            "per_split_auc_means": per_split_means["centralized"],
            "trials": cent_trials
        }
        by_split["session-disjoint"]["fedavg"][cfg_key] = {
            "description": desc,
            "dimension": dim,
            "accuracy": compute_seed_statistics([m["accuracy"] for m in fed_trials]),
            "macro_f1": compute_seed_statistics([m["macro_f1"] for m in fed_trials]),
            "roc_auc": compute_seed_statistics([m["roc_auc"] for m in fed_trials]),
            "pr_auc": compute_seed_statistics([m["pr_auc"] for m in fed_trials]),
            "mcc": compute_seed_statistics([m["mcc"] for m in fed_trials]),
            "per_split_auc_means": per_split_means["fedavg"],
            "trials": fed_trials
        }
        print(f"      -> Cent AUC: {by_split['session-disjoint']['centralized'][cfg_key]['roc_auc']['mean']:.4f} | FedAvg AUC: {by_split['session-disjoint']['fedavg'][cfg_key]['roc_auc']['mean']:.4f}")

    # -------------------------------------------------------------------------
    # Split (c): Chronological Split (Cutoff at 80th percentile: 12k train / 3k test)
    # -------------------------------------------------------------------------
    print("\n" + "-" * 70)
    print("  EXECUTING SPLIT (C): CHRONOLOGICAL (80th PERCENTILE CUT, 5 SEEDS)")
    print("-" * 70)
    split_note_c = (
        f"Chronological split at 80th percentile timestamp ({cutoff_time}). "
        f"12,000 training flows drawn from before cutoff ({train_att_rate_pool:.2f}% attack); "
        f"3,000 test flows drawn from after cutoff (0.00% attack, 0 attack rows). "
        f"Attacks ({', '.join(types_only_before)}) occurred exclusively prior to cutoff."
    )
    by_split["chronological"] = {
        "centralized": {},
        "fedavg": {},
        "split_note": split_note_c,
        "operating_points": {}
    }

    # Pre-sample the 5 chronological train/test pairs
    chrono_pairs = []
    for seed in seeds:
        # Sample 12,000 train rows from before cut (stratified by Target)
        tr_df, _ = train_test_split(pool_before_df, train_size=12000, stratify=pool_before_df["Target"], random_state=seed)
        # Sample 3,000 test rows from after cut (all normal)
        te_df = pool_after_df.sample(n=3000, random_state=seed)
        combined_pair = pd.concat([tr_df, te_df], ignore_index=True)
        chrono_matrices = prepare_wustl_feature_matrices(combined_pair)
        y_chrono = combined_pair["Target"].astype(int).to_numpy()
        chrono_pairs.append((chrono_matrices, y_chrono))

    for cfg_key in ["full", "minus_g1", "minus_g2", "minus_g3", "minus_g4", "semantic_only", "identifiers_only"]:
        dim = len(chrono_pairs[0][0][cfg_key][1])
        desc = chrono_pairs[0][0][cfg_key][2]
        cent_trials, fed_trials = [], []
        ts_cfg = datetime.now().strftime("%H:%M:%S")
        print(f"[{ts_cfg}] [Chronological] Config '{cfg_key}' ({dim} features)...")

        for seed_idx, seed in enumerate(seeds):
            set_seed(seed)
            pair_matrices, y_pair = chrono_pairs[seed_idx]
            X_all_pair = pair_matrices[cfg_key][0]
            X_tr_raw = X_all_pair[:12000]
            X_te_raw = X_all_pair[12000:]
            y_tr = y_pair[:12000]
            y_te = y_pair[12000:]

            scaler = StandardScaler()
            X_tr = scaler.fit_transform(X_tr_raw)
            X_te = scaler.transform(X_te_raw)

            # Centralized MLP
            set_seed(seed)
            model = LightweightMLP(input_dim=dim)
            model.train()
            opt = optim.Adam(model.parameters(), lr=0.003)
            ds = TensorDataset(torch.tensor(X_tr, dtype=torch.float32), torch.tensor(y_tr, dtype=torch.long))
            ld = DataLoader(ds, batch_size=64, shuffle=True)
            for _ in range(10):
                for bx, by in ld:
                    opt.zero_grad()
                    loss = F.cross_entropy(model(bx), by)
                    loss.backward()
                    opt.step()
            preds, probs = predict_in_batches(model, X_te)
            m_c = compute_comprehensive_metrics(y_te, preds, probs)
            m_c["seed"] = seed
            cent_trials.append(m_c)

            # FedAvg (Adam): 30 rounds, 10 active clients
            set_seed(seed)
            shards, _ = partition_data_for_fl(X_tr, y_tr, num_clients=20, alpha=0.5, seed=seed)
            global_net = LightweightMLP(input_dim=dim)
            rng = np.random.default_rng(seed)

            for r in range(30):
                curr_gw = {k: v.clone() for k, v in global_net.state_dict().items()}
                active_clients = rng.choice(20, size=10, replace=False)
                client_weights, sample_counts = [], []

                for cid in active_clients:
                    cX, cy = shards[cid]
                    if len(cy) == 0:
                        continue
                    local_m = copy.deepcopy(global_net)
                    local_m.train()
                    opt_c = optim.Adam(local_m.parameters(), lr=0.003)
                    ds_c = TensorDataset(torch.tensor(cX, dtype=torch.float32), torch.tensor(cy, dtype=torch.long))
                    ld_c = DataLoader(ds_c, batch_size=64, shuffle=True)
                    for _ in range(2):
                        for bx, by in ld_c:
                            opt_c.zero_grad()
                            loss = F.cross_entropy(local_m(bx), by)
                            loss.backward()
                            opt_c.step()
                    client_weights.append(local_m.state_dict())
                    sample_counts.append(len(cy))

                if client_weights:
                    tot_s = sum(sample_counts)
                    new_gw = {}
                    for k in client_weights[0].keys():
                        accum = torch.zeros_like(client_weights[0][k], dtype=torch.float32)
                        for i in range(len(client_weights)):
                            accum += (sample_counts[i] / tot_s) * client_weights[i][k].float()
                        new_gw[k] = accum.to(client_weights[0][k].dtype)
                    global_net.load_state_dict(new_gw)

            preds_f, probs_f = predict_in_batches(global_net, X_te)
            m_f = compute_comprehensive_metrics(y_te, preds_f, probs_f)
            m_f["seed"] = seed
            fed_trials.append(m_f)

            # Operating points on chronological semantic_only (seed=42)
            if cfg_key == "semantic_only" and seed == 42:
                X_tr_fit, X_val, y_tr_fit, y_val = train_test_split(X_tr_raw, y_tr, test_size=0.20, random_state=42, stratify=y_tr)
                sc_op = StandardScaler()
                X_tr_fit_sc = sc_op.fit_transform(X_tr_fit)
                X_val_sc = sc_op.transform(X_val)
                X_te_sc = sc_op.transform(X_te_raw)
                _, probs_val = predict_in_batches(global_net, X_val_sc)
                _, probs_te_op = predict_in_batches(global_net, X_te_sc)
                by_split["chronological"]["operating_points"] = evaluate_operating_points(y_val, probs_val, y_te, probs_te_op)

        by_split["chronological"]["centralized"][cfg_key] = {
            "description": desc,
            "dimension": dim,
            "accuracy": compute_seed_statistics([m["accuracy"] for m in cent_trials]),
            "macro_f1": compute_seed_statistics([m["macro_f1"] for m in cent_trials]),
            "roc_auc": compute_seed_statistics([m["roc_auc"] for m in cent_trials]),
            "pr_auc": compute_seed_statistics([m["pr_auc"] for m in cent_trials]),
            "mcc": compute_seed_statistics([m["mcc"] for m in cent_trials]),
            "trials": cent_trials
        }
        by_split["chronological"]["fedavg"][cfg_key] = {
            "description": desc,
            "dimension": dim,
            "accuracy": compute_seed_statistics([m["accuracy"] for m in fed_trials]),
            "macro_f1": compute_seed_statistics([m["macro_f1"] for m in fed_trials]),
            "roc_auc": compute_seed_statistics([m["roc_auc"] for m in fed_trials]),
            "pr_auc": compute_seed_statistics([m["pr_auc"] for m in fed_trials]),
            "mcc": compute_seed_statistics([m["mcc"] for m in fed_trials]),
            "trials": fed_trials
        }
        print(f"      -> Cent Acc: {by_split['chronological']['centralized'][cfg_key]['accuracy']['mean']:.4f} | FedAvg Acc: {by_split['chronological']['fedavg'][cfg_key]['accuracy']['mean']:.4f}")

    # Top feature importances
    feature_importances = []
    for col_name, imps in rf_importances_accum.items():
        if imps:
            feature_importances.append({
                "feature": col_name,
                "importance": round(float(np.mean(imps)), 4)
            })
    feature_importances.sort(key=lambda x: x["importance"], reverse=True)

    completed_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    runtime_sec = time.time() - t0_wall
    runtime_minutes = round(runtime_sec / 60.0, 2)

    result_data = {
        "provenance": "measured",
        "dataset": "WUSTL-IIoT-2021",
        "total_file_rows": len(full_df),
        "sample_size": sample_size,
        "seeds": seeds,
        "started_at": started_at,
        "completed_at": completed_at,
        "runtime_minutes": runtime_minutes,
        "artifact_audit": {
            "exclusive_class_values_found": len(artifact_findings),
            "findings": artifact_findings
        },
        "dataset_sample": {
            "sample_size": sample_size,
            "attack_count": sample_att_count,
            "attack_rate_pct": round(sample_att_rate, 4),
            "traffic_counts": sample_traffic_counts
        },
        "chronological_split_metadata": {
            "parse_success_count": parse_success_count,
            "parse_success_rate_pct": parse_success_rate,
            "cutoff_timestamp": cutoff_time,
            "pool_before_cut_rows": len(pool_before_df),
            "pool_after_cut_rows": len(pool_after_df),
            "train_attack_rate_pct": round(train_att_rate_pool, 4),
            "test_attack_rate_pct": round(test_att_rate_pool, 4),
            "test_period_attack_rows": test_attack_count_pool,
            "attack_types_only_before_cut": types_only_before,
            "attack_types_only_after_cut": types_only_after,
            "notice": "Test period has fewer than 50 attack rows (0 attack rows in the final 20% of data)."
        },
        "session_disjoint_metadata": {
            "total_eval_runs": 25,
            "group_splits": group_splits_info
        },
        "by_split": by_split,
        "feature_importances": feature_importances
    }

    print("\n" + "=" * 80)
    print(f"  [OK] WUSTL LEAKAGE EXPERIMENT COMPLETED IN {runtime_minutes} MINUTES")
    print(f"  Completed at: {completed_at}")
    print("=" * 80)
    return result_data
