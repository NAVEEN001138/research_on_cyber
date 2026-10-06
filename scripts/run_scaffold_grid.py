"""
Grid evaluation script for SCAFFOLD vs FedAvg-SGD
Evaluates lr in {0.01, 0.02, 0.05} and norm in {'batch', 'group'}.
Seed 42, random split, 30 rounds, K=20 steps, C=0.5 (10/20 clients).
Outputs to results/logs/scaffold_grid.log.
"""

import os
import sys
import copy
import time
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import roc_auc_score as _roc_auc, f1_score as _f1

# Ensure workspace root is in path
WORKSPACE_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if WORKSPACE_ROOT not in sys.path:
    sys.path.insert(0, WORKSPACE_ROOT)

from utils.seeding import set_seed
from utils.metrics import predict_in_batches
from layer1_telemetry.data_loader import (
    EDGE_IIOT_PATH,
    EDGE_IIOT_FEATURE_COLS,
    partition_data_for_fl
)
from layer2_detection.tcn_attention import LightweightTCNAttention
from layer2_detection.scaffold_fl import SCAFFOLDClient, SCAFFOLDServer
from layer2_detection.secure_aggregation import (
    compute_dense_update,
    apply_topk_sparsification
)

LOG_PATH = os.path.join(WORKSPACE_ROOT, "results", "logs", "scaffold_grid.log")
os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)


def log(msg, file_handle):
    print(msg, flush=True)
    file_handle.write(msg + "\n")
    file_handle.flush()


def run_experiment(algo, lr, norm, X_tr, y_tr, X_te, y_te, f_log):
    seed = 42
    set_seed(seed)
    num_clients = 20
    participation_rate = 0.5
    num_rounds = 30
    local_steps = 20
    batch_size = 64
    k_part = max(1, int(num_clients * participation_rate))

    client_shards, _ = partition_data_for_fl(
        X_tr, y_tr, num_clients=num_clients, alpha=0.5, seed=seed
    )

    global_net = LightweightTCNAttention(input_dim=len(EDGE_IIOT_FEATURE_COLS), norm=norm)
    scaffold_server = SCAFFOLDServer(global_net, num_total_clients=num_clients)

    clients = [
        SCAFFOLDClient(cid, client_shards[cid][0], client_shards[cid][1])
        for cid in range(num_clients)
    ]
    client_residuals = [None for _ in range(num_clients)]

    rng = np.random.default_rng(seed)
    curve = {}

    for r in range(num_rounds):
        part_indices = rng.choice(num_clients, size=k_part, replace=False)
        client_weights = []
        client_deltas = []
        client_delta_c = []
        sample_counts = []

        curr_gw = copy.deepcopy(scaffold_server.global_model.state_dict())

        for cid in part_indices:
            client = clients[cid]
            if client.sample_count == 0:
                continue

            if algo == "SCAFFOLD":
                w_local, delta_c_k, _ = client.train_scaffold_round(
                    scaffold_server.global_model,
                    scaffold_server.c_global,
                    local_steps=local_steps,
                    lr=lr,
                    batch_size=batch_size
                )
            else:  # FedAvg-SGD
                local_m = copy.deepcopy(scaffold_server.global_model)
                local_m.train()
                opt = optim.SGD(local_m.parameters(), lr=lr)
                ds = TensorDataset(
                    torch.tensor(client.X_local, dtype=torch.float32),
                    torch.tensor(client.y_local, dtype=torch.long)
                )
                ld = DataLoader(ds, batch_size=batch_size, shuffle=True)
                ld_iter = iter(ld)
                for _ in range(local_steps):
                    try:
                        bx, by = next(ld_iter)
                    except StopIteration:
                        ld_iter = iter(ld)
                        bx, by = next(ld_iter)
                    opt.zero_grad()
                    out = local_m(bx)
                    loss = F.cross_entropy(out, by)
                    loss.backward()
                    opt.step()
                w_local = copy.deepcopy(local_m.state_dict())
                delta_c_k = {}

            delta_w = compute_dense_update(w_local, curr_gw)
            decomp_delta, sparse_payload, new_res, _, _ = apply_topk_sparsification(
                delta_w, residual=client_residuals[cid], top_k_ratio=0.3
            )
            client_residuals[cid] = new_res

            reconstructed_w = {}
            for k in curr_gw.keys():
                reconstructed_w[k] = curr_gw[k] + decomp_delta[k]

            client_weights.append(reconstructed_w)
            client_deltas.append(decomp_delta)
            client_delta_c.append(delta_c_k)
            sample_counts.append(client.sample_count)

        if algo == "SCAFFOLD":
            scaffold_server.aggregate(client_weights, client_delta_c, sample_counts)
        else:
            tot_s = sum(sample_counts)
            new_gw = {}
            for k in client_weights[0].keys():
                if not client_weights[0][k].is_floating_point():
                    new_gw[k] = client_weights[0][k].clone()
                    continue
                accum = torch.zeros_like(client_weights[0][k], dtype=torch.float32)
                for i in range(len(client_weights)):
                    accum += (sample_counts[i] / tot_s) * client_weights[i][k].float()
                new_gw[k] = accum.to(client_weights[0][k].dtype)
            scaffold_server.global_model.load_state_dict(new_gw)

        if (r + 1) % 5 == 0 or (r + 1) == num_rounds:
            _, pr_r = predict_in_batches(scaffold_server.global_model, X_te)
            auc_r = float(_roc_auc(y_te, pr_r))
            curve[r + 1] = round(auc_r, 4)

    return curve


def main():
    with open(LOG_PATH, "w") as f_log:
        log("=" * 70, f_log)
        log("SCAFFOLD vs FedAvg-SGD Grid Exploration (Seed 42, K=20, C=0.5, 30 rounds)", f_log)
        log("=" * 70, f_log)

        # 1. Load Data
        raw_df = pd.read_csv(EDGE_IIOT_PATH, low_memory=False)
        raw_df.columns = raw_df.columns.str.strip()
        sample_df = raw_df.sample(n=15000, random_state=42).reset_index(drop=True)
        X_raw = sample_df[EDGE_IIOT_FEATURE_COLS].apply(pd.to_numeric, errors="coerce").fillna(0.0).to_numpy(dtype=np.float32)
        y_raw = sample_df["Attack_label"].astype(int).to_numpy()

        X_tr, X_te, y_tr, y_te = train_test_split(
            X_raw, y_raw, test_size=0.20, random_state=42, stratify=y_raw
        )

        scaler = StandardScaler()
        X_tr = scaler.fit_transform(X_tr)
        X_te = scaler.transform(X_te)

        learning_rates = [0.01, 0.02, 0.05]
        norms = ["batch", "group"]
        results = {}

        for norm in norms:
            for lr in learning_rates:
                cfg_name = f"norm={norm}, lr={lr}"
                log(f"\n--- Testing Config: {cfg_name} ---", f_log)

                t0 = time.time()
                fedavg_curve = run_experiment("FedAvg-SGD", lr, norm, X_tr, y_tr, X_te, y_te, f_log)
                t_fedavg = time.time() - t0

                t0 = time.time()
                scaffold_curve = run_experiment("SCAFFOLD", lr, norm, X_tr, y_tr, X_te, y_te, f_log)
                t_scaffold = time.time() - t0

                results[cfg_name] = {
                    "FedAvg-SGD": fedavg_curve,
                    "SCAFFOLD": scaffold_curve,
                    "final_FedAvg": fedavg_curve[30],
                    "final_SCAFFOLD": scaffold_curve[30],
                }

                curve_str_fedavg = " -> ".join(f"{fedavg_curve[r]:.4f}" for r in [5, 10, 15, 20, 25, 30])
                curve_str_scaffold = " -> ".join(f"{scaffold_curve[r]:.4f}" for r in [5, 10, 15, 20, 25, 30])
                log(f"  FedAvg-SGD curve [r=5..30]: {curve_str_fedavg} | Final: {fedavg_curve[30]:.4f} ({t_fedavg:.1f}s)", f_log)
                log(f"  SCAFFOLD   curve [r=5..30]: {curve_str_scaffold} | Final: {scaffold_curve[30]:.4f} ({t_scaffold:.1f}s)", f_log)

        log("\n" + "=" * 70, f_log)
        log("SUMMARY OF GRID RESULTS", f_log)
        log("=" * 70, f_log)
        log(f"{'Config':<25} | {'FedAvg Final':<12} | {'SCAFFOLD Final':<14} | {'Diff':<8} | {'Stable?':<8}", f_log)
        log("-" * 75, f_log)

        for cfg_name, res in results.items():
            sc_curve = res["SCAFFOLD"]
            post15_rounds = [15, 20, 25, 30]
            # Check stability: no drop > 0.05 after round 15
            max_drop_after_15 = 0.0
            for i in range(len(post15_rounds) - 1):
                r_prev = post15_rounds[i]
                r_next = post15_rounds[i + 1]
                drop = sc_curve[r_prev] - sc_curve[r_next]
                if drop > max_drop_after_15:
                    max_drop_after_15 = drop

            # Also check if round 20, 25, 30 drop more than 0.05 below round 15
            drop_below_15 = max(0.0, max(sc_curve[15] - sc_curve[r] for r in [20, 25, 30]))
            is_stable = (max_drop_after_15 <= 0.05) and (drop_below_15 <= 0.05)
            meets_auc = (res["final_SCAFFOLD"] >= res["final_FedAvg"] - 0.01)

            diff = res["final_SCAFFOLD"] - res["final_FedAvg"]
            verdict = "YES" if (is_stable and meets_auc) else ("STABLE_LOW" if is_stable else "NO")
            log(f"{cfg_name:<25} | {res['final_FedAvg']:<12.4f} | {res['final_SCAFFOLD']:<14.4f} | {diff:<+8.4f} | {verdict}", f_log)

        log("=" * 70, f_log)


if __name__ == "__main__":
    main()
