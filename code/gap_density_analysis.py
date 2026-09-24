"""Tests whether local point-cloud density explains the optimality-gap variance on
the N=300 subsamples, i.e. whether Proposed's large relative gap on some
instances is a geometric effect rather than an artifact of dividing by a small
W_exact.

Re-runs no optimizer: recomputes a cheap geometric statistic (mean
nearest-neighbour distance) on the same seeded point sets and joins it with the
committed raw per-seed results.
"""
import os
import numpy as np
import pandas as pd
from scipy.spatial import KDTree
from scipy.stats import spearmanr

from common import DATASET_LOADERS, subsample, EXACT_SUBSAMPLE_N, EXACT_SUB_SEEDS, RESULTS_DIR


def mean_nn_distance(X):
    """Mean distance to each point's nearest neighbor (excluding itself)."""
    tree = KDTree(X)
    dists, _ = tree.query(X, k=2)  # k=1 is the point itself (dist 0)
    return float(dists[:, 1].mean())


def build_instance_table():
    exact = pd.read_csv(os.path.join(RESULTS_DIR, "raw_exact.csv"))
    proposed = pd.read_csv(os.path.join(RESULTS_DIR, "raw_proposed_matched.csv"))

    rows = []
    for dataset in ["Synthetic", "HCV"]:
        X, _ = DATASET_LOADERS[dataset]()
        for seed in EXACT_SUB_SEEDS:
            Xs, _ = subsample(X, EXACT_SUBSAMPLE_N, seed)
            d_nn = mean_nn_distance(Xs)

            w_exact_row = exact[(exact.Dataset == dataset) & (exact.Mode == "sub300")
                                 & (exact.Seed == seed)]
            w_prop_row = proposed[(proposed.Dataset == dataset) & (proposed.Mode == "sub300")
                                   & (proposed.Seed == seed)]
            if len(w_exact_row) != 1 or len(w_prop_row) != 1:
                continue
            w_exact = w_exact_row["W_pos"].iloc[0]
            w_prop = w_prop_row["W_pos"].iloc[0]
            abs_gap = w_prop - w_exact
            pct_gap = abs_gap / w_exact * 100.0

            rows.append(dict(Dataset=dataset, Seed=seed, d_nn=d_nn,
                              W_exact=w_exact, W_proposed=w_prop,
                              abs_gap=abs_gap, pct_gap=pct_gap))
    return pd.DataFrame(rows)


def main():
    df = build_instance_table()
    df.to_csv(os.path.join(RESULTS_DIR, "gap_density_instances.csv"), index=False)

    report_lines = ["# Gap vs. local density analysis (N=300 subsamples)\n"]
    report_lines.append(
        "Tests whether instance-level geometry (mean nearest-neighbor distance, "
        "d_nn -- lower = denser local clustering) explains the optimality-gap "
        "variance, independently of the mechanical effect of dividing by a "
        "small W_exact. Spearman rank correlation (n=10 per dataset; small "
        "sample, results are suggestive, not conclusive).\n"
    )
    corr_rows = []
    for dataset, grp in df.groupby("Dataset"):
        for target in ["W_exact", "abs_gap", "pct_gap"]:
            rho, p = spearmanr(grp["d_nn"], grp[target])
            corr_rows.append(dict(Dataset=dataset, target=target, n=len(grp),
                                   spearman_rho=rho, p_value=p))
    corr_df = pd.DataFrame(corr_rows)
    corr_df.to_csv(os.path.join(RESULTS_DIR, "gap_density_correlations.csv"), index=False)

    report_lines.append(corr_df.to_string(index=False))
    report_lines.append("\n\nPer-instance raw table:\n")
    report_lines.append(df.to_string(index=False))

    with open(os.path.join(RESULTS_DIR, "gap_density_report.md"), "w") as f:
        f.write("\n".join(report_lines))

    print("\n".join(report_lines))


if __name__ == "__main__":
    main()
