"""
Aggregates raw_exact.csv, raw_proposed_matched.csv, raw_ga_combined.csv into:
  - results/summary_wpos_time.csv / .md   : mean+-std W_pos and time per (Dataset,Mode,Method)
  - results/mannwhitney.csv               : Proposed vs GA, two-sided Mann-Whitney U
  - results/optimality_gap.csv            : (Method - Exact)/Exact * 100, paired by seed
                                             where possible (sub300) or vs the single
                                             deterministic exact value (Iris full).
  - results/summary_full.md               : human-readable combined report, includes
                                             the cited JAIIO-published SIFT/MNIST numbers
                                             (not rerun -- see PROTOCOL.md).
"""
import os
import numpy as np
import pandas as pd
from scipy.stats import mannwhitneyu, wilcoxon

from common import RESULTS_DIR

# JAIIO published "Proposed" numbers (cited directly; also see raw_proposed_matched.csv
# for our own regenerated raw per-run values used for the new stats in this paper).
JAIIO_PUBLISHED = {
    "Synthetic": dict(mean=3.534, std=0.543, min=2.521, max=4.520, time=0.82, N=1000),
    "Iris":      dict(mean=0.918, std=0.036, min=0.843, max=0.983, time=0.70, N=150),
    "HCV":       dict(mean=2083.886, std=93.005, min=1884.077, max=2263.661, time=0.76, N=589),
    "SIFT":      dict(mean=15427.707, std=33.590, min=15371.676, max=15492.184, time=17.29, N=10000),
    "MNIST":     dict(mean=176559.824, std=295.413, min=176074.447, max=177145.002, time=54.70, N=10000),
}


def load_all():
    exact = pd.read_csv(os.path.join(RESULTS_DIR, "raw_exact.csv"))
    proposed = pd.read_csv(os.path.join(RESULTS_DIR, "raw_proposed_matched.csv"))
    ga_path = os.path.join(RESULTS_DIR, "raw_ga_combined.csv")
    ga = pd.read_csv(ga_path) if os.path.exists(ga_path) else pd.DataFrame(
        columns=["Dataset", "Mode", "N", "Seed", "Repetition", "Generations", "W_pos", "Time_s"])
    return exact, proposed, ga


def summary_table(exact, proposed, ga):
    rows = []
    for (ds, mode), grp in proposed.groupby(["Dataset", "Mode"]):
        rows.append({
            "Dataset": ds, "Mode": mode, "Method": "Proposed (this study)",
            "N": grp["N"].iloc[0], "Reps": len(grp),
            "W_pos_mean": grp["W_pos"].mean(), "W_pos_std": grp["W_pos"].std(),
            "W_pos_min": grp["W_pos"].min(), "W_pos_max": grp["W_pos"].max(),
            "Time_mean_s": grp["Time_s"].mean(), "Time_std_s": grp["Time_s"].std(),
        })
    for (ds, mode), grp in ga.groupby(["Dataset", "Mode"]):
        rows.append({
            "Dataset": ds, "Mode": mode, "Method": "GA baseline",
            "N": grp["N"].iloc[0], "Reps": len(grp),
            "W_pos_mean": grp["W_pos"].mean(), "W_pos_std": grp["W_pos"].std(),
            "W_pos_min": grp["W_pos"].min(), "W_pos_max": grp["W_pos"].max(),
            "Time_mean_s": grp["Time_s"].mean(), "Time_std_s": grp["Time_s"].std(),
        })
    for (ds, mode), grp in exact.groupby(["Dataset", "Mode"]):
        rows.append({
            "Dataset": ds, "Mode": mode, "Method": "Exact (Blossom)",
            "N": grp["N"].iloc[0], "Reps": len(grp),
            "W_pos_mean": grp["W_pos"].mean(), "W_pos_std": grp["W_pos"].std(),
            "W_pos_min": grp["W_pos"].min(), "W_pos_max": grp["W_pos"].max(),
            "Time_mean_s": grp["Time_s"].mean(), "Time_std_s": grp["Time_s"].std(),
        })
    for ds, d in JAIIO_PUBLISHED.items():
        rows.append({
            "Dataset": ds, "Mode": "full", "Method": "Proposed (JAIIO published, cited)",
            "N": d["N"], "Reps": 30,
            "W_pos_mean": d["mean"], "W_pos_std": d["std"],
            "W_pos_min": d["min"], "W_pos_max": d["max"],
            "Time_mean_s": d["time"], "Time_std_s": np.nan,
        })
    df = pd.DataFrame(rows)
    return df.sort_values(["Dataset", "Mode", "Method"]).reset_index(drop=True)


def mannwhitney_table(proposed, ga):
    rows = []
    for (ds, mode), ga_grp in ga.groupby(["Dataset", "Mode"]):
        prop_grp = proposed[(proposed.Dataset == ds) & (proposed.Mode == mode)]
        if len(prop_grp) == 0 or len(ga_grp) == 0:
            continue
        stat, p = mannwhitneyu(prop_grp["W_pos"], ga_grp["W_pos"], alternative="two-sided",
                                method="exact")
        rows.append({
            "Dataset": ds, "Mode": mode,
            "n_Proposed": len(prop_grp), "n_GA": len(ga_grp),
            "Proposed_mean": prop_grp["W_pos"].mean(), "GA_mean": ga_grp["W_pos"].mean(),
            "U_stat": stat, "p_value": p,
            "Significant_at_0.05": p < 0.05,
            "Proposed_better": prop_grp["W_pos"].mean() < ga_grp["W_pos"].mean(),
        })
    return pd.DataFrame(rows)


def optimality_gap_table(exact, proposed, ga):
    rows = []
    # Full-scale datasets with a single deterministic exact value: Iris,
    # Synthetic 2D, HCV -- vs 30 Proposed reps / N GA reps each.
    for ds in ["Iris", "Synthetic", "HCV"]:
        exact_full = exact[(exact.Dataset == ds) & (exact.Mode == "full")]
        if len(exact_full) != 1:
            continue
        w_exact = exact_full["W_pos"].iloc[0]
        for method_name, df_m in [("Proposed", proposed), ("GA", ga)]:
            grp = df_m[(df_m.Dataset == ds) & (df_m.Mode == "full")]
            if len(grp) == 0:
                continue
            gaps = (grp["W_pos"].values - w_exact) / w_exact * 100.0
            rows.append({
                "Dataset": ds, "Mode": "full", "Method": method_name,
                "n": len(gaps), "Gap_pct_mean": gaps.mean(), "Gap_pct_std": gaps.std(ddof=1),
                "Gap_pct_min": gaps.min(), "Gap_pct_max": gaps.max(),
            })

    # sub300: paired by (Dataset, Mode, Seed)
    for ds in ["Synthetic", "HCV"]:
        exact_sub = exact[(exact.Dataset == ds) & (exact.Mode == "sub300")][["Seed", "W_pos"]].rename(
            columns={"W_pos": "W_exact"})
        for method_name, df_m in [("Proposed", proposed), ("GA", ga)]:
            grp = df_m[(df_m.Dataset == ds) & (df_m.Mode == "sub300")][["Seed", "W_pos"]]
            if len(grp) == 0:
                continue
            merged = grp.merge(exact_sub, on="Seed", how="inner")
            if len(merged) == 0:
                continue
            gaps = (merged["W_pos"] - merged["W_exact"]) / merged["W_exact"] * 100.0
            rows.append({
                "Dataset": ds, "Mode": "sub300", "Method": method_name,
                "n": len(gaps), "Gap_pct_mean": gaps.mean(), "Gap_pct_std": gaps.std(),
                "Gap_pct_min": gaps.min(), "Gap_pct_max": gaps.max(),
            })
    return pd.DataFrame(rows)


def vargha_delaney_a(x, y):
    """Vargha-Delaney A(x,y) = P(a random x-sample < a random y-sample)
    + 0.5*P(tie). Orientation here: x=Proposed, y=GA, both minimizing
    W_pos, so A close to 1 means Proposed is (stochastically) better
    (lower cost) than GA almost every pairwise comparison; A=0.5 is no
    difference; A close to 0 would mean GA is better."""
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    wins = 0.0
    for xi in x:
        wins += np.sum(xi < y) + 0.5 * np.sum(xi == y)
    return wins / (len(x) * len(y))


def effect_size_table(proposed, ga):
    """Vargha-Delaney A for every (Dataset,Mode) Proposed-vs-GA comparison,
    plus the paired Wilcoxon signed-rank test for the five sub300 seeds
    shared between Proposed and GA (seeds 42-46, see common.py /
    run_ga_baseline.py: the GA's sub300 runs only cover the first five of
    the ten exact-solver seeds)."""
    rows = []
    for (ds, mode), ga_grp in ga.groupby(["Dataset", "Mode"]):
        prop_grp = proposed[(proposed.Dataset == ds) & (proposed.Mode == mode)]
        if len(prop_grp) == 0:
            continue
        A = vargha_delaney_a(prop_grp["W_pos"], ga_grp["W_pos"])
        row = {"Dataset": ds, "Mode": mode, "n_Proposed": len(prop_grp),
               "n_GA": len(ga_grp), "Vargha_Delaney_A": A,
               "Wilcoxon_p": np.nan, "Wilcoxon_n_pairs": np.nan}
        if mode.startswith("sub"):
            shared_seeds = sorted(set(prop_grp["Seed"]) & set(ga_grp["Seed"]))
            if len(shared_seeds) >= 1:
                p_paired = prop_grp[prop_grp.Seed.isin(shared_seeds)].sort_values("Seed")["W_pos"].values
                g_paired = ga_grp[ga_grp.Seed.isin(shared_seeds)].sort_values("Seed")["W_pos"].values
                if len(shared_seeds) >= 2 and not np.allclose(p_paired, g_paired):
                    stat, p_w = wilcoxon(p_paired, g_paired, alternative="two-sided")
                    row["Wilcoxon_p"] = p_w
                    row["Wilcoxon_n_pairs"] = len(shared_seeds)
        rows.append(row)
    return pd.DataFrame(rows)


def to_markdown(df, float_cols=()):
    df2 = df.copy()
    for c in float_cols:
        if c in df2.columns:
            df2[c] = df2[c].map(lambda x: f"{x:.4g}" if pd.notna(x) else "-")
    try:
        return df2.to_markdown(index=False)
    except ImportError:
        # tabulate not installed -- minimal manual markdown fallback
        cols = list(df2.columns)
        lines = ["| " + " | ".join(cols) + " |", "|" + "|".join(["---"] * len(cols)) + "|"]
        for _, r in df2.iterrows():
            lines.append("| " + " | ".join(str(r[c]) for c in cols) + " |")
        return "\n".join(lines)


def main():
    exact, proposed, ga = load_all()

    summary = summary_table(exact, proposed, ga)
    summary.to_csv(os.path.join(RESULTS_DIR, "summary_wpos_time.csv"), index=False)

    mw = mannwhitney_table(proposed, ga)
    mw.to_csv(os.path.join(RESULTS_DIR, "mannwhitney.csv"), index=False)

    gap = optimality_gap_table(exact, proposed, ga)
    gap.to_csv(os.path.join(RESULTS_DIR, "optimality_gap.csv"), index=False)

    eff = effect_size_table(proposed, ga)
    eff.to_csv(os.path.join(RESULTS_DIR, "effect_sizes.csv"), index=False)

    float_cols = ["W_pos_mean", "W_pos_std", "W_pos_min", "W_pos_max", "Time_mean_s", "Time_std_s"]
    md_parts = [
        "# CACIC 2026 -- Results summary\n",
        "## W_pos and runtime (mean +- std over Reps)\n",
        to_markdown(summary, float_cols),
        "\n\n## Proposed vs GA -- Mann-Whitney U (two-sided)\n",
        to_markdown(mw, ["Proposed_mean", "GA_mean", "U_stat", "p_value"]),
        "\n\n## Optimality gap vs Exact (Blossom), % = (Method - Exact)/Exact * 100\n",
        to_markdown(gap, ["Gap_pct_mean", "Gap_pct_std", "Gap_pct_min", "Gap_pct_max"]),
        "\n\n## Vargha-Delaney A (Proposed vs GA, A=1 favors Proposed) "
        "and paired Wilcoxon (sub300 shared seeds)\n",
        to_markdown(eff, ["Vargha_Delaney_A", "Wilcoxon_p"]),
        "\n",
    ]
    md = "\n".join(md_parts)
    with open(os.path.join(RESULTS_DIR, "summary_full.md"), "w") as f:
        f.write(md)

    print(md)
    print(f"\nSaved: summary_wpos_time.csv, mannwhitney.csv, optimality_gap.csv, summary_full.md in {RESULTS_DIR}")


if __name__ == "__main__":
    main()
