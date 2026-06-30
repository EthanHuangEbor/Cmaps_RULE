# Sensitivity Checks Note

Scope: no-retraining sensitivity checks over existing matrix and TCN test predictions.

These checks test whether benchmark conclusions depend on declared critical-zone thresholds or maintenance cost weights. They are not a real fleet scheduler or aviation safety validation.

## Decision Cost Scenarios

- baseline: preventive=1.0, early/cycle=0.02, late=10.0, missed-critical=20.0, critical=30.0
- high_late: preventive=1.0, early/cycle=0.02, late=20.0, missed-critical=20.0, critical=30.0
- high_missed: preventive=1.0, early/cycle=0.02, late=10.0, missed-critical=40.0, critical=30.0
- early_penalty: preventive=1.0, early/cycle=0.05, late=10.0, missed-critical=20.0, critical=30.0
- balanced_low: preventive=1.0, early/cycle=0.02, late=5.0, missed-critical=10.0, critical=30.0

Lead times: 10, 20, 30, and 50 cycles.

## Critical-Threshold Best Models

```text
subset  critical_threshold_checked             model  critical_rmse_mean  critical_overestimation_magnitude_mean
 FD001                        20.0    gru_safety_mse            3.727031                                2.211266
 FD001                        30.0    gru_safety_mse            3.751896                                2.152947
 FD001                        50.0    gru_safety_mse            4.863028                                1.990511
 FD001                        70.0     random_forest            9.796415                                5.464517
 FD002                        20.0    gru_safety_mse            4.890310                                2.044351
 FD002                        30.0    gru_safety_mse            5.053461                                2.150284
 FD002                        50.0    gru_safety_mse            8.123941                                2.719509
 FD002                        70.0    gru_safety_mse           10.909696                                3.921912
 FD003                        20.0     random_forest            2.473897                                1.390966
 FD003                        30.0     random_forest            3.591216                                1.929582
 FD003                        50.0     random_forest            4.761971                                2.432456
 FD003                        70.0 gradient_boosting            9.785512                                5.200826
 FD004                        20.0    gru_safety_mse            9.350960                                5.327351
 FD004                        30.0    gru_safety_mse           11.189882                                6.025870
 FD004                        50.0               tcn           13.720765                                8.931539
 FD004                        70.0    gru_safety_mse           15.966572                                7.654721
```

## Critical Threshold RMSE-Best Vs Risk-Best

```text
subset  critical_threshold_checked   rmse_best_model  rmse_best_rmse critical_best_model  critical_best_rmse  same_model
 FD001                        20.0 gradient_boosting       12.813703      gru_safety_mse            3.727031       False
 FD001                        30.0 gradient_boosting       12.813703      gru_safety_mse            3.751896       False
 FD001                        50.0 gradient_boosting       12.813703      gru_safety_mse            4.863028       False
 FD001                        70.0 gradient_boosting       12.813703       random_forest            9.796415       False
 FD002                        20.0               tcn       16.760626      gru_safety_mse            4.890310       False
 FD002                        30.0               tcn       16.760626      gru_safety_mse            5.053461       False
 FD002                        50.0               tcn       16.760626      gru_safety_mse            8.123941       False
 FD002                        70.0               tcn       16.760626      gru_safety_mse           10.909696       False
 FD003                        20.0 gradient_boosting       13.208708       random_forest            2.473897       False
 FD003                        30.0 gradient_boosting       13.208708       random_forest            3.591216       False
 FD003                        50.0 gradient_boosting       13.208708       random_forest            4.761971       False
 FD003                        70.0 gradient_boosting       13.208708   gradient_boosting            9.785512        True
 FD004                        20.0               tcn       19.279861      gru_safety_mse            9.350960       False
 FD004                        30.0               tcn       19.279861      gru_safety_mse           11.189882       False
 FD004                        50.0               tcn       19.279861                 tcn           13.720765        True
 FD004                        70.0               tcn       19.279861      gru_safety_mse           15.966572       False
```

## Decision Best Models By Cost Scenario

```text
cost_scenario subset  lead_time policy             model  expected_cost_mean  decision_regret_mean  missed_critical_rate_mean
 balanced_low  FD001       10.0   mean             ridge            1.916667              1.846667                   0.183333
 balanced_low  FD001       20.0   mean               tcn            1.289200              1.129200                   0.103333
 balanced_low  FD001       30.0   mean gradient_boosting            0.630533              0.380533                   0.026667
 balanced_low  FD001       50.0   mean    gru_safety_mse            0.414667              0.084667                   0.000000
 balanced_low  FD002       10.0   mean    gru_safety_mse            1.643629              1.558687                   0.144144
 balanced_low  FD002       20.0   mean    gru_safety_mse            0.762085              0.557452                   0.045045
 balanced_low  FD002       30.0   mean    gru_safety_mse            0.367310              0.131789                   0.007722
 balanced_low  FD002       50.0   mean    gru_safety_mse            0.477889              0.138121                   0.000000
 balanced_low  FD003       10.0   mean               tcn            1.215600              1.155600                   0.110000
 balanced_low  FD003       20.0   mean               tcn            0.783000              0.643000                   0.056667
 balanced_low  FD003       30.0   mean    gru_safety_mse            0.404467              0.204467                   0.013333
 balanced_low  FD003       50.0   mean              lstm            0.314933              0.024933                   0.000000
 balanced_low  FD004       10.0   mean             ridge            1.914812              1.858360                   0.169355
 balanced_low  FD004       20.0   mean    gru_safety_mse            1.117661              0.956371                   0.076613
 balanced_low  FD004       30.0   mean    gru_safety_mse            0.686129              0.472419                   0.030914
 balanced_low  FD004       50.0   mean               tcn            0.528172              0.205591                   0.004032
     baseline  FD001       10.0   mean             ridge            3.766667              3.696667                   0.183333
     baseline  FD001       20.0   mean               tcn            2.422533              2.262533                   0.103333
     baseline  FD001       30.0   mean gradient_boosting            1.030533              0.780533                   0.026667
     baseline  FD001       50.0   mean    gru_safety_mse            0.481333              0.151333                   0.000000
     baseline  FD002       10.0   mean    gru_safety_mse            3.194466              3.109524                   0.144144
     baseline  FD002       20.0   mean    gru_safety_mse            1.328366              1.123732                   0.045045
     baseline  FD002       30.0   mean    gru_safety_mse            0.483140              0.247619                   0.007722
     baseline  FD002       50.0   mean    gru_safety_mse            0.567979              0.228211                   0.000000
     baseline  FD003       10.0   mean               tcn            2.332267              2.272267                   0.110000
     baseline  FD003       20.0   mean               tcn            1.416333              1.276333                   0.056667
     baseline  FD003       30.0   mean    gru_safety_mse            0.604467              0.404467                   0.013333
     baseline  FD003       50.0   mean              lstm            0.331600              0.041600                   0.000000
     baseline  FD004       10.0   mean             ridge            3.783091              3.726640                   0.169355
     baseline  FD004       20.0   mean    gru_safety_mse            2.085403              1.924113                   0.076613
     baseline  FD004       30.0   mean    gru_safety_mse            1.149839              0.936129                   0.030914
     baseline  FD004       50.0   mean               tcn            0.736505              0.413925                   0.004032
early_penalty  FD001       10.0   mean             ridge            3.766667              3.696667                   0.183333
early_penalty  FD001       20.0   mean               tcn            2.426333              2.266333                   0.103333
early_penalty  FD001       30.0   mean gradient_boosting            1.031333              0.781333                   0.026667
early_penalty  FD001       50.0   mean    gru_safety_mse            0.493333              0.163333                   0.000000
early_penalty  FD002       10.0   mean    gru_safety_mse            3.196589              3.111647                   0.144144
early_penalty  FD002       20.0   mean    gru_safety_mse            1.330566              1.125933                   0.045045
early_penalty  FD002       30.0   mean    gru_safety_mse            0.487773              0.252252                   0.007722
early_penalty  FD002       50.0   mean    gru_safety_mse            0.589833              0.250064                   0.000000
early_penalty  FD003       10.0   mean               tcn            2.340667              2.280667                   0.110000
early_penalty  FD003       20.0   mean               tcn            1.420833              1.280833                   0.056667
early_penalty  FD003       30.0   mean    gru_safety_mse            0.606167              0.406167                   0.013333
early_penalty  FD003       50.0   mean              lstm            0.334000              0.044000                   0.000000
early_penalty  FD004       10.0   mean             ridge            3.786358              3.729906                   0.169355
early_penalty  FD004       20.0   mean    gru_safety_mse            2.090524              1.929234                   0.076613
early_penalty  FD004       30.0   mean    gru_safety_mse            1.160887              0.947177                   0.030914
early_penalty  FD004       50.0   mean               tcn            0.748522              0.425941                   0.004032
    high_late  FD001       10.0   mean             ridge            3.800000              3.730000                   0.183333
    high_late  FD001       20.0   mean               tcn            2.622533              2.462533                   0.103333
    high_late  FD001       30.0   mean gradient_boosting            1.297200              1.047200                   0.026667
    high_late  FD001       50.0   mean    gru_safety_mse            0.614667              0.284667                   0.000000
    high_late  FD002       10.0   mean    gru_safety_mse            3.413256              3.328314                   0.144144
    high_late  FD002       20.0   mean    gru_safety_mse            1.560026              1.355393                   0.045045
    high_late  FD002       30.0   mean    gru_safety_mse            0.560360              0.324839                   0.007722
    high_late  FD002       50.0   mean    gru_safety_mse            0.748160              0.408391                   0.000000
    high_late  FD003       10.0   mean               tcn            2.365600              2.305600                   0.110000
    high_late  FD003       20.0   mean               tcn            1.549667              1.409667                   0.056667
    high_late  FD003       30.0   mean    gru_safety_mse            0.737800              0.537800                   0.013333
    high_late  FD003       50.0   mean              lstm            0.364933              0.074933                   0.000000
    high_late  FD004       10.0   mean             ridge            4.132554              4.076102                   0.169355
    high_late  FD004       20.0   mean    gru_safety_mse            2.488629              2.327339                   0.076613
    high_late  FD004       30.0   mean    gru_safety_mse            1.458978              1.245269                   0.030914
    high_late  FD004       50.0   mean               tcn            1.072527              0.749946                   0.004032
  high_missed  FD001       10.0   mean             ridge            7.433333              7.363333                   0.183333
  high_missed  FD001       20.0   mean               gru            4.454933              4.294933                   0.100000
  high_missed  FD001       30.0   mean gradient_boosting            1.563867              1.313867                   0.026667
  high_missed  FD001       50.0   mean    gru_safety_mse            0.481333              0.151333                   0.000000
  high_missed  FD002       10.0   mean    gru_safety_mse            6.077349              5.992407                   0.144144
  high_missed  FD002       20.0   mean    gru_safety_mse            2.229266              2.024633                   0.045045
  high_missed  FD002       30.0   mean    gru_safety_mse            0.637580              0.402059                   0.007722
  high_missed  FD002       50.0   mean    gru_safety_mse            0.567979              0.228211                   0.000000
  high_missed  FD003       10.0   mean               tcn            4.532267              4.472267                   0.110000
  high_missed  FD003       20.0   mean               tcn            2.549667              2.409667                   0.056667
  high_missed  FD003       30.0   mean    gru_safety_mse            0.871133              0.671133                   0.013333
  high_missed  FD003       50.0   mean              lstm            0.331600              0.041600                   0.000000
  high_missed  FD004       10.0   mean             ridge            7.170188              7.113737                   0.169355
  high_missed  FD004       20.0   mean    gru_safety_mse            3.617661              3.456371                   0.076613
  high_missed  FD004       30.0   mean    gru_safety_mse            1.768118              1.554409                   0.030914
  high_missed  FD004       50.0   mean               tcn            0.817151              0.494570                   0.004032
```

## Decision RMSE-Best Vs Cost-Best

```text
cost_scenario subset  lead_time policy   rmse_best_model  rmse_best_rmse decision_best_model  decision_best_expected_cost  same_model
 balanced_low  FD001       10.0   mean gradient_boosting       12.813703               ridge                     1.916667       False
 balanced_low  FD001       20.0   mean gradient_boosting       12.813703                 tcn                     1.289200       False
 balanced_low  FD001       30.0   mean gradient_boosting       12.813703   gradient_boosting                     0.630533        True
 balanced_low  FD001       50.0   mean gradient_boosting       12.813703      gru_safety_mse                     0.414667       False
 balanced_low  FD002       10.0   mean               tcn       16.760626      gru_safety_mse                     1.643629       False
 balanced_low  FD002       20.0   mean               tcn       16.760626      gru_safety_mse                     0.762085       False
 balanced_low  FD002       30.0   mean               tcn       16.760626      gru_safety_mse                     0.367310       False
 balanced_low  FD002       50.0   mean               tcn       16.760626      gru_safety_mse                     0.477889       False
 balanced_low  FD003       10.0   mean gradient_boosting       13.208708                 tcn                     1.215600       False
 balanced_low  FD003       20.0   mean gradient_boosting       13.208708                 tcn                     0.783000       False
 balanced_low  FD003       30.0   mean gradient_boosting       13.208708      gru_safety_mse                     0.404467       False
 balanced_low  FD003       50.0   mean gradient_boosting       13.208708                lstm                     0.314933       False
 balanced_low  FD004       10.0   mean               tcn       19.279861               ridge                     1.914812       False
 balanced_low  FD004       20.0   mean               tcn       19.279861      gru_safety_mse                     1.117661       False
 balanced_low  FD004       30.0   mean               tcn       19.279861      gru_safety_mse                     0.686129       False
 balanced_low  FD004       50.0   mean               tcn       19.279861                 tcn                     0.528172        True
     baseline  FD001       10.0   mean gradient_boosting       12.813703               ridge                     3.766667       False
     baseline  FD001       20.0   mean gradient_boosting       12.813703                 tcn                     2.422533       False
     baseline  FD001       30.0   mean gradient_boosting       12.813703   gradient_boosting                     1.030533        True
     baseline  FD001       50.0   mean gradient_boosting       12.813703      gru_safety_mse                     0.481333       False
     baseline  FD002       10.0   mean               tcn       16.760626      gru_safety_mse                     3.194466       False
     baseline  FD002       20.0   mean               tcn       16.760626      gru_safety_mse                     1.328366       False
     baseline  FD002       30.0   mean               tcn       16.760626      gru_safety_mse                     0.483140       False
     baseline  FD002       50.0   mean               tcn       16.760626      gru_safety_mse                     0.567979       False
     baseline  FD003       10.0   mean gradient_boosting       13.208708                 tcn                     2.332267       False
     baseline  FD003       20.0   mean gradient_boosting       13.208708                 tcn                     1.416333       False
     baseline  FD003       30.0   mean gradient_boosting       13.208708      gru_safety_mse                     0.604467       False
     baseline  FD003       50.0   mean gradient_boosting       13.208708                lstm                     0.331600       False
     baseline  FD004       10.0   mean               tcn       19.279861               ridge                     3.783091       False
     baseline  FD004       20.0   mean               tcn       19.279861      gru_safety_mse                     2.085403       False
     baseline  FD004       30.0   mean               tcn       19.279861      gru_safety_mse                     1.149839       False
     baseline  FD004       50.0   mean               tcn       19.279861                 tcn                     0.736505        True
early_penalty  FD001       10.0   mean gradient_boosting       12.813703               ridge                     3.766667       False
early_penalty  FD001       20.0   mean gradient_boosting       12.813703                 tcn                     2.426333       False
early_penalty  FD001       30.0   mean gradient_boosting       12.813703   gradient_boosting                     1.031333        True
early_penalty  FD001       50.0   mean gradient_boosting       12.813703      gru_safety_mse                     0.493333       False
early_penalty  FD002       10.0   mean               tcn       16.760626      gru_safety_mse                     3.196589       False
early_penalty  FD002       20.0   mean               tcn       16.760626      gru_safety_mse                     1.330566       False
early_penalty  FD002       30.0   mean               tcn       16.760626      gru_safety_mse                     0.487773       False
early_penalty  FD002       50.0   mean               tcn       16.760626      gru_safety_mse                     0.589833       False
early_penalty  FD003       10.0   mean gradient_boosting       13.208708                 tcn                     2.340667       False
early_penalty  FD003       20.0   mean gradient_boosting       13.208708                 tcn                     1.420833       False
early_penalty  FD003       30.0   mean gradient_boosting       13.208708      gru_safety_mse                     0.606167       False
early_penalty  FD003       50.0   mean gradient_boosting       13.208708                lstm                     0.334000       False
early_penalty  FD004       10.0   mean               tcn       19.279861               ridge                     3.786358       False
early_penalty  FD004       20.0   mean               tcn       19.279861      gru_safety_mse                     2.090524       False
early_penalty  FD004       30.0   mean               tcn       19.279861      gru_safety_mse                     1.160887       False
early_penalty  FD004       50.0   mean               tcn       19.279861                 tcn                     0.748522        True
    high_late  FD001       10.0   mean gradient_boosting       12.813703               ridge                     3.800000       False
    high_late  FD001       20.0   mean gradient_boosting       12.813703                 tcn                     2.622533       False
    high_late  FD001       30.0   mean gradient_boosting       12.813703   gradient_boosting                     1.297200        True
    high_late  FD001       50.0   mean gradient_boosting       12.813703      gru_safety_mse                     0.614667       False
    high_late  FD002       10.0   mean               tcn       16.760626      gru_safety_mse                     3.413256       False
    high_late  FD002       20.0   mean               tcn       16.760626      gru_safety_mse                     1.560026       False
    high_late  FD002       30.0   mean               tcn       16.760626      gru_safety_mse                     0.560360       False
    high_late  FD002       50.0   mean               tcn       16.760626      gru_safety_mse                     0.748160       False
    high_late  FD003       10.0   mean gradient_boosting       13.208708                 tcn                     2.365600       False
    high_late  FD003       20.0   mean gradient_boosting       13.208708                 tcn                     1.549667       False
    high_late  FD003       30.0   mean gradient_boosting       13.208708      gru_safety_mse                     0.737800       False
    high_late  FD003       50.0   mean gradient_boosting       13.208708                lstm                     0.364933       False
    high_late  FD004       10.0   mean               tcn       19.279861               ridge                     4.132554       False
    high_late  FD004       20.0   mean               tcn       19.279861      gru_safety_mse                     2.488629       False
    high_late  FD004       30.0   mean               tcn       19.279861      gru_safety_mse                     1.458978       False
    high_late  FD004       50.0   mean               tcn       19.279861                 tcn                     1.072527        True
  high_missed  FD001       10.0   mean gradient_boosting       12.813703               ridge                     7.433333       False
  high_missed  FD001       20.0   mean gradient_boosting       12.813703                 gru                     4.454933       False
  high_missed  FD001       30.0   mean gradient_boosting       12.813703   gradient_boosting                     1.563867        True
  high_missed  FD001       50.0   mean gradient_boosting       12.813703      gru_safety_mse                     0.481333       False
  high_missed  FD002       10.0   mean               tcn       16.760626      gru_safety_mse                     6.077349       False
  high_missed  FD002       20.0   mean               tcn       16.760626      gru_safety_mse                     2.229266       False
  high_missed  FD002       30.0   mean               tcn       16.760626      gru_safety_mse                     0.637580       False
  high_missed  FD002       50.0   mean               tcn       16.760626      gru_safety_mse                     0.567979       False
  high_missed  FD003       10.0   mean gradient_boosting       13.208708                 tcn                     4.532267       False
  high_missed  FD003       20.0   mean gradient_boosting       13.208708                 tcn                     2.549667       False
  high_missed  FD003       30.0   mean gradient_boosting       13.208708      gru_safety_mse                     0.871133       False
  high_missed  FD003       50.0   mean gradient_boosting       13.208708                lstm                     0.331600       False
  high_missed  FD004       10.0   mean               tcn       19.279861               ridge                     7.170188       False
  high_missed  FD004       20.0   mean               tcn       19.279861      gru_safety_mse                     3.617661       False
  high_missed  FD004       30.0   mean               tcn       19.279861      gru_safety_mse                     1.768118       False
  high_missed  FD004       50.0   mean               tcn       19.279861                 tcn                     0.817151        True
```

## Reading

- RMSE-best and critical-threshold-best agree in 2/16 subset-threshold cells.
- RMSE-best and decision-cost-best agree in 10/80 scenario-subset-lead-time cells.
- If these agreement rates remain low, the paper can argue ranking discordance is not an artifact of one hand-picked threshold or cost schema.
