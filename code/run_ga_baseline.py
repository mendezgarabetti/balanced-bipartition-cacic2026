"""
GA baseline runner. Requires run_ga_c2 from ga_c2.py, which this repository
does not redistribute (see the README).

Cost per generation, measured over 20 generations:
    Iris-full   (N=150,D=4) : ~92 ms/gen  -> 8000 gens ~= 735s/run
    Synth-full  (N=1000,D=2): ~594 ms/gen -> 8000 gens ~= 4750s/run
    HCV-full    (N=589,D=12): ~353 ms/gen -> 8000 gens ~= 2822s/run
    sub300 (D=2 or D=12)    : ~180 ms/gen -> 8000 gens ~= 1450s/run

At those rates the reference 8000-generation protocol is not tractable for
the repetition counts needed across all five configurations, so generations
are reduced to 1000 throughout and repetition counts are set per
configuration according to cost. Both reductions are stated in the paper and
documented in PROTOCOL.md.

This script is invoked once per (dataset, mode) configuration, so the
configurations can run as independent parallel processes. Each invocation
writes its own CSV; --combine merges them.

Usage:
    python3 run_ga_baseline.py --dataset Iris --mode full --reps 10
    python3 run_ga_baseline.py --dataset Synthetic --mode full --reps 30
    python3 run_ga_baseline.py --dataset HCV --mode full --reps 30
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
    get_iris, get_synthetic_2d, get_hcv, subsample, run_ga_c2,
    EXACT_SUBSAMPLE_N, EXACT_SUB_SEEDS, RESULTS_DIR,
)

GENERATIONS = 1000  # reduced from the 8000 "original" default -- see PROTOCOL.md
POP_SIZE = 100
FULL_SEEDS = list(range(42, 72))  # up to 30 available; reps below use a prefix

LOADERS = {
    "Iris": get_iris,
    "Synthetic": get_synthetic_2d,
    "HCV": get_hcv,
}


def run_config(dataset, mode, reps):
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
