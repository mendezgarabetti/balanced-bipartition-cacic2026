"""
Exact optimum baseline for c=2 via minimum-weight general (non-bipartite)
matching, solved with networkx's Blossom implementation
(networkx.algorithms.matching.min_weight_matching).

Complete graph over N points, edge weight = squared Euclidean distance.
min_weight_matching(G, weight='weight') returns a maximum-cardinality
matching (floor(N/2) pairs) of minimum total weight -- exactly W_pos*
for the c=2 Balanced Bipartition problem.

Tractability (measured on this machine under networkx 3.6.1, see PROTOCOL.md):
    N=300 -> ~5.0s   (uniform random 4.88s; Synthetic 2D 5.06s; HCV 5.29s)
    N=500 -> ~23.6s
    N=589 -> 40.7s   (HCV, full)
    N=1000 -> 202.4s (Synthetic 2D, full)
Scaling is ~O(N^3) and barely depends on D or point distribution.
(An earlier series under networkx 3.4.2 reported ~19s at N=300 and ~88s at
N=500 -- superseded, ~3.7x slower than the current implementation.)
Chosen tractable subsample size: N_SUB = 300.

Runs:
  (a) Full Iris (N=150) -- small enough to solve directly, once (deterministic,
      no repetitions needed: the point set is fixed).
  (b) 10 random subsamples (seeds 42..51) of size N_SUB=300 from Synthetic 2D
      (full N=1000) and from HCV (full N=589), to get mean/std of the exact
      optimum on comparable sub-instances against Proposed/GA run on the
      SAME subsamples (see run_proposed_matched.py / run_ga_baseline.py).
  (c) Full Synthetic 2D (N=1000) and full HCV (N=589) -- a single
      deterministic solve each (the point set is fixed, no repetitions
      needed), used as the full-scale ground truth in Table 1. These two
      turned out tractable (202.4s and 40.7s respectively) despite the
      original framing of this baseline as sub300-only; added here so the
      full-scale W_pos^exact values are versioned raw data rather than a
      one-off number quoted only in PROTOCOL.md/the paper text.
  SIFT and MNIST are skipped entirely: N=10000 is many orders of magnitude
  beyond tractability for this O(N^3) solver -- see PROTOCOL.md.
"""
import os
import time
import numpy as np
import pandas as pd
import networkx as nx
from itertools import combinations

from common import (
    get_iris, get_synthetic_2d, get_hcv, subsample,
    EXACT_SUBSAMPLE_N, EXACT_SUB_SEEDS, RESULTS_DIR,
)


def solve_exact_matching(X):
    """Build complete graph (weight = squared euclidean dist) and solve
    min-weight matching with Blossom (networkx). Returns (tuples, W_pos, solve_time_s)."""
    N = len(X)
    G = nx.Graph()
    G.add_nodes_from(range(N))
    for i, j in combinations(range(N), 2):
        w = float(np.sum((X[i] - X[j]) ** 2))
        G.add_edge(i, j, weight=w)

    t0 = time.time()
    matching = nx.algorithms.matching.min_weight_matching(G, weight="weight")
    t_solve = time.time() - t0

    W_pos = sum(G[u][v]["weight"] for u, v in matching)
    tuples = [[int(u), int(v)] for u, v in matching]
    return tuples, W_pos, t_solve


def main():
    rows = []

    # ── (a) Full Iris, single deterministic solve ─────────────────────────
    print("=== Exact matching: Iris (full, N=150) ===", flush=True)
    X, desc = get_iris()
    tuples, W_pos, t_solve = solve_exact_matching(X)
    print(f"  N={len(X)} pairs={len(tuples)} W_pos={W_pos:.6f} solve_time={t_solve:.2f}s", flush=True)
    rows.append({
        "Dataset": "Iris", "Mode": "full", "N": len(X), "Seed": None,
        "Repetition": 1, "W_pos": W_pos, "Time_s": t_solve,
    })

    # ── (b) Subsamples of Synthetic and HCV ────────────────────────────────
    for ds_name, loader in [("Synthetic", get_synthetic_2d), ("HCV", get_hcv)]:
        print(f"=== Exact matching: {ds_name} (subsample N={EXACT_SUBSAMPLE_N}) ===", flush=True)
        X_full, desc = loader()
        for rep, seed in enumerate(EXACT_SUB_SEEDS, start=1):
            X_sub, idx = subsample(X_full, EXACT_SUBSAMPLE_N, seed)
            tuples, W_pos, t_solve = solve_exact_matching(X_sub)
            print(f"  rep={rep} seed={seed} N={len(X_sub)} W_pos={W_pos:.6f} solve_time={t_solve:.2f}s", flush=True)
            rows.append({
                "Dataset": ds_name, "Mode": f"sub{EXACT_SUBSAMPLE_N}", "N": len(X_sub),
                "Seed": seed, "Repetition": rep, "W_pos": W_pos, "Time_s": t_solve,
            })

    # ── (c) Full-scale Synthetic 2D and HCV, single deterministic solve each ─
    for ds_name, loader in [("Synthetic", get_synthetic_2d), ("HCV", get_hcv)]:
        print(f"=== Exact matching: {ds_name} (full) ===", flush=True)
        X, desc = loader()
        tuples, W_pos, t_solve = solve_exact_matching(X)
        print(f"  N={len(X)} pairs={len(tuples)} W_pos={W_pos:.6f} solve_time={t_solve:.2f}s", flush=True)
        rows.append({
            "Dataset": ds_name, "Mode": "full", "N": len(X), "Seed": None,
            "Repetition": 1, "W_pos": W_pos, "Time_s": t_solve,
        })

    df = pd.DataFrame(rows)
    out_path = os.path.join(RESULTS_DIR, "raw_exact.csv")
    df.to_csv(out_path, index=False)
    print(f"\nSaved: {out_path}")
    print(df.groupby(["Dataset", "Mode"])["W_pos"].agg(["mean", "std", "count"]))


if __name__ == "__main__":
    main()
