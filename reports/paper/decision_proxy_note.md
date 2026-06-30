# Decision Proxy Extension Note

Scope: benchmark-derived maintenance decision proxy using existing test predictions. This is not a real fleet cost model.

Cost schema: preventive cost = 1, early cost per cycle = 0.02, late cost = 10, missed-critical cost = 20, critical threshold = 30 cycles.

Lead times: 10, 20, 30, and 50 cycles. Lower expected cost and decision regret are better.

## Best By Expected Cost

```text
subset  lead_time policy             model  expected_cost_mean  decision_regret_mean  missed_critical_rate_mean
 FD001       10.0   mean             ridge            3.766667              3.696667                   0.183333
 FD001       20.0   mean               tcn            2.422533              2.262533                   0.103333
 FD001       30.0   mean gradient_boosting            1.030533              0.780533                   0.026667
 FD001       50.0   mean    gru_safety_mse            0.481333              0.151333                   0.000000
 FD002       10.0   mean    gru_safety_mse            3.194466              3.109524                   0.144144
 FD002       20.0   mean    gru_safety_mse            1.328366              1.123732                   0.045045
 FD002       30.0   mean    gru_safety_mse            0.483140              0.247619                   0.007722
 FD002       50.0   mean    gru_safety_mse            0.567979              0.228211                   0.000000
 FD003       10.0   mean               tcn            2.332267              2.272267                   0.110000
 FD003       20.0   mean               tcn            1.416333              1.276333                   0.056667
 FD003       30.0   mean    gru_safety_mse            0.604467              0.404467                   0.013333
 FD003       50.0   mean              lstm            0.331600              0.041600                   0.000000
 FD004       10.0   mean             ridge            3.783091              3.726640                   0.169355
 FD004       20.0   mean    gru_safety_mse            2.085403              1.924113                   0.076613
 FD004       30.0   mean    gru_safety_mse            1.149839              0.936129                   0.030914
 FD004       50.0   mean               tcn            0.736505              0.413925                   0.004032
```

## RMSE-Best Vs Decision-Best

```text
subset  lead_time policy   rmse_best_model  rmse_best_rmse decision_best_model  decision_best_expected_cost  same_model
 FD001       10.0   mean gradient_boosting       12.813703               ridge                     3.766667       False
 FD001       20.0   mean gradient_boosting       12.813703                 tcn                     2.422533       False
 FD001       30.0   mean gradient_boosting       12.813703   gradient_boosting                     1.030533        True
 FD001       50.0   mean gradient_boosting       12.813703      gru_safety_mse                     0.481333       False
 FD002       10.0   mean               tcn       16.760626      gru_safety_mse                     3.194466       False
 FD002       20.0   mean               tcn       16.760626      gru_safety_mse                     1.328366       False
 FD002       30.0   mean               tcn       16.760626      gru_safety_mse                     0.483140       False
 FD002       50.0   mean               tcn       16.760626      gru_safety_mse                     0.567979       False
 FD003       10.0   mean gradient_boosting       13.208708                 tcn                     2.332267       False
 FD003       20.0   mean gradient_boosting       13.208708                 tcn                     1.416333       False
 FD003       30.0   mean gradient_boosting       13.208708      gru_safety_mse                     0.604467       False
 FD003       50.0   mean gradient_boosting       13.208708                lstm                     0.331600       False
 FD004       10.0   mean               tcn       19.279861               ridge                     3.783091       False
 FD004       20.0   mean               tcn       19.279861      gru_safety_mse                     2.085403       False
 FD004       30.0   mean               tcn       19.279861      gru_safety_mse                     1.149839       False
 FD004       50.0   mean               tcn       19.279861                 tcn                     0.736505        True
```

## Initial Reading

- RMSE-best and decision-best agree in 2/16 subset-lead-time cells.
- Treat this as a declared-preference decision proxy, not as a validated maintenance scheduler.
- If decision-best changes after adding TCN, report the raw cost components alongside RMSE and risk metrics.
