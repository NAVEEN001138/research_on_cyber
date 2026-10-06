"""
scripts/dedupe_alias_keys.py
----------------------------
Auditable cleanup script to:
1. Remove alias key 'Cosine_Trust' from results/phases/poison.json (retaining 'Cosine_Trust_NormBounded').
2. Remove top-level redundant 'centralized' and 'fedavg' blocks from results/phases/leakage.json (retaining per-split data under 'by_split').
3. Rename SGD algorithms in results/phases/fl.json to explicit labels:
   'FedAvg' -> 'FedAvg (SGD)', 'FedProx' -> 'FedProx (SGD)', 'SCAFFOLD' -> 'SCAFFOLD (SGD)'
   and remove alias keys 'FedAvg-SGD' and 'FedProx-SGD'.
4. Rebuild results/RESULTS.json via rebuild_results().
"""

import os
import sys
import json

# Ensure project root is in sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from run_experiments import PHASES_DIR, rebuild_results


def dedupe_poison():
    p_path = os.path.join(PHASES_DIR, "poison.json")
    if not os.path.exists(p_path):
        print(f"[SKIP] {p_path} not found")
        return
    with open(p_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # 1. Clean results_by_ratio
    rbr = data.get("results_by_ratio", {})
    removed_count = 0
    for ratio_key, ratio_dict in rbr.items():
        if "Cosine_Trust" in ratio_dict:
            del ratio_dict["Cosine_Trust"]
            removed_count += 1

    # 2. Ensure defenses list contains the 5 canonical defenses
    data["defenses"] = [
        "FedAvg_Undefended",
        "Coordinate_Median",
        "Trimmed_Mean",
        "Multi_Krum",
        "Cosine_Trust_NormBounded"
    ]

    with open(p_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    print(f"[OK] poison.json deduped: removed 'Cosine_Trust' alias from {removed_count} ratio blocks")


def dedupe_leakage():
    l_path = os.path.join(PHASES_DIR, "leakage.json")
    if not os.path.exists(l_path):
        print(f"[SKIP] {l_path} not found")
        return
    with open(l_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    changed = False
    if "centralized" in data:
        del data["centralized"]
        changed = True
    if "fedavg" in data:
        del data["fedavg"]
        changed = True

    if changed:
        with open(l_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        print("[OK] leakage.json deduped: removed top-level 'centralized' and 'fedavg' blocks")
    else:
        print("[OK] leakage.json already clean")


def dedupe_fl():
    fl_path = os.path.join(PHASES_DIR, "fl.json")
    if not os.path.exists(fl_path):
        print(f"[SKIP] {fl_path} not found")
        return
    with open(fl_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    splits = data.get("splits", {})
    for split_name, split_data in splits.items():
        algs = split_data.get("algorithms", {})
        # Remove alias keys first
        if "FedAvg-SGD" in algs:
            del algs["FedAvg-SGD"]
        if "FedProx-SGD" in algs:
            del algs["FedProx-SGD"]

        # Rename to explicit optimizer labels
        if "FedAvg" in algs and "FedAvg (SGD)" not in algs:
            algs["FedAvg (SGD)"] = algs.pop("FedAvg")
        if "FedProx" in algs and "FedProx (SGD)" not in algs:
            algs["FedProx (SGD)"] = algs.pop("FedProx")
        if "SCAFFOLD" in algs and "SCAFFOLD (SGD)" not in algs:
            algs["SCAFFOLD (SGD)"] = algs.pop("SCAFFOLD")

    with open(fl_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    print("[OK] fl.json updated: explicit optimizer labels and alias keys removed")


def main():
    print("=== DEDUPLICATING ALIAS KEYS ACROSS RESULTS ===")
    dedupe_poison()
    dedupe_leakage()
    dedupe_fl()
    rebuild_results()
    print("[SUCCESS] All results rebuilt into results/RESULTS.json")


if __name__ == "__main__":
    main()
