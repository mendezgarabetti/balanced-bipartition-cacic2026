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

This does not limit verification. Every number in every table and figure can
be checked from the raw per-run results committed under `results/`:

- `analyze_results.py` regenerates Table 1, the significance tests, the
  optimality gaps and the effect sizes;
- `gap_density_analysis.py` and `make_fig_gap_density.py` regenerate the
  gap-versus-density analysis and figure;
- `exact_matching_baseline.py` recomputes the exact optima from scratch.

Only re-running *Proposed* or the GA from scratch needs the two files above.
The scripts that require them (`run_proposed_matched.py`,
`run_ga_baseline.py`, `run_ga_baseline_extra.py`) fail with an explanatory
message rather than a bare `ImportError`.

## Reproducing

```bash
pip install -r requirements.txt

# Verification from the committed raw results -- runs as-is:
python code/analyze_results.py          # Table 1, significance tests, effect sizes
python code/gap_density_analysis.py     # gap vs. local density correlations
python code/make_fig_gap_density.py     # the figure
python code/exact_matching_baseline.py  # recompute the exact optima (slowest; see below)

# Re-running the methods themselves -- needs the two files described above:
python code/run_proposed_matched.py     # heuristic, matched seeds
python code/run_ga_baseline.py          # GA baseline
python code/run_ga_baseline_extra.py    # GA, extra repetitions (n=3 -> n=30)
```

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

- **Iris** (`data/iris_dataset.csv`) — Fisher's iris dataset, UCI Machine
  Learning Repository. $N=150$, $D=4$, min-max normalised.
- **HCV** (`data/hcvdat0.csv`) — HCV data set, Lichtinghagen, Klawonn & Hoffmann,
  UCI Machine Learning Repository (CC BY 4.0). $N=589$ after dropping rows with
  missing values, $D=12$, standardised. Contains no personal identifiers.
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
