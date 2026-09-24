# How Close to Optimal? Benchmarking a Hybrid Heuristic for Balanced Bipartition with Positional Correspondence

Code, data and raw per-run results for the paper presented at **CACIC 2026**
(Congreso Argentino de Ciencias de la Computación), WASI track.

Miguel Méndez-Garabetti, Margarita Ruiz-Olazar, Diego Ihara, Benjamín Barán.

## What this is

Given $N$ points in $\mathbb{R}^D$, *balanced bipartition with positional
correspondence* splits them into two equal-size groups $S_1, S_2$ together with
an explicit one-to-one alignment between them, minimising

$$W_{pos} = \sum_{i=1}^{M} \lVert S_1[i] - S_2[i] \rVert^2, \qquad M = \lfloor N/2 \rfloor .$$

The companion paper — Ruiz-Olazar, Ihara, Barán and Méndez-Garabetti,
[*Balanced Bipartition into Homogeneous Groups with Positional
Correspondence*](https://55jaiio.sadio.org.ar/wp-content/uploads/2026/07/389.pdf),
55 JAIIO / ASAID 2026 — introduced a hybrid heuristic for this problem (KD-Tree
greedy initialisation plus swap-based local search) but left two questions open:
how it compares against a real metaheuristic, and how far its solutions are from
the true optimum.

This repository contains the experiments that close both. The key observation
is that for two groups the objective depends only on *which pairs are formed*,
never on which element of a pair is labelled $S_1$ or $S_2$, so the problem
reduces exactly to **minimum-weight maximum-cardinality matching** on the
complete graph, solvable in polynomial time by Edmonds' Blossom algorithm.
That gives a true optimum to measure against.

## Layout

```
code/      experiment and analysis scripts
data/      the two real datasets (Iris, HCV); Synthetic 2D is generated
results/   raw per-run results, derived statistics, the figure, and the protocol
```

`results/PROTOCOL.md` documents how each dataset is prepared, how each method
was configured, which seeds were used, which scope reductions were applied and
why, and which numbers in the paper are newly generated as opposed to cited.

## Methods compared

| | role | in this repository |
|---|---|---|
| **Proposed** | the hybrid heuristic under evaluation | on request (see below) |
| **GA baseline** | general-purpose metaheuristic, same encoding | on request (see below) |
| **Exact** | true optimum via Blossom matching | `code/exact_matching_baseline.py` |

### Method implementations

The two method implementations, `hibrido_c2.py` (*Proposed*) and `ga_c2.py`
(GA baseline), were written for the [companion JAIIO
paper](https://55jaiio.sadio.org.ar/wp-content/uploads/2026/07/389.pdf) and are
**not redistributed here**; they are available from the authors on request. The
exact solver, which is this paper's own contribution, is included.

### What this package does and does not support

Be precise about the scope. This repository is **analysis code, experimental
data and the exact baseline**: it supports reanalysis of the recorded results
and recomputation of the exact optimum, but not independent rerunning of all
three methods.

Supported:

- `analyze_results.py` recomputes Table 1, the significance tests, the
  optimality gaps and the effect sizes from the committed per-run records;
- `gap_density_analysis.py` and `make_fig_gap_density.py` recompute the
  gap-versus-density analysis and figure;
- `exact_matching_baseline.py` recomputes the exact optima from scratch, since
  the exact baseline is included.

Not supported:

- Rerunning *Proposed* or the GA, which needs the two files above. The scripts
  that call them (`run_proposed_matched.py`, `run_ga_baseline.py`,
  `run_ga_baseline_extra.py`) fail with an explanatory message rather than a
  bare `ImportError`.
- Reconstructing the cited SIFT and MNIST figures, or the originally published
  Iris/Synthetic/HCV values. Those are carried as constants
  (`JAIIO_PUBLISHED` in `analyze_results.py`) transcribed from the companion
  paper; the runs behind them are not part of this deposit.

In short: the statistics reported in the paper can be recomputed and audited
from the recorded results, but *how* the *Proposed* and GA numbers were
produced cannot be independently verified from this package alone.

## Reproducing

```bash
pip install -r requirements.txt

# Verification from the committed raw results -- runs as-is:
python code/analyze_results.py          # Table 1, significance tests, effect sizes
python code/gap_density_analysis.py     # gap vs. local density correlations
python code/make_fig_gap_density.py     # the figure
python code/exact_matching_baseline.py  # recompute the exact optima (slowest; see below)

# Re-running the methods themselves -- needs the two files described above.
# The GA runner takes one configuration at a time:
python code/run_proposed_matched.py

python code/run_ga_baseline.py --dataset Iris      --mode full   --reps 10
python code/run_ga_baseline.py --dataset Synthetic --mode full   --reps 3
python code/run_ga_baseline.py --dataset HCV       --mode full   --reps 3
python code/run_ga_baseline.py --dataset Synthetic --mode sub300 --reps 5
python code/run_ga_baseline.py --dataset HCV       --mode sub300 --reps 5

# Synthetic/HCV full reach 30 repetitions in two steps: the 3 above (seeds
# 42-44) plus 27 more (seeds 45-71) written to separate "_extra" files.
python code/run_ga_baseline_extra.py --seed-start 45 --seed-end 71

python code/run_ga_baseline.py --combine
```

**Follow that sequence as written.** `--reps 30` on Synthetic or HCV full would
rewrite the base file with seeds 42-71, which then collide with the 27 seeds
already in the `_extra` files; `--combine` refuses to merge a set of files that
repeats a (Dataset, Mode, Seed) triple rather than silently double-counting.

Scripts resolve every path relative to the repository root, so it can be
cloned anywhere. Raw results are committed, so the analysis steps can be run
without re-running the experiments.

**Reproducibility level.** Re-running the analysis on the committed raw data
regenerates every derived CSV byte-for-byte, except
`gap_density_instances.csv` and `gap_density_correlations.csv`, which differ in
the 15th–16th significant digit (last-bit floating point). Every value at the
precision reported in the paper is unaffected: Spearman $\rho$ is identical,
and the p-values agree to all reported digits.

### A note on exact-solver runtimes

The exact solver's wall-clock times depend strongly on the NetworkX version.
All timings reported in the paper were measured under **networkx 3.6.1**:

| N | solve time |
|---|---:|
| 300 | ~5.0 s |
| 500 | ~23.6 s |
| 589 (HCV, full) | 40.7 s |
| 1000 (Synthetic 2D, full) | 202.4 s |

Under networkx 3.4.2 the same solves are roughly 3.7× slower. Scaling is close
to $O(N^3)$ and varies little with dimensionality or with the point
distribution; $N$ alone is the dominant factor. If you are comparing runtimes,
pin the version.

## Environment

Results in the paper were produced with Python 3.12.3 on an Intel Core i9-13900
(62 GB RAM, Ubuntu 24.04). Each individual run is single-threaded; independent
configurations were executed in parallel. Package versions used:

```
numpy 2.4.6   pandas 3.0.3      scipy 1.17.1
sklearn 1.8.0  networkx 3.6.1   matplotlib 3.10.9
```

## Data

Both real datasets are redistributed here unmodified, as published by the
[UCI Machine Learning Repository](https://archive.ics.uci.edu/), and keep their
original terms; see `LICENSE`.

- **Iris** (`data/iris_dataset.csv`) — Fisher's iris dataset, originally
  R. A. Fisher, *The use of multiple measurements in taxonomic problems*,
  Annals of Eugenics 7(2):179–188, 1936
  ([doi:10.1111/j.1469-1809.1936.tb02137.x](https://doi.org/10.1111/j.1469-1809.1936.tb02137.x)),
  distributed by UCI. $N=150$, $D=4$, min-max normalised. Public domain in
  practice and unrestricted for research reuse.
- **HCV** (`data/hcvdat0.csv`) — HCV data, Lichtinghagen, Klawonn & Hoffmann,
  UCI Machine Learning Repository, 2020
  ([doi:10.24432/C5D612](https://doi.org/10.24432/C5D612)), licensed
  **CC BY 4.0**: reuse is permitted with attribution. $N=589$ after dropping
  rows with missing values, $D=12$, standardised. De-identified laboratory
  measurements; contains no personal identifiers.
- **Synthetic 2D** — generated at run time by
  `sklearn.datasets.make_blobs(n_samples=1000, centers=5, n_features=2, random_state=42)`,
  min-max normalised. Not stored; reproducible from the seed.

## A caveat on the *Proposed* implementation

The version of `hibrido_c2.py` used here is not byte-identical to the code that
produced the numbers published in the JAIIO companion paper: in-code comments
document three dated post-publication changes to the greedy constructive phase.
No pre-refactor copy was under version control. The paper therefore reports both the originally
published values (cited) and freshly regenerated per-run values, and uses only
the latter for the statistical comparisons. See `results/PROTOCOL.md`.

## License

Code is released under the MIT License (`LICENSE`). The bundled datasets retain
their original terms from the UCI Machine Learning Repository.

## Citation

```bibtex
@inproceedings{mendezgarabetti2026howclose,
  author    = {M\'endez-Garabetti, Miguel and Ruiz-Olazar, Margarita
               and Ihara, Diego and Bar\'an, Benjam\'in},
  title     = {How Close to Optimal? Benchmarking a Hybrid Heuristic for
               Balanced Bipartition with Positional Correspondence Against
               Exact and Evolutionary Baselines},
  booktitle = {Congreso Argentino de Ciencias de la Computaci\'on (CACIC)},
  year      = {2026}
}
```
