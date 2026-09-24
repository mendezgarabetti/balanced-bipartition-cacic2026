"""Exact optimum for c=2, via minimum-weight maximum-cardinality matching on the
complete graph (squared Euclidean edge weights), solved with networkx's Blossom
implementation. Each solve is deterministic, so it is run once per point set.

Solves full Iris, full Synthetic 2D, full HCV, and ten N=300 subsamples of the
latter two. SIFT and MNIST (N=10,000) are out of reach for an O(N^3) solver.
Runtimes depend on the networkx version; see results/PROTOCOL.md.
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
