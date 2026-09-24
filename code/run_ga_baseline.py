"""GA baseline runner. Needs run_ga_c2 from ga_c2.py, which this repository does
not redistribute (see the README).

Generations are reduced from the reference 8000 to 1000, and repetition counts
are set per configuration according to cost; see results/PROTOCOL.md. One
invocation per (dataset, mode) so configurations can run in parallel, each
writing its own CSV; --combine merges them.

Synthetic/HCV full reach their 30 repetitions in two steps: 3 here (seeds
42-44) plus 27 from run_ga_baseline_extra.py (seeds 45-71), kept in separate
"_extra" files. Passing --reps 30 here instead would rewrite the base file
with seeds 42-71 and collide with those; --combine rejects such a merge.

Usage:
    python3 run_ga_baseline.py --dataset Iris --mode full --reps 10
    python3 run_ga_baseline.py --dataset Synthetic --mode full --reps 3
    python3 run_ga_baseline.py --dataset HCV --mode full --reps 3
    python3 run_ga_baseline.py --dataset Synthetic --mode sub300 --reps 5
    python3 run_ga_baseline.py --dataset HCV --mode sub300 --reps 5
    python3 run_ga_baseline.py --combine
"""
import argparse
import glob
import os
import time
import numpy as np
import pandas as pd

from common import (
    get_iris, get_synthetic_2d, get_hcv, subsample,
    EXACT_SUBSAMPLE_N, EXACT_SUB_SEEDS, RESULTS_DIR,
)

# run_ga_c2 is imported inside run_config() rather than here, so that --combine,
# which only merges CSVs, works without the GA implementation (see the README).

GENERATIONS = 1000  # reduced from the 8000 "original" default -- see PROTOCOL.md
POP_SIZE = 100
FULL_SEEDS = list(range(42, 72))  # up to 30 available; reps below use a prefix

LOADERS = {
    "Iris": get_iris,
    "Synthetic": get_synthetic_2d,
    "HCV": get_hcv,
}


def run_config(dataset, mode, reps):
    from common import run_ga_c2

    loader = LOADERS[dataset]
    X_full, desc = loader()
    rows = []

    if mode == "full":
        seeds = FULL_SEEDS[:reps]
        X = X_full
        for rep, seed in enumerate(seeds, start=1):
            M = len(X) // 2
            t0 = time.time()
            _, w_pos = run_ga_c2(X, M, generations=GENERATIONS, pop_size=POP_SIZE, seed=seed)
            t_exec = time.time() - t0
            rows.append({
                "Dataset": dataset, "Mode": "full", "N": len(X), "Seed": seed,
                "Repetition": rep, "Generations": GENERATIONS, "W_pos": w_pos, "Time_s": t_exec,
            })
            print(f"[{dataset}/full] rep={rep} seed={seed} W_pos={w_pos:.4f} time={t_exec:.1f}s", flush=True)
    elif mode == "sub300":
        seeds = EXACT_SUB_SEEDS[:reps]  # paired with exact_matching_baseline.py's first `reps` seeds
        for rep, seed in enumerate(seeds, start=1):
            X_sub, idx = subsample(X_full, EXACT_SUBSAMPLE_N, seed)
            M = len(X_sub) // 2
            t0 = time.time()
            _, w_pos = run_ga_c2(X_sub, M, generations=GENERATIONS, pop_size=POP_SIZE, seed=seed)
            t_exec = time.time() - t0
            rows.append({
                "Dataset": dataset, "Mode": "sub300", "N": len(X_sub), "Seed": seed,
                "Repetition": rep, "Generations": GENERATIONS, "W_pos": w_pos, "Time_s": t_exec,
            })
            print(f"[{dataset}/sub300] rep={rep} seed={seed} W_pos={w_pos:.4f} time={t_exec:.1f}s", flush=True)
    else:
        raise ValueError(mode)

    df = pd.DataFrame(rows)
    out_path = os.path.join(RESULTS_DIR, f"raw_ga_{dataset}_{mode}.csv")
    df.to_csv(out_path, index=False)
    print(f"Saved: {out_path}")
    return df


def combine():
    files = glob.glob(os.path.join(RESULTS_DIR, "raw_ga_*.csv"))
    files = [f for f in files if not f.endswith("raw_ga_combined.csv")]
    dfs = [pd.read_csv(f) for f in sorted(files)]
    if not dfs:
        print("No raw_ga_*.csv files found to combine.")
        return
    df = pd.concat(dfs, ignore_index=True)

    # A repeated (Dataset, Mode, Seed) means two files describe the same run,
    # which would silently double-count it. Refuse rather than guess which wins.
    key = ["Dataset", "Mode", "Seed"]
    dupes = df[df.duplicated(key, keep=False)]
    if not dupes.empty:
        print("Refusing to combine: the same (Dataset, Mode, Seed) appears more than once.")
        for (ds, mode), grp in dupes.groupby(["Dataset", "Mode"]):
            seeds = sorted(grp["Seed"].unique())
            print(f"  {ds}/{mode}: {len(seeds)} repeated seed(s) {seeds[0]}..{seeds[-1]}")
        print(
            "\nThis usually means a base file was regenerated with a --reps value that\n"
            "overlaps the '_extra' seeds. Synthetic/HCV full expect 3 reps here (seeds\n"
            "42-44) plus 27 from run_ga_baseline_extra.py (seeds 45-71); see the README.\n"
            "Remove or regenerate the conflicting file, then combine again."
        )
        raise SystemExit(1)

    out_path = os.path.join(RESULTS_DIR, "raw_ga_combined.csv")
    df.to_csv(out_path, index=False)
    print(f"Combined {len(files)} files -> {out_path}")
    print(df.groupby(["Dataset", "Mode"])["W_pos"].agg(["mean", "std", "count"]))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--dataset", choices=list(LOADERS.keys()))
    ap.add_argument("--mode", choices=["full", "sub300"])
    ap.add_argument("--reps", type=int)
    ap.add_argument("--combine", action="store_true")
    args = ap.parse_args()

    if args.combine:
        combine()
    else:
        assert args.dataset and args.mode and args.reps, "need --dataset --mode --reps (or --combine)"
        run_config(args.dataset, args.mode, args.reps)
