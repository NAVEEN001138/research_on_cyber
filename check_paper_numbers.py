"""
=============================================================================
PAPER NUMBER CHECKER
Script: check_paper_numbers.py
-----------------------------------------------------------------------------
Proves that every number in the manuscript is traceable to results/RESULTS.json.

  * Builds the set of every numeric leaf in RESULTS.json, in every rendering the
    table generator can produce (raw, 1-4 decimals, ×100 percentages, /1024 KB,
    thousands separators).
  * Extracts numeric tokens from  paper/tables/*.md  (all of them) and from
    RESEARCH_PAPER_IEEE.md (every line up to the References heading; years,
    section numbers, equation indices and citation keys are ignored).
  * Every token must be in the acceptable set or in
    paper/tables/_allowed_constants.json (configuration literals the generator wrote).
  * Exit code 1 and a list of offending tokens with file:line otherwise.
=============================================================================
"""

import os
import re
import sys
import json
import glob

RESULTS_FILE = "results/RESULTS.json"
PAPER = "RESEARCH_PAPER_IEEE.md"
TABLES = "paper/tables"

# tokens that are never results
IGNORE_EXACT = {"0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "100"}
YEAR = re.compile(r"^(19|20)\d{2}$")
DOI = re.compile(r"10\.\d{4,}/\S+")
TOKEN = re.compile(r"(?<![\w.])(\d{1,3}(?:,\d{3})+(?:\.\d+)?|\d+\.\d+|\d+)(?![\w.]*[A-Za-z])")


def renderings(v):
    out = set()
    if isinstance(v, bool):
        return out
    if isinstance(v, int):
        out.add(str(v)); out.add(f"{v:,}")
        v = float(v)
    if isinstance(v, float):
        for d in (0, 1, 2, 3, 4, 6):
            out.add(f"{v:.{d}f}")
            out.add(f"{v * 100:.{d}f}")          # percentages
            out.add(f"{v / 1024.0:.{d}f}")       # bytes -> KB
            out.add(f"{v * 1024.0:.{d}f}")       # MB -> KB
        out.add(repr(v)); out.add(str(v))
        if v.is_integer():
            out.add(f"{int(v):,}")
    return out


def leaves(o):
    if isinstance(o, dict):
        for v in o.values():
            yield from leaves(v)
    elif isinstance(o, list):
        for v in o:
            yield from leaves(v)
    elif isinstance(o, (int, float)) and not isinstance(o, bool):
        yield o


def acceptable_set(results):
    acc = set()
    for v in leaves(results):
        acc |= renderings(v)
    # sums the generator is allowed to derive
    pq = results.get("resource_profile", {}).get("pqc_cryptography", {})
    if all(k in pq for k in ("keygen", "encaps", "decaps")):
        acc |= renderings(pq["keygen"]["median_ms"] + pq["encaps"]["median_ms"] + pq["decaps"]["median_ms"])
    ds = results.get("dataset_distribution")
    if ds:
        tot = ds["total_rows"]
        for v in list(ds["per_attack_type"].values()) + [ds["normal_rows"], ds["attack_rows"]]:
            acc |= renderings(v / tot * 100.0)
    return acc


def tokens_in_line(line):
    if DOI.search(line):
        line = DOI.sub(" ", line)
    line = re.sub(r"\[\d+(?:[,–-]\d+)*\]", " ", line)        # citation keys [12], [3-5]
    line = re.sub(r"\(\d+\)", " ", line)                       # equation numbers (3)
    line = re.sub(r"(?i)\b(table|fig\.?|figure|section|stage|layer|seed|eq\.?)\s*\d+", " ", line)
    for tok in TOKEN.findall(line):
        t = tok.strip()
        if t in IGNORE_EXACT or YEAR.match(t):
            continue
        yield t


def scan_file(path, stop_at_references=False):
    found = []
    with open(path, encoding="utf-8") as f:
        for i, line in enumerate(f, 1):
            if stop_at_references and re.match(r"^\s*#+\s*(references|bibliography)\b", line, re.I):
                break
            for t in tokens_in_line(line):
                found.append((path, i, t, line.strip()[:90]))
    return found


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if not os.path.exists(RESULTS_FILE):
        print("FAIL: results/RESULTS.json missing"); sys.exit(1)
    with open(RESULTS_FILE) as f:
        results = json.load(f)
    acc = acceptable_set(results)
    allowed_path = os.path.join(TABLES, "_allowed_constants.json")
    allowed = set(json.load(open(allowed_path))) if os.path.exists(allowed_path) else set()
    allowed |= set(str(s) for s in results.get("fl_benchmarks", {}).get("seeds", []))
    prose_path = "paper/prose_constants.json"
    prose = {}
    if os.path.exists(prose_path):
        prose = {k: v for k, v in json.load(open(prose_path)).items() if not k.startswith("_")}
        allowed |= set(prose.keys())

    checks = []
    for p in sorted(glob.glob(os.path.join(TABLES, "*.md"))):
        checks += scan_file(p)
    if os.path.exists(PAPER):
        checks += scan_file(PAPER, stop_at_references=True)

    bad = [c for c in checks if c[2] not in acc and c[2] not in allowed and c[2].replace(",", "") not in acc]
    print(f"tokens checked: {len(checks)} | acceptable renderings: {len(acc)} | allowed constants: {len(allowed)}")
    if bad:
        print(f"\nFAIL: {len(bad)} numeric token(s) are not traceable to {RESULTS_FILE}:")
        for path, i, t, ctx in bad:
            print(f"  {path}:{i}  {t!r}   | {ctx}")
        sys.exit(1)
    used_prose = sorted({c[2] for c in checks if c[2] in prose and c[2] not in acc})
    if used_prose:
        print(f"declared protocol constants used in prose (see paper/prose_constants.json): {', '.join(used_prose)}")
    print("PASS: every numeric token in paper tables and manuscript body is traceable to RESULTS.json or declared in prose_constants.json")


if __name__ == "__main__":
    main()
