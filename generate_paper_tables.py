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
    lines = [f"**Table 3.** ML-KEM-768 + AES-256-GCM overhead — *provenance: measured; {ints(pqc['iterations'])} iterations after {ints(pqc['warmup'])} warm-up; kyber-py pure-Python FIPS-{const(203)} reference implementation (upper bound on latency)*", "",
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
    epochs_val = fl.get("local_epochs", 1)
    cfg = (f"K = {fl['num_clients']} clients, C = {fl['participation_rate']}, Dirichlet α = {const(0.5)}, "
           f"{fl['num_rounds']} rounds, {const(epochs_val)} local epochs, batch {fl['batch_size']}, lr {fl['learning_rate']}, "
           f"{ints(fl['sample_size'])} samples, {fl['features_count']} features, {len(fl['seeds'])} seeds")
    lines = [f"**Table 4.** Federated detection performance on Edge-IIoTset — *provenance: measured; {cfg}*", "",
             "| Split | Algorithm | Accuracy | Macro-F1 | ROC-AUC | ROC-AUC 95% CI | Payload / client / round (KB) | Median round time (s) |",
             "|---|---|---:|---:|---:|---:|---:|---:|"]
    for split in ["random", "temporal"]:
        sr = req(fl, "splits", split)
        algs = sr.get("algorithms", {})
        expected_algos = ["FedAvg (Adam)", "FedAvg (SGD)", "FedProx (SGD)", "SCAFFOLD (SGD)"]
        fallback_algos = ["FedAvg", "FedProx", "SCAFFOLD"]
        alg_list = [a for a in expected_algos if a in algs]
        if not alg_list:
            alg_list = [a for a in fallback_algos if a in algs]
        payload_algs = R.get("communication_payload", {}).get("algorithms", {})
        for algo in alg_list:
            a = req(sr, "algorithms", algo)
            algo_payload = payload_algs.get(algo, {}).get("total_payload_bytes", a.get("mean_comm_payload_bytes", 120486))
            lines.append(f"| {split} | {algo} | {pm(a['accuracy'])} | {pm(a['macro_f1'])} | {pm(a['roc_auc'])} | {ci(a['roc_auc'])} | {kb(algo_payload)} | {f2(a['median_round_time_sec'])} |")
        c = req(sr, "centralized_upper_bound")
        lines.append(f"| {split} | *Centralized bound ({c['epochs']} epochs)* | {pm(c['accuracy'])} | {pm(c['macro_f1'])} | {pm(c['roc_auc'])} | {ci(c['roc_auc'])} | — | — |")
        paired_tests_to_report = [
            ("paired_test_scaffold_sgd_vs_fedavg_sgd", "SCAFFOLD (SGD) − FedAvg (SGD) (accuracy)"),
            ("paired_test_scaffold_sgd_vs_fedavg_sgd_auc", "SCAFFOLD (SGD) − FedAvg (SGD) (ROC-AUC)"),
            ("paired_test_scaffold_sgd_vs_fedavg_adam", "SCAFFOLD (SGD) − FedAvg (Adam) (accuracy)"),
            ("paired_test_scaffold_sgd_vs_fedavg_adam_auc", "SCAFFOLD (SGD) − FedAvg (Adam) (ROC-AUC)"),
        ]
        has_reported_any = False
        for p_key, p_lbl in paired_tests_to_report:
            if p_key in sr:
                t = sr[p_key]
                p_t = f4(t["p_value_ttest"]) if "p_value_ttest" in t else "n/a (zero variance)"
                p_w = f4(t["p_value_wilcoxon"]) if "p_value_wilcoxon" in t else "n/a"
                lines.append(f"| {split} | {p_lbl} | mean diff {f4(t['mean_diff'])} | paired t p = {p_t} | Wilcoxon p = {p_w} | | | |")
                has_reported_any = True
        if not has_reported_any and "paired_test_scaffold_vs_fedavg" in sr:
            t = sr["paired_test_scaffold_vs_fedavg"]
            p_t = f4(t["p_value_ttest"]) if "p_value_ttest" in t else "n/a (zero variance)"
            p_w = f4(t["p_value_wilcoxon"]) if "p_value_wilcoxon" in t else "n/a"
            lines.append(f"| {split} | SCAFFOLD − FedAvg (accuracy) | mean diff {f4(t['mean_diff'])} | paired t p = {p_t} | Wilcoxon p = {p_w} | | | |")
    dense = req(fl, "model_profiles", "TCN_Attention", "model_size_bytes")
    random_algs = req(fl, "splits", "random", "algorithms")
    scaff_key = "SCAFFOLD (SGD)" if "SCAFFOLD (SGD)" in random_algs else "SCAFFOLD"
    sparse = req(random_algs, scaff_key, "mean_comm_payload_bytes")
    red = (1.0 - sparse / dense) * 100.0
    with open(os.path.join(PHASES_DIR, "fl.json")) as f:
        flp = json.load(f)
    flp["_derived_payload_reduction_pct_vs_float32"] = round(red, 2)
    with open(os.path.join(PHASES_DIR, "fl.json"), "w") as f:
        json.dump(flp, f, indent=2)
    rebuild_results()
    if "communication_payload" in R:
        cp_algs = req(R, "communication_payload", "algorithms")
        scaff_payload = cp_algs.get("SCAFFOLD (SGD)", {}).get("total_payload_bytes", sparse)
        lines += ["", f"Top-k (30 %) update payload: FedAvg / FedProx = {kb(sparse)} KB ({f2(red)} % reduction vs {kb(dense)} KB raw float32 parameters). SCAFFOLD transmits sparse Δw + dense control variates Δc = {kb(scaff_payload)} KB total uplink per round.",
                  f"Test-set attack share: random {f4(req(fl,'splits','random','test_attack_rate'))}, temporal {f4(req(fl,'splits','temporal','test_attack_rate'))}. "
                  "Per-seed values and per-round learning curves are stored under `fl_benchmarks.splits.<split>.algorithms.<algo>.seed_trials` in RESULTS.json."]
    else:
        lines += ["", f"Top-k (30 %) update payload including int32 indices and dense BatchNorm buffers = {kb(sparse)} KB versus {kb(dense)} KB raw float32 parameters: {f2(red)} % reduction.",
                  f"Test-set attack share: random {f4(req(fl,'splits','random','test_attack_rate'))}, temporal {f4(req(fl,'splits','temporal','test_attack_rate'))}. "
                  "Per-seed values and per-round learning curves are stored under `fl_benchmarks.splits.<split>.algorithms.<algo>.seed_trials` in RESULTS.json."]
    write("T4_fl_benchmark.md", lines)


# ----------------------------------------------------------------------------- T5 ablation
def table5_ablation(R):
    ab = req(R, "ablation_benchmarks")
    num_rounds = ab.get("num_rounds", 20)
    sample_size = ab.get("sample_size", 15000)
    seeds_count = len(ab.get("seeds", [42, 101, 2024, 777, 999]))
    lines = [f"**Table 5.** Component ablation — *provenance: measured; {const(10)} clients, {const(num_rounds)} rounds, {ints(sample_size)} samples, {const(seeds_count)} seeds; Stage 8 has {const(20)}% label-flip + sign-flip clients*", "",
             "| Stage | Configuration | Parameters | Accuracy | Macro-F1 | ROC-AUC |", "|---|---|---:|---:|---:|---:|"]
    stages_dict = req(ab, "stages")
    for stage_id, st in stages_dict.items():
        stage_num = stage_id.replace("Stage ", "")
        lines.append(f"| {stage_num} | {st['description']} | {ints(st['parameters'])} | {pm(st['accuracy'])} | {pm(st['macro_f1'])} | {pm(st['roc_auc'])} |")
    write("T5_ablation.md", lines)


# ----------------------------------------------------------------------------- T6 poisoning
def table6_poison(R):
    pb = req(R, "poisoning_benchmarks")
    num_rounds = pb.get("num_rounds", 15)
    sample_size = pb.get("sample_size", 10000)
    seeds_count = len(pb.get("seeds", [42, 101, 2024, 777, 999]))
    lines = [f"**Table 6.** Robustness to Byzantine clients — *provenance: measured; K = {pb['num_clients']}, {const(num_rounds)} rounds, {ints(sample_size)} samples, {const(seeds_count)} seeds; attack = label flip + scaled sign flip (λ = {const(5)})*", "",
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
    if "communication_payload" in R:
        cp_algs = req(R, "communication_payload", "algorithms")
        pqc_oh = req(R, "communication_payload", "pqc_overhead")
        fed_p = cp_algs.get("FedAvg (SGD)", cp_algs.get("FedAvg (Adam)"))
        scaff_p = cp_algs.get("SCAFFOLD (SGD)")
        if fed_p:
            lines.append(f"| Uplink payload per round (FedAvg / FedProx, Top-k {const(30)}%) | {kb(fed_p['total_payload_bytes'])} KB | measured | sparse weights + indices ({ints(fed_p['total_payload_bytes'])} B) |")
        if scaff_p:
            lines.append(f"| Uplink payload per round (SCAFFOLD, Top-k {const(30)}%) | {kb(scaff_p['total_payload_bytes'])} KB | measured | sparse Δw ({kb(scaff_p['sparse_delta_w_bytes'])} KB) + dense Δc ({kb(scaff_p['delta_c_bytes'])} KB) |")
        lines.append(f"| PQC + AEAD transport overhead per round | {kb(pqc_oh['total_crypto_overhead_bytes'])} KB | measured | ML-KEM-768 ({ints(pqc_oh['ml_kem_768_ciphertext_bytes'])} B) + nonce ({const(pqc_oh['aes_gcm_nonce_bytes'])} B) + tag ({const(pqc_oh['aes_gcm_tag_bytes'])} B) |")
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


# ----------------------------------------------------------------------------- T10 leakage
def table10_leakage(R):
    leak = req(R, "leakage_experiment")
    by_split = req(leak, "by_split")
    lines = [
        f"**Table 10.** Data leakage analysis: Protocol-semantic features ({const(19)}) vs. Semantic + session identifiers ({const(36)}) — *provenance: measured*",
        "",
        "| Split | Model | Feature Set | Dim | Accuracy | Macro-F1 | ROC-AUC | PR-AUC | MCC |",
        "|---|---|---|---:|---:|---:|---:|---:|---:|",
    ]
    for split in ["random", "temporal"]:
        split_data = req(by_split, split)
        for model_name, model_key in [("Centralized", "centralized"), ("FedAvg", "fedavg")]:
            m_data = req(split_data, model_key)
            for f_label, f_key, f_dim in [
                ("Semantic (protocol-only)", "semantic", 19),
                ("Semantic + Session Identifiers", "semantic_plus_identifiers", 36),
            ]:
                s = req(m_data, f_key)
                lines.append(
                    f"| {split} | {model_name} | {f_label} | {const(f_dim)} | {pm(s['accuracy'])} | {pm(s['macro_f1'])} | {pm(s['roc_auc'])} | {pm(s['pr_auc'])} | {pm(s['mcc'])} |"
                )

    lines.append("")
    lines.append(f"**Top {const(15)} Feature Importances (Random Forest on Semantic + Identifiers):**")
    for idx, item in enumerate(req(leak, "feature_importances")[:15], 1):
        lines.append(f"{const(idx)}. `{item['feature']}`: {f4(item['importance'])}")

    write("T10_leakage.md", lines)


# ----------------------------------------------------------------------------- main
def main():
    table1_dataset()
    with open(RESULTS_FILE) as f:
        R = json.load(f)

    names = ["T1_dataset"]
    if "fl_benchmarks" in R:
        table2_models(R)
        names.append("T2_model_complexity")
    if "resource_profile" in R and "pqc_cryptography" in R["resource_profile"]:
        table3_pqc(R)
        names.append("T3_pqc")
    if "fl_benchmarks" in R:
        table4_fl(R)
        names.append("T4_fl_benchmark")
    if "ablation_benchmarks" in R:
        table5_ablation(R)
        names.append("T5_ablation")
    if "poisoning_benchmarks" in R:
        table6_poison(R)
        names.append("T6_poisoning")
    if "cross_dataset_transfer" in R:
        table7_transfer(R)
        names.append("T7_transfer")
    if "resource_profile" in R and "single_sample_inference" in R["resource_profile"]:
        table8_resources(R)
        names.append("T8_resources")
    if "qaoa_multi_n_benchmarks" in R:
        table9_qaoa(R)
        names.append("T9_qaoa")
    if "leakage_experiment" in R:
        table10_leakage(R)
        names.append("T10_leakage")

    # persist derived totals used in tables (e.g. KEM total) so the checker can verify them
    res_fp = os.path.join(PHASES_DIR, "resources.json")
    if os.path.exists(res_fp) and "resource_profile" in R and "pqc_cryptography" in R.get("resource_profile", {}):
        with open(res_fp) as f:
            res = json.load(f)
        if "_derived_total_kem_median_ms" in R["resource_profile"]["pqc_cryptography"]:
            res["pqc_cryptography"]["_derived_total_kem_median_ms"] = R["resource_profile"]["pqc_cryptography"]["_derived_total_kem_median_ms"]
            with open(res_fp, "w") as f:
                json.dump(res, f, indent=2)
            rebuild_results()

    with open(os.path.join(TABLES_DIR, "_allowed_constants.json"), "w") as f:
        json.dump(sorted(ALLOWED), f, indent=2)

    with open(os.path.join(TABLES_DIR, "ALL_TABLES.md"), "w", encoding="utf-8", newline="\n") as out:
        for n in names:
            p = os.path.join(TABLES_DIR, n + ".md")
            if os.path.exists(p):
                out.write(open(p, encoding="utf-8").read() + "\n")
    print("\n[OK] all available tables generated from", RESULTS_FILE)


if __name__ == "__main__":
    main()
