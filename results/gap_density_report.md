# Gap vs. local density analysis (N=300 subsamples)

Tests whether instance-level geometry (mean nearest-neighbor distance, d_nn -- lower = denser local clustering) explains the optimality-gap variance, independently of the mechanical effect of dividing by a small W_exact. Spearman rank correlation (n=10 per dataset; small sample, results are suggestive, not conclusive).

  Dataset  target  n  spearman_rho  p_value
      HCV W_exact 10      0.418182 0.229113
      HCV abs_gap 10     -0.018182 0.960240
      HCV pct_gap 10     -0.042424 0.907364
Synthetic W_exact 10      0.454545 0.186905
Synthetic abs_gap 10     -0.648485 0.042540
Synthetic pct_gap 10     -0.745455 0.013330


Per-instance raw table:

  Dataset  Seed     d_nn     W_exact  W_proposed    abs_gap    pct_gap
Synthetic    42 0.013579    0.278809    0.466249   0.187439  67.228493
Synthetic    43 0.012405    0.086444    0.787290   0.700846 810.748890
Synthetic    44 0.013314    0.080252    0.148735   0.068483  85.334854
Synthetic    45 0.013328    0.268534    0.406008   0.137475  51.194702
Synthetic    46 0.013829    0.284429    0.478069   0.193640  68.080425
Synthetic    47 0.012452    0.274452    0.500306   0.225855  82.293087
Synthetic    48 0.012265    0.086966    0.711949   0.624983 718.653085
Synthetic    49 0.013268    0.100260    0.600939   0.500679 499.382714
Synthetic    50 0.013095    0.273119    0.483487   0.210369  77.024647
Synthetic    51 0.013157    0.074340    0.169866   0.095527 128.499799
      HCV    42 1.593060  759.201699  947.412307 188.210607  24.790594
      HCV    43 1.542644  830.498427  898.554727  68.056300   8.194633
      HCV    44 1.601358 1052.975936 1207.391042 154.415106  14.664638
      HCV    45 1.562304  764.165430  956.512798 192.347368  25.170907
      HCV    46 1.565947  702.803882 1129.932498 427.128615  60.774937
      HCV    47 1.580683  668.230995  830.957877 162.726882  24.351891
      HCV    48 1.562956  793.977332  898.983675 105.006343  13.225358
      HCV    49 1.579744  772.737926  940.465104 167.727178  21.705571
      HCV    50 1.612434 1002.892925 1137.808413 134.915488  13.452631
      HCV    51 1.644059 1198.185612 1356.711292 158.525680  13.230478