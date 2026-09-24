# CACIC 2026 -- Results summary

## W_pos and runtime (mean +- std over Reps)

| Dataset | Mode | Method | N | Reps | W_pos_mean | W_pos_std | W_pos_min | W_pos_max | Time_mean_s | Time_std_s |
|---|---|---|---|---|---|---|---|---|---|---|
| HCV | full | Exact (Blossom) | 589 | 1 | 1208 | - | 1208 | 1208 | 40.72 | - |
| HCV | full | GA baseline | 589 | 30 | 4307 | 123.8 | 4046 | 4559 | 306.3 | 107.7 |
| HCV | full | Proposed (JAIIO published, cited) | 589 | 30 | 2084 | 93 | 1884 | 2264 | 0.76 | - |
| HCV | full | Proposed (this study) | 589 | 30 | 1840 | 110.4 | 1583 | 2106 | 1.447 | 0.2128 |
| HCV | sub300 | Exact (Blossom) | 300 | 10 | 854.6 | 171.7 | 668.2 | 1198 | 5.102 | 0.1838 |
| HCV | sub300 | GA baseline | 300 | 5 | 1881 | 116.3 | 1771 | 2047 | 314.4 | 15.22 |
| HCV | sub300 | Proposed (this study) | 300 | 10 | 1030 | 168 | 831 | 1357 | 1.414 | 0.08835 |
| Iris | full | Exact (Blossom) | 150 | 1 | 0.7684 | - | 0.7684 | 0.7684 | 0.4898 | - |
| Iris | full | GA baseline | 150 | 10 | 6.237 | 0.782 | 5.187 | 7.576 | 161.7 | 13.59 |
| Iris | full | Proposed (JAIIO published, cited) | 150 | 30 | 0.918 | 0.036 | 0.843 | 0.983 | 0.7 | - |
| Iris | full | Proposed (this study) | 150 | 30 | 1.011 | 0.182 | 0.8625 | 1.595 | 0.7212 | 0.03133 |
| MNIST | full | Proposed (JAIIO published, cited) | 10000 | 30 | 1.766e+05 | 295.4 | 1.761e+05 | 1.771e+05 | 54.7 | - |
| SIFT | full | Proposed (JAIIO published, cited) | 10000 | 30 | 1.543e+04 | 33.59 | 1.537e+04 | 1.549e+04 | 17.29 | - |
| Synthetic | full | Exact (Blossom) | 1000 | 1 | 0.08788 | - | 0.08788 | 0.08788 | 202.4 | - |
| Synthetic | full | GA baseline | 1000 | 30 | 77.42 | 2.918 | 70.03 | 83.62 | 635.7 | 136.1 |
| Synthetic | full | Proposed (JAIIO published, cited) | 1000 | 30 | 3.534 | 0.543 | 2.521 | 4.52 | 0.82 | - |
| Synthetic | full | Proposed (this study) | 1000 | 30 | 1.765 | 0.484 | 0.6 | 3.152 | 1.195 | 0.3556 |
| Synthetic | sub300 | Exact (Blossom) | 300 | 10 | 0.1808 | 0.1005 | 0.07434 | 0.2844 | 4.816 | 0.191 |
| Synthetic | sub300 | GA baseline | 300 | 5 | 12.18 | 1.349 | 10.17 | 13.42 | 312.7 | 15.99 |
| Synthetic | sub300 | Proposed (this study) | 300 | 10 | 0.4753 | 0.204 | 0.1487 | 0.7873 | 1.461 | 0.06641 |


## Proposed vs GA -- Mann-Whitney U (two-sided)

| Dataset | Mode | n_Proposed | n_GA | Proposed_mean | GA_mean | U_stat | p_value | Significant_at_0.05 | Proposed_better | Design | Preferred_test |
|---|---|---|---|---|---|---|---|---|---|---|---|
| HCV | full | 30 | 30 | 1840 | 4307 | 0 | 1.691e-17 | True | True | independent samples | this Mann-Whitney U |
| HCV | sub300 | 10 | 5 | 1030 | 1881 | 0 | 0.000666 | True | True | partially matched instances | paired Wilcoxon on shared seeds (see effect_sizes.csv) |
| Iris | full | 30 | 10 | 1.011 | 6.237 | 0 | 2.359e-09 | True | True | independent samples | this Mann-Whitney U |
| Synthetic | full | 30 | 30 | 1.765 | 77.42 | 0 | 1.691e-17 | True | True | independent samples | this Mann-Whitney U |
| Synthetic | sub300 | 10 | 5 | 0.4753 | 12.18 | 0 | 0.000666 | True | True | partially matched instances | paired Wilcoxon on shared seeds (see effect_sizes.csv) |


## Optimality gap vs Exact (Blossom), % = (Method - Exact)/Exact * 100

| Dataset | Mode | Method | n | Gap_pct_mean | Gap_pct_std | Gap_pct_min | Gap_pct_max |
|---|---|---|---|---|---|---|---|
| Iris | full | Proposed | 30 | 31.55 | 23.69 | 12.24 | 107.5 |
| Iris | full | GA | 10 | 711.7 | 101.8 | 575 | 885.9 |
| Synthetic | full | Proposed | 30 | 1909 | 550.8 | 582.7 | 3487 |
| Synthetic | full | GA | 30 | 8.799e+04 | 3320 | 7.958e+04 | 9.505e+04 |
| HCV | full | Proposed | 30 | 52.34 | 9.137 | 31.06 | 74.34 |
| HCV | full | GA | 30 | 256.5 | 10.25 | 234.9 | 277.4 |
| Synthetic | sub300 | Proposed | 10 | 258.8 | 298.4 | 51.19 | 810.7 |
| Synthetic | sub300 | GA | 5 | 8161 | 5259 | 4178 | 1.574e+04 |
| HCV | sub300 | Proposed | 10 | 21.96 | 14.9 | 8.195 | 60.77 |
| HCV | sub300 | GA | 5 | 132.1 | 26.89 | 94.36 | 154.7 |


## Vargha-Delaney A (Proposed vs GA, A=1 favors Proposed) and paired Wilcoxon (sub300 shared seeds)

| Dataset | Mode | n_Proposed | n_GA | Vargha_Delaney_A | Wilcoxon_p | Wilcoxon_n_pairs |
|---|---|---|---|---|---|---|
| HCV | full | 30 | 30 | 1 | - | nan |
| HCV | sub300 | 10 | 5 | 1 | 0.0625 | 5.0 |
| Iris | full | 30 | 10 | 1 | - | nan |
| Synthetic | full | 30 | 30 | 1 | - | nan |
| Synthetic | sub300 | 10 | 5 | 1 | 0.0625 | 5.0 |

