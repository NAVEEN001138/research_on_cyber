"""
=============================================================================
PAPER RENDERER
Script: build_paper.py
-----------------------------------------------------------------------------
Renders paper/PAPER_TEMPLATE.md -> RESEARCH_PAPER_IEEE.md.

Placeholders
  {{TABLE:T4_fl_benchmark}}                 -> contents of paper/tables/T4_fl_benchmark.md
  {{V:fl_benchmarks.num_clients}}           -> raw value from results/RESULTS.json
  {{V:<dotted.path>:pct1}}                  -> value*100 with 1 decimal   (also pct2)
  {{V:<dotted.path>:f2}}                    -> 2 decimals (f1, f3, f4)
  {{V:<dotted.path>:int}}                   -> thousands-separated integer
  {{V:<dotted.path>:kb}}                    -> bytes / 1024, 2 decimals
  {{ENV:cpu_model}}                         -> results/environment.json field
  {{LEN:<dotted.path>}}                     -> len() of a list / dict

A missing path is a hard error: the paper is never rendered with a fallback.
Run generate_paper_tables.py first, then this, then check_paper_numbers.py.
=============================================================================
"""

import os
import re
import sys
import json

RESULTS_FILE = "results/RESULTS.json"
ENV_FILE = "results/environment.json"
TEMPLATE = "paper/PAPER_TEMPLATE.md"
TABLES_DIR = "paper/tables"
OUT = "RESEARCH_PAPER_IEEE.md"

FMT = {
    None: lambda v: str(v),
    "pct1": lambda v: f"{float(v) * 100:.1f}",
    "pct2": lambda v: f"{float(v) * 100:.2f}",
    "f1": lambda v: f"{float(v):.1f}",
    "f2": lambda v: f"{float(v):.2f}",
    "f3": lambda v: f"{float(v):.3f}",
    "f4": lambda v: f"{float(v):.4f}",
    "int": lambda v: f"{int(v):,}",
    "kb": lambda v: f"{float(v) / 1024.0:.2f}",
}


def lookup(root, dotted):
    cur = root
    for part in dotted.split("."):
        if isinstance(cur, list):
            cur = cur[int(part)]
        elif isinstance(cur, dict) and part in cur:
            cur = cur[part]
        else:
            raise KeyError(f"path not found in {RESULTS_FILE}: {dotted!r} (failed at {part!r})")
    return cur


def main():
    dry = "--dry-run" in sys.argv          # validate template; report unresolved paths; write nothing
    missing = []
    with open(RESULTS_FILE) as f:
        R = json.load(f)
    with open(ENV_FILE) as f:
        ENV = json.load(f)
    with open(TEMPLATE, encoding="utf-8") as f:
        text = f.read()

    def sub_table(m):
        p = os.path.join(TABLES_DIR, m.group(1) + ".md")
        if not os.path.exists(p):
            if dry:
                missing.append("TABLE:" + m.group(1)); return "<<MISSING TABLE>>"
            raise FileNotFoundError(f"table not generated: {p} (run generate_paper_tables.py)")
        return open(p, encoding="utf-8").read().rstrip("\n")

    def sub_val(m):
        path, fmt = m.group(1), m.group(2)
        if fmt not in FMT:
            raise ValueError(f"unknown format {fmt!r} in {{{{V:{path}:{fmt}}}}}")
        try:
            return FMT[fmt](lookup(R, path))
        except (KeyError, IndexError):
            if dry:
                missing.append(path); return "<<MISSING>>"
            raise

    def sub_env(m):
        return str(ENV[m.group(1)])

    def sub_len(m):
        try:
            return str(len(lookup(R, m.group(1))))
        except (KeyError, IndexError):
            if dry:
                missing.append(m.group(1)); return "<<MISSING>>"
            raise

    text = re.sub(r"\{\{TABLE:([A-Za-z0-9_]+)\}\}", sub_table, text)
    text = re.sub(r"\{\{V:([A-Za-z0-9_.\- %()]+?)(?::([a-z0-9]+))?\}\}", sub_val, text)
    text = re.sub(r"\{\{ENV:([A-Za-z0-9_]+)\}\}", sub_env, text)
    text = re.sub(r"\{\{LEN:([A-Za-z0-9_.\- %()]+?)\}\}", sub_len, text)

    left = re.findall(r"\{\{[^}]*\}\}", text)
    if left:
        raise RuntimeError(f"unresolved placeholders: {left[:5]}")

    if dry:
        print(f"[DRY RUN] template parses; {len(set(missing))} placeholder path(s) unresolved with the current RESULTS.json:")
        for mp in sorted(set(missing)):
            print("   ", mp)
        return

    with open(OUT, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    print(f"[OK] rendered {OUT} from {TEMPLATE} using {RESULTS_FILE}")


if __name__ == "__main__":
    main()
