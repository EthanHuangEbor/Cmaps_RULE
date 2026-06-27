# Research Status

Date: 2026-06-27

This project is now a safety-oriented C-MAPSS RUL benchmark covering FD001-FD004.
It should not be framed as a new SOTA architecture. The current contribution is
a reproducible evaluation workflow that shows how model rankings change when
aggregate accuracy is compared with late-life error and optimistic
overestimation risk.

## Current Evidence

- FD001/FD003: completed multi-seed model matrix for classical baselines and
  deep sequence models, plus focused GRU safety/window/capacity evidence from
  the earlier report package.
- FD002/FD004: completed representative 3-seed matrix for ML baselines, GRU,
  and Safety-GRU.
- FD001-FD004: completed the systematic GRU safety-loss ablation:
  4 subsets x 3 seeds x 8 jobs = 96 training jobs. The aggregated deep-ablation
  table has 192 split-level rows, and metrics/predictions/training-history
  files are complete for every job.
- FD002: the representative matrix shows GRU as strongest by aggregate RMSE,
  while Safety-GRU improves critical-zone error and overestimation metrics.
- FD004: the representative matrix shows Random Forest as strongest by
  aggregate RMSE, while Safety-GRU improves late-life and overestimation-risk
  metrics.
- The full ablation strengthens the main thesis: the aggregate RMSE winner is
  usually not the winner for NASA S-score, critical-zone RMSE, or optimistic
  overestimation risk.

The detailed current roadmap and FD002/FD004 table are in
`reports/progress_roadmap_2026-06-27.md`.

## Latest Ablation Findings

The paper-relevant summaries are tracked in:

- `reports/paper/deep_ablation_test_summary.csv`
- `reports/paper/deep_ablation_best_by_metric.csv`
- `reports/paper/deep_ablation_tradeoff_summary.csv`

Key test-split findings:

- FD001: RMSE is best for `asymmetric_w2_h64_l1_w30`, while
  `safety_w3_h64_l1_w30` is best for NASA S-score, Critical RMSE30/50,
  overestimation ratio, and overestimation magnitude with about a 2.6% RMSE
  cost.
- FD002: RMSE is best for `critical_w2_h64_l1_w30`. Safety/asymmetric losses
  reduce late-life or overestimation risk, but the best risk reductions require
  about 7-21% higher RMSE depending on the metric.
- FD003: `critical_w3_h64_l1_w30` is best for both RMSE and NASA S-score, but
  other safety/asymmetric variants still win individual late-life and
  overestimation metrics.
- FD004: baseline GRU is best for RMSE, while `safety_w2_h64_l1_w30` or
  `safety_w3_h64_l1_w30` are best for safety-oriented metrics. The NASA S-score
  best improves by about 56.5% at about 1.2% RMSE cost; the strongest
  late-life/overestimation reductions cost about 12.7% RMSE.

## Next Required Analysis

Do not start a new primary experiment until the ablation is converted into
paper tables and figures. The next work should be:

- Turn the three `reports/paper/deep_ablation_*.csv` files into manuscript
  tables.
- Add paired seed-level uncertainty or bootstrap checks for the most important
  RMSE-vs-risk comparisons.
- Draft the results section around subset-dependent safety trade-offs, not
  around SOTA architecture claims.

## Deferred Work

Uncertainty, decision simulation, domain shift, sensor robustness, and XAI are
implemented as scaffolds, but should stay secondary until the four-subset
safety-loss ablation is converted into paper-ready evidence.

## Scope Boundaries

- C-MAPSS is simulated benchmark data, not real fleet telemetry.
- Safety-GRU means benchmark loss weighting, not aviation safety certification.
- The project should report strong classical baselines and negative results
  honestly, and should not claim SOTA without broader independent validation.
