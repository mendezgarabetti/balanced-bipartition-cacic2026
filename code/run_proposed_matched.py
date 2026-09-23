"""
Runs the existing JAIIO "Proposed" heuristic (hybrid_optimizer_c2 from the
read-only hibrido_c2.py) with matched seeds so we have paired raw data for:
  (1) Proposed vs GA on the full-size datasets (Iris, Synthetic 2D, HCV) --
      mirrors the JAIIO protocol (S=10000 swap iters, seeds 42+i).
  (2) Proposed vs Exact on the N=300 subsamples of Synthetic/HCV (+ full
      Iris) used by exact_matching_baseline.py -- for optimality-gap stats.

SIFT and MNIST are NOT rerun here: we cite the JAIIO published numbers
directly for those two datasets (see PROTOCOL.md / analyze_results.py).
"""
import os
import time
import numpy as np
import pandas as pd

from common import (
    get_iris, get_synthetic_2d, get_hcv, subsample, hybrid_optimizer_c2,
    EXACT_SUBSAMPLE_N, EXACT_SUB_SEEDS, RESULTS_DIR,
)

SWAP_ITERS = 10000
FULL_SEEDS = list(range(42, 72))  # 30 reps, seeds 42..71 (matches JAIIO protocol)

DATASETS = {
    "Iris": get_iris,
    "Synthetic": get_synthetic_2d,
    "HCV": get_hcv,
}


def run_full():
    rows = []
    for ds_name, loader in DATASETS.items():
        X, desc = loader()
        print(f"=== Proposed (full): {desc} ===", flush=True)
        for rep, seed in enumerate(FULL_SEEDS, start=1):
            t0 = time.time()
            _, w_pos = hybrid_optimizer_c2(X, swap_iters=SWAP_ITERS, seed=seed)
            t_exec = time.time() - t0
            rows.append({
                "Dataset": ds_name, "Mode": "full", "N": len(X), "Seed": seed,
                "Repetition": rep, "W_pos": w_pos, "Time_s": t_exec,
            })
        last = rows[-len(FULL_SEEDS):]
        vals = [r["W_pos"] for r in last]
        print(f"  -> mean={np.mean(vals):.4f} std={np.std(vals):.4f} "
              f"(n={len(vals)})", flush=True)
    return pd.DataFrame(rows)


def run_subsamples():
    rows = []
    for ds_name, loader in [("Synthetic", get_synthetic_2d), ("HCV", get_hcv)]:
        X_full, desc = loader()
        print(f"=== Proposed (sub{EXACT_SUBSAMPLE_N}): {ds_name} ===", flush=True)
        for rep, seed in enumerate(EXACT_SUB_SEEDS, start=1):
            X_sub, idx = subsample(X_full, EXACT_SUBSAMPLE_N, seed)
            t0 = time.time()
            _, w_pos = hybrid_optimizer_c2(X_sub, swap_iters=SWAP_ITERS, seed=seed)
            t_exec = time.time() - t0
            rows.append({
                "Dataset": ds_name, "Mode": f"sub{EXACT_SUBSAMPLE_N}", "N": len(X_sub),
                "Seed": seed, "Repetition": rep, "W_pos": w_pos, "Time_s": t_exec,
            })
    return pd.DataFrame(rows)


def main():
    df_full = run_full()
    df_sub = run_subsamples()
    df = pd.concat([df_full, df_sub], ignore_index=True)
    out_path = os.path.join(RESULTS_DIR, "raw_proposed_matched.csv")
    df.to_csv(out_path, index=False)
    print(f"\nSaved: {out_path}")
    print(df.groupby(["Dataset", "Mode"])["W_pos"].agg(["mean", "std", "count"]))


if __name__ == "__main__":
    main()
