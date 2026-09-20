"""
=============================================================================
PAPER TABLE GENERATOR
Script: generate_paper_tables.py
-----------------------------------------------------------------------------
Reads results/RESULTS.json (the single source of truth) and writes every
manuscript table to paper/tables/*.md.

Rules (enforced here, verified by check_paper_numbers.py):
  * No number is typed by hand. Every numeric cell is formatted from a value
    in RESULTS.json with a fixed format string (never re-rounded by hand).
  * Missing keys raise KeyError. There are NO default values.
  * Every table caption states provenance, seed count and the run configuration.
  * Configuration literals that appear in tables but are not results
    (e.g. "k = 0.3", NIST key sizes) are written to
    paper/tables/_allowed_constants.json so the checker can whitelist them.
=============================================================================
"""

import os
import sys
import json
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from layer1_telemetry.data_loader import EDGE_IIOT_PATH
from run_experiments import PHASES_DIR, rebuild_results, RESULTS_FILE

TABLES_DIR = "paper/tables"
ALLOWED = set()          # config literals written into tables (not results)


# ----------------------------------------------------------------------------- helpers
def req(d, *path):
    """Strict nested lookup: raises KeyError naming the full path if anything is missing."""
    cur = d
    for k in path:
        if isinstance(cur, dict) and k in cur:
            cur = cur[k]
        else:
            raise KeyError("RESULTS.json is missing " + " -> ".join(map(str, path)))
    return cur


def f4(v): return f"{float(v):.4f}"
def f3(v): return f"{float(v):.3f}"
def f2(v): return f"{float(v):.2f}"
def f1(v): return f"{float(v):.1f}"
def pm(stat, fmt=f4): return f"{fmt(stat['mean'])} ± {fmt(stat['std'])}"
def ci(stat, fmt=f4): return f"[{fmt(stat['ci_lower'])}, {fmt(stat['ci_upper'])}]"
def kb(bytes_): return f"{float(bytes_) / 1024.0:.2f}"
def ints(v): return f"{int(v):,}"
def const(x):
    ALLOWED.add(str(x)); return str(x)


def write(name, lines):
    os.makedirs(TABLES_DIR, exist_ok=True)
    path = os.path.join(TABLES_DIR, name)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(lines) + "\n")
    print(f"  wrote {path}")


# ----------------------------------------------------------------------------- T1 dataset
def table1_dataset():
    """Computed directly from the CSV; stored as its own phase file so the checker can see it."""
    total_columns = len(pd.read_csv(EDGE_IIOT_PATH, nrows=5).columns)
    df = pd.read_csv(EDGE_IIOT_PATH, usecols=["Attack_type", "Attack_label"], low_memory=False)
    df.columns = df.columns.str.strip()
    by_type = df.groupby("Attack_type").size().sort_values(ascending=False)
    total = int(len(df)); normal = int((df["Attack_label"] == 0).sum()); attack = total - normal
    rec = {
        "provenance": "measured",
        "source_file": os.path.basename(EDGE_IIOT_PATH),
        "total_columns": total_columns,
        "total_rows": total, "normal_rows": normal, "attack_rows": attack,
        "attack_share_pct": round(attack / total * 100.0, 2),
        "per_attack_type": {k: int(v) for k, v in by_type.items()},
    }
    os.makedirs(PHASES_DIR, exist_ok=True)
    with open(os.path.join(PHASES_DIR, "dataset.json"), "w") as f:
        json.dump(rec, f, indent=2)
    rebuild_results()

    lines = ["**Table 1.** Edge-IIoTset (ML-EdgeIIoT-dataset.csv) class distribution — *provenance: measured (full file)*", "",
             "| Attack type | Rows | Share of file (%) |", "|---|---:|---:|"]
    for k, v in rec["per_attack_type"].items():
        lines.append(f"| {k} | {ints(v)} | {f2(v / total * 100)} |")
    lines.append(f"| **Total** | **{ints(total)}** | 100.00 |")
    lines.append(f"| Normal / Attack | {ints(normal)} / {ints(attack)} | {f2(normal / total * 100)} / {f2(rec['attack_share_pct'])} |")
    write("T1_dataset.md", lines)
    return rec


# ----------------------------------------------------------------------------- T2 model complexity
def table2_models(R):
    fl = req(R, "fl_benchmarks"); prof = req(fl, "model_profiles")
    lines = [f"**Table 2.** Model complexity (input dim = {req(fl, 'features_count')}) — *provenance: measured (parameter count and FLOPs profiled in code)*", "",
             "| Model | Trainable parameters | Size (KB, float32) | GFLOPs / sample |", "|---|---:|---:|---:|"]
    for name in ["MLP", "CNN_1D", "TCN_NoAttention", "TCN_Attention"]:
        p = req(prof, name)
        lines.append(f"| {name.replace('_', ' ')} | {ints(p['parameters'])} | {kb(p['model_size_bytes'])} | {p['gflops']:.6f} |")
    write("T2_model_complexity.md", lines)


# ----------------------------------------------------------------------------- T3 PQC
def table3_pqc(R):
    pqc = req(R, "resource_profile", "pqc_cryptography")
    lines = [f"**Table 3.** ML-KEM-768 + AES-256-GCM overhead — *provenance: measured; {ints(pqc['iterations'])} iterations after {ints(pqc['warmup'])} warm-up; kyber-py pure-Python FIPS-203 reference implementation (upper bound on latency)*", "",
             "| Operation | Median (ms) | P95 (ms) | Std (ms) | Bytes |", "|---|---:|---:|---:|---:|"]
    rows = [("ML-KEM-768 KeyGen", "keygen", f"pk {const(1184)} / sk {const(2400)}"),
            ("ML-KEM-768 Encaps", "encaps", f"ct {const(1088)}"),
            ("ML-KEM-768 Decaps", "decaps", f"ss {const(32)}"),
            ("AES-256-GCM encrypt", "aes_gcm_encrypt", f"payload {ints(pqc['payload_bytes'])}"),
            ("AES-256-GCM decrypt", "aes_gcm_decrypt", f"nonce {const(12)} + tag {const(16)}")]
    for label, key, b in rows:
        s = req(pqc, key)
        lines.append(f"| {label} | {f4(s['median_ms'])} | {f4(s['p95_ms'])} | {f4(s['std_ms'])} | {b} |")
    total = req(pqc, "keygen", "median_ms") + req(pqc, "encaps", "median_ms") + req(pqc, "decaps", "median_ms")
    pqc["_derived_total_kem_median_ms"] = round(total, 4)   # persisted below so the checker can find it
    lines.append(f"| **KEM total (keygen+encaps+decaps)** | **{f4(total)}** | — | — | ciphertext overhead per round {ints(pqc['ciphertext_overhead_bytes'])} |")
    write("T3_pqc.md", lines)


# ----------------------------------------------------------------------------- T4 FL
def table4_fl(R):
    fl = req(R, "fl_benchmarks")
    cfg = (f"K = {fl['num_clients']} clients, C = {fl['participation_rate']}, Dirichlet α = {const(0.5)}, "
           f"{fl['num_rounds']} rounds, {fl['local_epochs']} local epochs, batch {fl['batch_size']}, lr {fl['learning_rate']}, "
           f"{ints(fl['sample_size'])} samples, {fl['features_count']} features, {len(fl['seeds'])} seeds")
    lines = [f"**Table 4.** Federated detection performance on Edge-IIoTset — *provenance: measured; {cfg}*", "",
             "| Split | Algorithm | Accuracy | Macro-F1 | ROC-AUC | ROC-AUC 95% CI | Payload / client / round (KB) | Median round time (s) |",
             "|---|---|---:|---:|---:|---:|---:|---:|"]
    for split in ["random", "temporal"]:
        sr = req(fl, "splits", split)
        for algo in ["FedAvg", "FedProx", "SCAFFOLD"]:
            a = req(sr, "algorithms", algo)
            lines.append(f"| {split} | {algo} | {pm(a['accuracy'])} | {pm(a['macro_f1'])} | {pm(a['roc_auc'])} | {ci(a['roc_auc'])} | {kb(a['mean_comm_payload_bytes'])} | {f2(a['median_round_time_sec'])} |")
        c = req(sr, "centralized_upper_bound")
        lines.append(f"| {split} | *Centralized bound ({c['epochs']} epochs)* | {pm(c['accuracy'])} | {pm(c['macro_f1'])} | {pm(c['roc_auc'])} | {ci(c['roc_auc'])} | — | — |")
        t = req(sr, "paired_test_scaffold_vs_fedavg")
        p_t = f4(t["p_value_ttest"]) if "p_value_ttest" in t else "n/a (zero variance)"
        p_w = f4(t["p_value_wilcoxon"]) if "p_value_wilcoxon" in t else "n/a"
        lines.append(f"| {split} | SCAFFOLD − FedAvg (accuracy) | mean diff {f4(t['mean_diff'])} | paired t p = {p_t} | Wilcoxon p = {p_w} | | | |")
    dense = req(fl, "model_profiles", "TCN_Attention", "model_size_bytes")
    sparse = req(fl, "splits", "random", "algorithms", "SCAFFOLD", "mean_comm_payload_bytes")
    red = (1.0 - sparse / dense) * 100.0
    with open(os.path.join(PHASES_DIR, "fl.json")) as f:
        flp = json.load(f)
    flp["_derived_payload_reduction_pct_vs_float32"] = round(red, 2)
    with open(os.path.join(PHASES_DIR, "fl.json"), "w") as f:
        json.dump(flp, f, indent=2)
    rebuild_results()
    lines += ["", f"Top-k (30 %) update payload including int32 indices and dense BatchNorm buffers = {kb(sparse)} KB versus {kb(dense)} KB raw float32 parameters: {f2(red)} % reduction.",
              f"Test-set attack share: random {f4(req(fl,'splits','random','test_attack_rate'))}, temporal {f4(req(fl,'splits','temporal','test_attack_rate'))}. "
              "Per-seed values and per-round learning curves are stored under `fl_benchmarks.splits.<split>.algorithms.<algo>.seed_trials` in RESULTS.json."]
    write("T4_fl_benchmark.md", lines)


# ----------------------------------------------------------------------------- T5 ablation
def table5_ablation(R):
    ab = req(R, "ablation_benchmarks")
    lines = [f"**Table 5.** Component ablation — *provenance: measured; {const(10)} clients, {ab['num_rounds']} rounds, {ints(ab['sample_size'])} samples, {len(ab['seeds'])} seeds; Stage 8 has {const(20)}% label-flip + sign-flip clients*", "",
             "| Stage | Configuration | Parameters | Accuracy | Macro-F1 | ROC-AUC |", "|---|---|---:|---:|---:|---:|"]
    for i in range(1, 9):
        st = req(ab, "stages", f"Stage {i}")
        lines.append(f"| {i} | {st['description']} | {ints(st['parameters'])} | {pm(st['accuracy'])} | {pm(st['macro_f1'])} | {pm(st['roc_auc'])} |")
    write("T5_ablation.md", lines)


# ----------------------------------------------------------------------------- T6 poisoning
def table6_poison(R):
    pb = req(R, "poisoning_benchmarks")
    lines = [f"**Table 6.** Robustness to Byzantine clients — *provenance: measured; K = {pb['num_clients']}, {pb['num_rounds']} rounds, {ints(pb['sample_size'])} samples, {len(pb['seeds'])} seeds; attack = label flip + scaled sign flip (λ = {const(5)})*", "",
             "| Malicious clients | Defense | Accuracy | Macro-F1 | ROC-AUC |", "|---|---|---:|---:|---:|"]
    for ratio in req(pb, "poison_ratios"):
        pct = f"{int(round(ratio * 100))}%"
        rr = req(pb, "results_by_ratio", pct)
        for d in req(pb, "defenses"):
            s = req(rr, d)
            lines.append(f"| {const(pct)} | {d.replace('_', ' ')} | {pm(s['accuracy'])} | {pm(s['macro_f1'])} | {pm(s['roc_auc'])} |")
    write("T6_poisoning.md", lines)


# ----------------------------------------------------------------------------- T7 transfer
def table7_transfer(R):
    ct = req(R, "cross_dataset_transfer")
    lines = [f"**Table 7.** Cross-dataset transfer Edge-IIoTset → WUSTL-IIoT-2021 — *provenance: measured; {ct['shared_features_count']} semantically shared features ({', '.join(ct['shared_features'])}); {ints(ct['evaluated_target_rows'])} of {ints(ct['wustl_total_rows'])} target flows; source model {ct['source_model']}*", "",
             "| Setting | Accuracy | Macro-F1 | ROC-AUC | PR-AUC |", "|---|---:|---:|---:|---:|"]
    for key, label in [("zero_shot", "Zero-shot (source scaler, no target labels)"),
                       ("fine_tuned", "Fine-tuned on 20 % of target"),
                       ("scratch_on_target", "From scratch on the same 20 % of target")]:
        s = req(ct, key)
        lines.append(f"| {label} | {pm(s['accuracy'])} | {pm(s['macro_f1'])} | {pm(s['roc_auc'])} | {pm(s['pr_auc'])} |")
    lines += ["", ct["feature_space_note"]]
    write("T7_transfer.md", lines)


# ----------------------------------------------------------------------------- T8 resources
def table8_resources(R):
    rp = req(R, "resource_profile"); inf = req(rp, "single_sample_inference"); mem = req(rp, "memory_footprint")
    en = req(rp, "energy_consumption"); mc = req(rp, "model_complexity")
    lines = ["**Table 8.** Edge resource profile (CPU only) — *provenance per row*", "",
             "| Metric | Value | Provenance | Method |", "|---|---:|---|---|",
             f"| Single-sample inference latency, median | {f4(inf['median_ms'])} ms | measured | batch = 1, {const(200)} warm-up, {const(2000)} timed |",
             f"| Single-sample inference latency, P95 / P99 | {f4(inf['p95_ms'])} / {f4(inf['p99_ms'])} ms | measured | same run |",
             f"| Throughput at batch = 1 | {f2(inf['throughput_samples_per_sec'])} samples/s | measured | 1000 / median latency |",
             f"| Process RSS | {f2(mem['process_rss_mb'])} MB | measured | psutil.Process().memory_info().rss |",
             f"| Trainable parameters | {ints(mc['parameters'])} | measured | sum(p.numel()) |",
             f"| Serialized float32 size | {kb(mc['model_size_bytes'])} KB | measured | params × 4 |",
             f"| Median FL round time (SCAFFOLD, random split) | {f2(en['mean_round_time_sec'])} s | measured | from Table 4 run |",
             f"| Energy per round | {f2(en['estimated_joules_per_round'])} J | **estimated** | round time × assumed {f1(en['assumed_tdp_watts'])} W TDP |"]
    write("T8_resources.md", lines)


# ----------------------------------------------------------------------------- T9 QAOA
def table9_qaoa(R):
    q = req(R, "qaoa_multi_n_benchmarks")
    lines = [f"**Table 9.** QUBO response-selection: QAOA (statevector simulator) vs exact ILP vs greedy — *provenance: measured; {q['actions_per_asset']} actions per asset; objective = negative utility (lower is better)*", "",
             "| N assets | Qubits | Trials | ILP latency (ms) | QAOA latency (ms) | QAOA gap vs ILP (%) |", "|---:|---:|---:|---:|---:|---:|"]
    for key in sorted(req(q, "results_by_n").keys(), key=lambda k: int(k.split("_")[1])):
        r = q["results_by_n"][key]
        lines.append(f"| {r['n_assets']} | {r['qubits']} | {len(r['trials'])} | {f2(r['mean_ilp_latency_ms'])} | {f2(r['mean_qaoa_latency_ms'])} | {f2(r['mean_qaoa_gap_pct'])} |")
    write("T9_qaoa.md", lines)


# ----------------------------------------------------------------------------- main
def main():
    table1_dataset()
    with open(RESULTS_FILE) as f:
        R = json.load(f)
    table2_models(R); table3_pqc(R); table4_fl(R); table5_ablation(R)
    table6_poison(R); table7_transfer(R); table8_resources(R); table9_qaoa(R)

    # persist derived totals used in tables (e.g. KEM total) so the checker can verify them
    with open(os.path.join(PHASES_DIR, "resources.json")) as f:
        res = json.load(f)
    res["pqc_cryptography"]["_derived_total_kem_median_ms"] = R["resource_profile"]["pqc_cryptography"]["_derived_total_kem_median_ms"]
    with open(os.path.join(PHASES_DIR, "resources.json"), "w") as f:
        json.dump(res, f, indent=2)
    rebuild_results()

    with open(os.path.join(TABLES_DIR, "_allowed_constants.json"), "w") as f:
        json.dump(sorted(ALLOWED), f, indent=2)
    names = ["T1_dataset", "T2_model_complexity", "T3_pqc", "T4_fl_benchmark", "T5_ablation", "T6_poisoning", "T7_transfer", "T8_resources", "T9_qaoa"]
    with open(os.path.join(TABLES_DIR, "ALL_TABLES.md"), "w", encoding="utf-8", newline="\n") as out:
        for n in names:
            out.write(open(os.path.join(TABLES_DIR, n + ".md"), encoding="utf-8").read() + "\n")
    print("\n[OK] all tables generated from", RESULTS_FILE)


if __name__ == "__main__":
    main()
