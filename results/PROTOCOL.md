# Experimental protocol

Everything needed to interpret the files in this directory: how each dataset is
prepared, how each method was configured, which seeds were used, and which
numbers in the paper are newly generated as opposed to cited.

The companion paper referred to throughout is Ruiz-Olazar, Ihara, Barán and
Méndez-Garabetti, [*Balanced Bipartition into Homogeneous Groups with Positional
Correspondence*](https://55jaiio.sadio.org.ar/wp-content/uploads/2026/07/389.pdf),
55 JAIIO / ASAID 2026.

## Datasets

| dataset | N | D | preprocessing |
|---|---:|---:|---|
| Iris | 150 | 4 | per-column min-max to [0, 1] |
| HCV | 589 | 12 | z-score (`StandardScaler`) |
| Synthetic 2D | 1000 | 2 | per-column min-max to [0, 1] |

HCV is the UCI HCV data set with rows containing missing values dropped, `Sex`
label-encoded, and the first two columns (index, category) excluded. Synthetic
2D is generated at run time, not stored:

```python
make_blobs(n_samples=1000, centers=5, n_features=2, random_state=42)
```

Note that HCV is standardised rather than min-max scaled. This follows the
companion JAIIO paper's original loader, so that the numbers here are directly
comparable to the published ones.

## Odd N: the unmatched element

The objective pairs M = ⌊N/2⌋ elements, so when N is odd one element is left
out and contributes nothing. Among the datasets used here this affects **HCV
only** (N=589): the matching covers 294 pairs and excludes one point. All three
methods use the same ⌊N/2⌋ convention, so their W_pos values remain directly
comparable, but they do *not* choose the excluded element the same way:

- the exact solver selects it jointly while optimising;
- the GA lets it vary, through mutation and its per-individual 2M-of-N sampling;
- *Proposed* fixes it once during construction and never revisits it.

This asymmetry is a limitation of the heuristic rather than a flaw in the
comparison, and it may contribute to HCV's gap; that is untested. Note that
because the *Proposed* and GA implementations are not redistributed here, this
equivalence cannot be fully audited from this repository alone.

## Subsampling

Sub-instances of N=300 are drawn by `common.subsample()`, which is
deterministic given a seed and is used identically by all three methods, so
every method sees the *same* point set for a given (dataset, seed).

- Exact solver and *Proposed*: seeds 42–51 (10 instances).
- GA baseline: seeds 42–46 (5 instances), a prefix of the above.

Because the GA covers only the first five, the sub300 comparison between
*Proposed* and the GA is only partially matched. The defensible test there is
the paired one restricted to those five shared seeds; see the paper.

For those five instances the same seed drives both the subsampling and each
algorithm's own randomness, so instance variability and run-to-run variability
are conflated at that scale. The full-scale results are not affected.

## Methods

### Exact optimum (`exact_matching_baseline.py`)

Complete graph over the points, edge weight = squared Euclidean distance,
solved with `networkx.algorithms.matching.min_weight_matching` (pure-Python
Blossom). This returns a maximum-cardinality minimum-weight matching, i.e.
exactly ⌊N/2⌋ pairs of minimum total weight, which is W_pos optimal. No
bipartite assumption is needed.

Each solve is a single deterministic run; repetitions would be meaningless on
a fixed point set. Solved: full Iris, full Synthetic 2D, full HCV, and the ten
N=300 subsamples of Synthetic 2D and HCV.

**What the reported times cover.** Exact-solver timings are the matching
routine only: the clock starts after the complete graph and its edge weights
have been built. *Proposed* and GA timings cover their optimizer calls. Graph
construction is O(N²) against an O(N³) solve, so its share shrinks as N grows,
and it is small at every scale reported here: 4.7% of the total for Iris
(N=150), 0.9% for HCV (N=589), 0.5% for Synthetic 2D (N=1000). It does not
change any reported figure, but the speed ratios against *Proposed* are
matching-routine comparisons, not end-to-end ones.

Tractability under networkx 3.6.1 (see the README: the version matters):

| N | solve time |
|---|---:|
| 300 | ~5.0 s |
| 500 | ~23.6 s |
| 589 (HCV, full) | 40.7 s |
| 1000 (Synthetic 2D, full) | 202.4 s |

Scaling is close to O(N³) and varies little with dimensionality or with the
point distribution. SIFT and MNIST (N=10,000) were not attempted: cubic
extrapolation from the N=1000 solve gives roughly 56 hours per solve.

### GA baseline

Population 100, tournament size 5, elite fraction 0.05, crossover rate 0.25,
mutation rate 0.25.

Generations were reduced from the original default of 8000 to **1000** for all
runs in this study. A timing test showed 8000 generations was not tractable
for the repetition counts needed across all configurations. This is a scope
reduction, and the paper states it explicitly when comparing against
*Proposed*.

Repetition counts vary by configuration, reflecting the compute budget rather
than a uniformly matched protocol:

| dataset | mode | reps | seeds |
|---|---|---:|---|
| Iris | full | 10 | 42–51 |
| Synthetic 2D | full | 30 | 42–71 |
| HCV | full | 30 | 42–71 |
| Synthetic 2D | sub300 | 5 | 42–46 |
| HCV | sub300 | 5 | 42–46 |

SIFT and MNIST were not run: the implementation is pure Python/NumPy, and at
N=10,000 even a handful of generations is out of reach.

### Proposed heuristic

`swap_iters = 10000`, matching the companion paper's protocol. Full-scale runs
use 30 repetitions (seeds 42–71); subsampled runs use 10, matched to the exact
solver's seeds.

The implementation is not redistributed here (see the README). It is also not
byte-identical to the version that produced the companion paper's published
numbers: in-code comments document three dated post-publication changes to the
greedy constructive phase, and no pre-refactor copy was under version control.

## Statistics

- **Mann–Whitney U**, two-sided, with scipy's `method='exact'` set explicitly.
  The default `'auto'` switches to the asymptotic approximation once the
  smaller sample exceeds size 8, or whenever ties are present, which would
  understate significance for full Iris and for the n=30-vs-30 configurations.
- **Vargha–Delaney A** for every comparison. A=1 means *Proposed* achieves a
  lower cost than the GA on every pairwise draw; A=0.5 means no difference.
- **Wilcoxon signed-rank**, paired, on the five sub300 seeds shared between
  *Proposed* and the GA. This is a matched-pairs design with its own
  assumptions, not a weaker-assumption substitute for Mann–Whitney.

> **Reading `mannwhitney.csv` on sub300.** That file reports the unpaired
> Mann–Whitney for every configuration, and marks the two sub300 rows
> `Significant_at_0.05 = True`. Do not read those two rows as the primary
> evidence: at that scale the samples cover overlapping but unequal instance
> sets, so the unpaired test mixes instance and algorithmic variability. The
> defensible test is the paired Wilcoxon on the five shared seeds, which gives
> **p = 0.0625** for both datasets and therefore does *not* reach p < 0.05. The
> `Design` and `Preferred_test` columns in `mannwhitney.csv` carry this
> caveat, and the paired result is in `effect_sizes.csv`. The full-scale rows
> are unaffected: there the samples are independent and the test is the right
> one.
- Standard deviations use `ddof=1` throughout.
- Optimality gap is
  `(mean_W_method - W_exact) / W_exact * 100`, the same definition for every
  dataset and method.

## Cited versus newly generated

- **Newly generated here**: all exact optima, all GA results, and the
  regenerated *Proposed* per-run values (`raw_*.csv`). Only these are used for
  the statistical comparisons.
- **Cited from the companion JAIIO paper**: the *Proposed* results for SIFT and
  MNIST (N=10,000), and the originally published Iris/Synthetic/HCV values,
  which appear alongside the regenerated ones for comparison. These are labelled
  "JAIIO published, cited" in `summary_wpos_time.csv`.

## Files

| file | contents |
|---|---|
| `raw_exact.csv` | per-solve exact optima and solve times |
| `raw_proposed_matched.csv` | per-run *Proposed* results, matched seeds |
| `raw_ga_*.csv` | per-run GA results by dataset and mode |
| `raw_ga_combined.csv` | the above, concatenated |
| `summary_wpos_time.csv` | W_pos and runtime summary (paper Table 1) |
| `optimality_gap.csv` | gaps against the exact optimum |
| `mannwhitney.csv` | significance tests, *Proposed* vs GA |
| `effect_sizes.csv` | Vargha–Delaney A and paired Wilcoxon |
| `gap_density_instances.csv` | per-instance gap and mean 1-NN distance |
| `gap_density_correlations.csv` | Spearman correlations of the above |
| `summary_full.md`, `gap_density_report.md` | generated human-readable summaries |
