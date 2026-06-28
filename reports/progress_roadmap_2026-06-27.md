# Progress Roadmap: Safety-Oriented C-MAPSS RUL Research

Date: 2026-06-27

## Current Position

This repository is now a safety-oriented C-MAPSS RUL benchmark rather than a
plain "deep learning versus classical ML" comparison. The central question is:

> Do model rankings change when RUL predictors are judged by aggregate accuracy,
> late-life error, optimistic overestimation risk, and policy-oriented metrics?

The current evidence now covers FD001-FD004 at two levels:

- A representative model matrix for ML baselines, GRU, and Safety-GRU.
- A systematic GRU safety-loss ablation across all four C-MAPSS subsets.

The strongest paper thread is no longer "which model has the lowest RMSE". It
is the empirically reproducible mismatch between aggregate RMSE rankings and
late-life / overestimation-risk rankings.

## Completed Assets

- Leakage-controlled preprocessing with engine-level validation splits.
- Train-only scaling, capped RUL labels, sliding windows, and last-window test
  evaluation.
- Classical baselines: Ridge, Random Forest, and scikit-learn Gradient
  Boosting fallback.
- Deep baselines: LSTM, GRU, and 1D-CNN for the primary FD001/FD003 matrix.
- Safety-aware GRU variants using critical-zone, asymmetric, and combined
  safety losses.
- Full FD001-FD004 GRU safety-loss ablation: 4 subsets x 3 seeds x 8 jobs = 96
  jobs.
- Metrics: RMSE, MAE, NASA S-score, Critical RMSE30/50, overestimation ratio,
  and overestimation magnitude.
- Runners for matrix experiments, deep ablations, uncertainty, decisions,
  domain shift, sensor robustness, and figure generation.

Generated tables, trained models, and raw NASA files remain local-only and are
ignored by Git. Paper-scale summaries are tracked under `reports/paper/`.

## Latest FD002/FD004 Representative Results

Representative settings: seeds 42/43/44, window size 30, max RUL 130, and
GRU-only deep baselines.

| Subset | Job | Model | RMSE mean | RMSE std | MAE mean | NASA S-score | Critical RMSE30 | Critical RMSE50 | Overestimation ratio | Overestimation magnitude |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| FD002 | deep_default_w30 | GRU | 17.812 | 0.475 | 13.148 | 1526.641 | 6.885 | 10.121 | 0.486 | 6.309 |
| FD002 | ML | Gradient Boosting | 19.890 | 0.199 | 15.947 | 2877.033 | 15.788 | 18.098 | 0.499 | 8.444 |
| FD002 | ML | Random Forest | 18.793 | 0.176 | 14.575 | 2451.565 | 12.066 | 15.376 | 0.492 | 7.230 |
| FD002 | ML | Ridge | 21.038 | 0.059 | 17.265 | 2354.960 | 16.911 | 18.186 | 0.520 | 9.016 |
| FD002 | safety_w2_h64_l1_w30 | Safety-GRU | 20.349 | 0.156 | 15.189 | 1806.993 | 5.053 | 8.124 | 0.308 | 3.410 |
| FD004 | deep_default_w30 | GRU | 21.145 | 0.857 | 15.576 | 6320.352 | 16.436 | 19.486 | 0.522 | 8.459 |
| FD004 | ML | Gradient Boosting | 21.197 | 0.062 | 16.528 | 2854.621 | 16.252 | 19.264 | 0.536 | 9.377 |
| FD004 | ML | Random Forest | 20.183 | 0.193 | 15.065 | 3037.653 | 15.006 | 16.995 | 0.522 | 8.515 |
| FD004 | ML | Ridge | 24.188 | 0.150 | 19.920 | 4198.092 | 24.113 | 26.455 | 0.563 | 11.985 |
| FD004 | safety_w2_h64_l1_w30 | Safety-GRU | 21.931 | 1.151 | 16.326 | 3377.626 | 11.190 | 14.620 | 0.394 | 5.509 |

## Latest Four-Subset Safety-Loss Ablation

Completed on 2026-06-27 with seeds 42/43/44, GRU, window size 30, hidden size
64, one recurrent layer, epochs 60, and patience 8.

Validation status:

- `metrics.csv`: 96 files.
- `predictions.csv`: 96 files.
- `training_history.csv`: 96 files.
- `combined_metrics.csv`: 192 rows.
- Unique subset/seed/job combinations: 96.
- Minimum seeds per subset/job/split: 3.
- Missing expected files: 0.

Runtime note: FD001/FD003 were run before CUDA PyTorch was installed in this
local venv. FD002/FD004 were run after switching to `torch 2.12.1+cu126` on an
RTX 4060 Laptop GPU. The experiment definitions, seeds, data splits, and output
schema are unchanged.

Paper-scale outputs:

- `reports/paper/deep_ablation_test_summary.csv`
- `reports/paper/deep_ablation_best_by_metric.csv`
- `reports/paper/deep_ablation_tradeoff_summary.csv`

### Test-Split Trade-Off Summary

| Subset | RMSE-best job | Safety-risk winner pattern | Main interpretation |
|---|---|---|---|
| FD001 | `asymmetric_w2_h64_l1_w30` | `safety_w3_h64_l1_w30` wins NASA S-score, Critical RMSE30/50, overestimation ratio, and overestimation magnitude. | Safety loss reduces risk metrics with about 2.6% RMSE cost. |
| FD002 | `critical_w2_h64_l1_w30` | Safety/asymmetric variants split the risk-metric wins. | Risk reductions are real but cost about 7-21% RMSE depending on the metric. |
| FD003 | `critical_w3_h64_l1_w30` | RMSE and NASA S-score align, but other variants still win late-life and overestimation metrics. | This is the subset-dependent nuance; do not overclaim universal improvement. |
| FD004 | `baseline_lr1e-3_h64_l1_w30` | `safety_w2_h64_l1_w30` wins NASA S-score; `safety_w3_h64_l1_w30` wins critical and overestimation metrics. | Strongest evidence that RMSE-optimal GRU is not safety-risk optimal. |

Selected effect sizes from `deep_ablation_tradeoff_summary.csv`:

- FD001: `safety_w3_h64_l1_w30` reduces overestimation magnitude by about
  40.4% relative to the RMSE-best job, at about 2.6% higher RMSE.
- FD002: `safety_w3_h64_l1_w30` reduces overestimation magnitude by about
  53.6%, at about 20.6% higher RMSE.
- FD003: `critical_w3_h64_l1_w30` is both RMSE and NASA S-score best, but
  `safety_w3_h64_l1_w30` still reduces overestimation magnitude by about 29.3%
  at about 11.9% higher RMSE.
- FD004: `safety_w2_h64_l1_w30` reduces NASA S-score by about 56.5% at about
  1.2% higher RMSE; `safety_w3_h64_l1_w30` reduces Critical RMSE30 by about
  32.6% and overestimation magnitude by about 49.4% at about 12.7% higher
  RMSE.

## Interpretation

- FD002/FD004 representative results already showed that aggregate accuracy and
  safety-oriented risk metrics rank models differently.
- The full FD001-FD004 ablation confirms that this is not a one-off artifact,
  but it is subset dependent.
- The manuscript should present safety losses as trade-off mechanisms. They can
  reduce dangerous overestimation and late-life error while worsening aggregate
  RMSE.
- FD003 is useful precisely because it is mixed: it prevents the paper from
  sounding like a universal improvement claim.

## Next Priority: Manuscript Tables and Figures

Do not launch a new primary experiment until the current evidence is converted
into paper-ready artifacts. Next steps:

- Build compact tables from `reports/paper/deep_ablation_test_summary.csv` and
  `reports/paper/deep_ablation_tradeoff_summary.csv`.
- Generate one multi-panel figure showing RMSE vs safety-risk trade-offs across
  FD001-FD004.
- Add seed-level confidence intervals or paired checks for the most important
  comparisons.
- Rewrite the results section around the claim: RMSE-optimal model selection can
  understate late-life and optimistic-overestimation risk.

## Decision Rules

- Do not choose models by RMSE alone.
- Report RMSE/MAE together with NASA S-score, Critical RMSE30/50,
  overestimation ratio, and overestimation magnitude.
- Treat safety losses as trade-off mechanisms, not as a guaranteed improvement.
- Keep claims scoped to C-MAPSS simulated benchmark data.

## Paper Direction

Working title:

> Safety-Aware Evaluation of Classical and Deep Sequence Models for Turbofan
> Engine RUL Prediction on C-MAPSS

Contribution statement:

> This project does not claim a new SOTA architecture. It contributes a
> reproducible, leakage-controlled C-MAPSS workflow showing that model rankings
> change when aggregate accuracy is evaluated alongside late-life error and
> optimistic overestimation risk.

The next manuscript rewrite should move from the old FD001/FD003-only framing
to FD001-FD004 safety-loss trade-off evidence. Uncertainty, decision
simulation, domain shift, and sensor robustness should remain secondary until
this core argument is paper-ready.

## Scope Boundaries

- C-MAPSS is simulated benchmark data, not real fleet telemetry.
- Safety-GRU means benchmark loss weighting, not aviation safety certification.
- Decision simulation is hypothetical cost evaluation, not deployable airline
  maintenance scheduling.
- Transformer, TCN, and GNN papers remain related-work context unless
  implemented and evaluated in this repository.
