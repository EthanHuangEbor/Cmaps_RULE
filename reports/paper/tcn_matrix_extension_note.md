# TCN Matrix Extension Note

Scope: baseline TCN only, FD001-FD004, seeds 42/43/44, window size 30, max RUL 130, hidden size 64, 4 temporal blocks, epochs 60, patience 8.

This extension should be read as a stronger sequence baseline for the Paper 1/Paper 2 safety-oriented benchmark, not as a new SOTA claim.

## Test Summary

```text
subset model split  rmse_mean  mae_mean  nasa_s_score_mean  critical_rmse_50_mean  overestimation_ratio_mean  overestimation_magnitude_mean
 FD001   tcn  test  17.313647 13.020024         654.060315              10.673169                   0.550000                       7.315638
 FD002   tcn  test  16.760626 12.725082        1234.049794               8.964733                   0.477477                       5.490921
 FD003   tcn  test  18.890550 13.919684        1245.591310              13.700074                   0.480000                       8.002098
 FD004   tcn  test  19.279861 14.598569        2230.784742              13.720765                   0.517473                       7.322619
```

## Comparison To Representative Matrix Best

Lower is better for every listed metric. Positive deltas mean TCN is worse than the best representative-matrix model for that metric.

```text
subset                   metric   tcn_value representative_best_model  representative_best_value  delta_vs_best  pct_delta_vs_best
 FD001                     rmse   17.313647         gradient_boosting                  12.813703       4.499943          35.118212
 FD001                      mae   13.020024             random_forest                   9.623473       3.396552          35.294452
 FD001             nasa_s_score  654.060315         gradient_boosting                 247.455449     406.604866         164.314372
 FD001         critical_rmse_50   10.673169            gru_safety_mse                   4.863029       5.810140         119.475759
 FD001     overestimation_ratio    0.550000            gru_safety_mse                   0.466667       0.083333          17.857143
 FD001 overestimation_magnitude    7.315638                                                  NaN            NaN                NaN
 FD002                     rmse   16.760626                       gru                  17.811811      -1.051185          -5.901617
 FD002                      mae   12.725082                       gru                  13.148470      -0.423388          -3.220055
 FD002             nasa_s_score 1234.049794                       gru                1526.640567    -292.590773         -19.165662
 FD002         critical_rmse_50    8.964733            gru_safety_mse                   8.123940       0.840793          10.349571
 FD002     overestimation_ratio    0.477477            gru_safety_mse                   0.307593       0.169884          55.230126
 FD002 overestimation_magnitude    5.490921            gru_safety_mse                   3.409616       2.081305          61.042211
 FD003                     rmse   18.890550         gradient_boosting                  13.208708       5.681842          43.015883
 FD003                      mae   13.919684         gradient_boosting                   9.665716       4.253969          44.010902
 FD003             nasa_s_score 1245.591310         gradient_boosting                 311.849730     933.741580         299.420358
 FD003         critical_rmse_50   13.700074             random_forest                   4.761971       8.938102         187.697524
 FD003     overestimation_ratio    0.480000            gru_safety_mse                   0.430000       0.050000          11.627907
 FD003 overestimation_magnitude    8.002098                                                  NaN            NaN                NaN
 FD004                     rmse   19.279861             random_forest                  20.182966      -0.903104          -4.474586
 FD004                      mae   14.598569             random_forest                  15.065328      -0.466759          -3.098233
 FD004             nasa_s_score 2230.784742         gradient_boosting                2854.620600    -623.835858         -21.853547
 FD004         critical_rmse_50   13.720765            gru_safety_mse                  14.619931      -0.899166          -6.150275
 FD004     overestimation_ratio    0.517473            gru_safety_mse                   0.393817       0.123656          31.399317
 FD004 overestimation_magnitude    7.322619            gru_safety_mse                   5.509154       1.813466          32.917319
```

## Initial Reading

- RMSE: TCN matches or improves the representative-matrix best on 2/4 subsets.
- Critical RMSE50: TCN matches or improves the representative-matrix best on 1/4 subsets.
- Overestimation magnitude: comparable values are available on 2/4 subsets.
- Do not promote TCN into the main claim until a decision proxy and sensitivity checks are regenerated.
- Safety-loss TCN has not been run in this extension; risk-shaping claims should still refer to Safety-GRU and Dual-LSTM safety-w2 unless new TCN safety jobs are added.
