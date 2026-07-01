# TCN Claim Trace And Experiment Gate

Scope: map every current TCN, decision-proxy, and sensitivity-check paper claim to concrete CSV evidence before deciding whether to run a TCN safety-loss experiment.

## Claim-Evidence Map

```text
claim_id                                                                                         extracted_value                                                                                                                                                  evidence_files                                                                                                             interpretation
 TCN-001                                                 baseline-only TCN across FD001-FD004 and seeds 42/43/44                                                                              reports/paper/tcn_matrix_summary.csv; reports/paper/tcn_vs_representative_best.csv                             Use TCN to stress-test benchmark rankings, not to reframe the paper around a new architecture.
 TCN-002                                                                                                     2/4                                                                                                                    reports/paper/tcn_vs_representative_best.csv                                     TCN is competitive on aggregate RMSE in some subsets but does not dominate the matrix.
 TCN-003                                      critical_rmse_50=1/4; overestimation_magnitude=0/2 comparable rows                                                                                                                    reports/paper/tcn_vs_representative_best.csv                                                   TCN cannot be promoted as a risk-best model from baseline-only evidence.
 DEC-001                                                                                          agreement=2/16                                                                                                              reports/paper/decision_proxy_rmse_vs_cost_best.csv                                                 Decision proxy strengthens the safety-oriented ranking-discordance thesis.
 DEC-002                                                              baseline_cost=4/16; sensitivity_cost=19/80                                                                 reports/paper/decision_proxy_best_by_cost.csv; reports/paper/sensitivity_decision_cost_best.csv           TCN is useful as an additional comparator, while Safety-GRU/classical models still explain many risk-best cells.
SENS-001                                                                                          agreement=2/16                                                                                              reports/paper/sensitivity_critical_threshold_rmse_vs_risk_best.csv                                                      RMSE-best rarely matches critical-zone-best across threshold choices.
SENS-002 agreement=10/80; balanced_low=2/16; baseline=2/16; early_penalty=2/16; high_late=2/16; high_missed=2/16                                                                                                   reports/paper/sensitivity_decision_cost_rmse_vs_cost_best.csv                                                                      Agreement remains low under every tested cost schema.
GATE-001                                                                                                   defer reports/paper/tcn_vs_representative_best.csv; reports/paper/decision_proxy_rmse_vs_cost_best.csv; reports/paper/sensitivity_decision_cost_rmse_vs_cost_best.csv Current claims are evaluation claims with sufficient CSV evidence; TCN safety-loss would open a new model-family ablation.
```

## TCN Safety-Loss Gate

```text
                                                     gate_item                                                                                                                                 evidence                                                           decision
                Current manuscript claims need TCN safety-loss                     Claim map frames TCN as baseline/evaluation extension; no current claim requires architecture-specific risk shaping.                                                                 no
                   Baseline TCN already dominates risk metrics                                                                       critical_rmse_50=1/4; overestimation_magnitude=0/2 comparable rows                                                                 no
Ranking-discordance thesis lacks evidence without new training  agreement=2/16; agreement=2/16; agreement=10/80; balanced_low=2/16; baseline=2/16; early_penalty=2/16; high_late=2/16; high_missed=2/16                                                                 no
                                  Recommended immediate action                                                                      All TCN/decision/sensitivity claims now have CSV-backed trace rows. defer TCN safety-loss; integrate claim trace into manuscript first
                Conditional trigger for future TCN safety-loss Run only if manuscript adds architecture-independent safety-loss claims or reviewers ask whether risk shaping transfers from GRU to TCN.                                      conditional future experiment
```

## Decision

- Do not run a TCN safety-loss small experiment immediately.
- The current evidence package supports the evaluation-paper claim: aggregate RMSE, critical-zone risk, and decision-cost rankings separate under multiple checks.
- Treat TCN safety-loss as a conditional future experiment, not a blocker for the next manuscript pass.
