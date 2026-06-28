# Cycle-Consistent Safety-Oriented Dual-LSTM RUL Method Spec

Date: 2026-06-28

## Positioning

Paper 2 is a method prototype, not part of Paper 1. Its working direction is:

> Cycle-Consistent Safety-Oriented Dual-LSTM for Aero-Engine RUL Prediction.

The novelty boundary is deliberately narrow. Dual-LSTM has already appeared in RUL literature, and cycle-consistency has appeared in degradation/RUL settings. This project therefore must not claim first-ever Dual-LSTM RUL. The intended contribution is a C-MAPSS aero-engine method that combines target-conditioned degradation transition, cycle-consistency regularization, and Paper 1's safety-oriented evaluation metrics.

## Method Definition

C-MAPSS has no control input, so the soft-robot inverse-control interpretation is not transferable. The adapted model uses:

- Forward RUL branch: `X_t -> z_t -> y_hat_t`.
- Target-conditioned transition branch: `(z_t, horizon k) -> z_hat_{t+k}`.
- Cycle consistency: `head(z_hat_{t+k})` should predict `y_{t+k}`.
- Latent consistency: `z_hat_{t+k}` should align with `stopgrad(encoder(X_{t+k}))`.
- Monotonic regularization: future predicted RUL should not exceed current predicted RUL.
- Inference boundary: test-time prediction uses only the forward branch and the current last window; future windows and true future RUL are never used at inference.

Training pairs are constructed only within the same engine:

```text
(X_t, y_t, X_{t+k}, y_{t+k}, k)
```

The prototype uses `k=1`, `window_size=30`, `max_rul=130`, engine-level validation split, train-only scaling, and last-window test evaluation.

## Implemented Interfaces

- `rul_prediction.data.make_paired_sequence_windows`: creates same-engine paired windows.
- `rul_prediction.models_dual_lstm.CycleConsistentDualLSTM`: forward RUL encoder/head plus transition LSTM.
- `rul_prediction.train_dual_lstm`: trains one Dual-LSTM job and writes the existing experiment schema.
- `scripts/run_dual_lstm_matrix.py`: runs baseline LSTM and Dual-LSTM jobs, then calls existing aggregation/error-analysis modules.

The output schema remains compatible with the existing matrix workflow:

- `metrics.csv`
- `predictions.csv`
- `training_history.csv`
- `selected_features.csv`

Additional trace columns include `pair_horizon`, `lambda_cycle`, `lambda_latent`, and `lambda_mono`.

## Prototype Result

Command:

```powershell
.\.venv\Scripts\python.exe scripts\run_dual_lstm_matrix.py --subsets FD001 --seeds 42 --jobs lstm_baseline_h64_l1_w30 dual_no_cycle_h64_l1_w30 dual_cycle_h64_l1_w30 dual_cycle_safety_w2_h64_l1_w30 --epochs 20 --patience 4 --skip-existing
```

Small summary file:

- `reports/paper2/dual_lstm_fd001_prototype_summary.csv`

FD001 seed 42 test snapshot:

| Job | RMSE | Critical RMSE50 | Overestimation ratio | Overestimation magnitude |
| --- | ---: | ---: | ---: | ---: |
| LSTM baseline | 15.38 | 6.07 | 0.66 | 7.97 |
| Dual-LSTM no-cycle | 14.55 | 5.31 | 0.58 | 5.27 |
| Dual-LSTM cycle | 14.28 | 5.77 | 0.66 | 6.95 |
| Dual-LSTM cycle safety-w2 | 14.92 | 4.58 | 0.43 | 3.07 |

Interpretation: the prototype is technically viable and meets the gate for small validation. The result should not yet be written as a stable scientific claim because it is one subset and one seed only.

## Small Validation Result

Command:

```powershell
.\.venv\Scripts\python.exe scripts\run_dual_lstm_matrix.py --subsets FD001 FD004 --seeds 42 43 44 --jobs lstm_baseline_h64_l1_w30 dual_no_cycle_h64_l1_w30 dual_cycle_h64_l1_w30 dual_cycle_safety_w2_h64_l1_w30 --epochs 30 --patience 5
```

Generated small paper-facing files:

- `reports/paper2/dual_lstm_small_validation_seed_metrics.csv`
- `reports/paper2/dual_lstm_small_validation_summary.csv`
- `reports/paper2/dual_lstm_small_validation_rmse_vs_risk_best.csv`

FD001/FD004 three-seed test means:

| Subset | Job | RMSE | Critical RMSE50 | Overestimation ratio | Overestimation magnitude |
| --- | --- | ---: | ---: | ---: | ---: |
| FD001 | LSTM baseline | 14.98 | 5.83 | 0.63 | 7.17 |
| FD001 | Dual-LSTM cycle | 14.86 | 5.96 | 0.65 | 7.37 |
| FD001 | Dual-LSTM cycle safety-w2 | 14.88 | 5.39 | 0.49 | 4.23 |
| FD004 | LSTM baseline | 23.40 | 22.01 | 0.51 | 9.20 |
| FD004 | Dual-LSTM cycle | 22.32 | 19.19 | 0.55 | 9.00 |
| FD004 | Dual-LSTM cycle safety-w2 | 22.38 | 15.11 | 0.44 | 5.96 |

Interpretation: the small validation gate is passed. The cycle branch improves RMSE relative to the LSTM baseline on both tested subsets. Adding the safety loss gives up little aggregate RMSE relative to the cycle-only job while substantially reducing critical-zone and optimistic-overestimation risk, especially on FD004. This remains a small validation result, not a final Paper 2 claim.

## Full Matrix Result

Command:

```powershell
.\.venv\Scripts\python.exe scripts\run_dual_lstm_matrix.py --subsets FD001 FD002 FD003 FD004 --seeds 42 43 44 --jobs lstm_baseline_h64_l1_w30 dual_no_cycle_h64_l1_w30 dual_cycle_h64_l1_w30 dual_cycle_safety_w2_h64_l1_w30 --epochs 30 --patience 5 --skip-existing
```

Generated full paper-facing files:

- `reports/paper2/dual_lstm_seed_metrics.csv`
- `reports/paper2/dual_lstm_full_summary.csv`
- `reports/paper2/dual_lstm_rmse_vs_risk_best.csv`
- `reports/paper2/claim_evidence_map.csv`
- `reports/paper2/positioning_memo.md`
- `reports/paper2/experiment_plan.md`

Full matrix verification:

- 48 jobs have `metrics.csv`, `predictions.csv`, `training_history.csv`, and `selected_features.csv`.
- `combined_metrics.csv` has 96 rows.
- Every subset/job/split has seeds 42, 43, and 44.
- `claim_evidence_map.csv` marks all four current claim gates as pass.

FD001-FD004 three-seed test means:

| Subset | Job | RMSE | Critical RMSE50 | Overestimation ratio | Overestimation magnitude |
| --- | --- | ---: | ---: | ---: | ---: |
| FD001 | LSTM baseline | 14.98 | 5.83 | 0.63 | 7.17 |
| FD001 | Dual-LSTM cycle | 14.86 | 5.96 | 0.65 | 7.37 |
| FD001 | Dual-LSTM cycle safety-w2 | 14.88 | 5.39 | 0.49 | 4.23 |
| FD002 | LSTM baseline | 18.38 | 8.87 | 0.39 | 4.60 |
| FD002 | Dual-LSTM cycle | 18.06 | 9.54 | 0.43 | 5.50 |
| FD002 | Dual-LSTM cycle safety-w2 | 20.32 | 8.82 | 0.35 | 3.83 |
| FD003 | LSTM baseline | 14.71 | 5.98 | 0.57 | 6.76 |
| FD003 | Dual-LSTM cycle | 14.77 | 5.48 | 0.56 | 6.56 |
| FD003 | Dual-LSTM cycle safety-w2 | 14.37 | 4.33 | 0.43 | 4.65 |
| FD004 | LSTM baseline | 23.40 | 22.01 | 0.51 | 9.20 |
| FD004 | Dual-LSTM cycle | 22.32 | 19.19 | 0.55 | 9.00 |
| FD004 | Dual-LSTM cycle safety-w2 | 22.38 | 15.11 | 0.44 | 5.96 |

Interpretation: the full matrix supports moving Paper 2 into paper-facing analysis. Dual-LSTM cycle is the RMSE-oriented representation control. Dual-LSTM cycle safety-w2 improves late-life or overestimation-risk metrics on at least three subsets, but FD002 requires explicit trade-off wording because the risk-best safety job costs about 13.2% RMSE relative to the RMSE-best Dual-LSTM job. The LSTM baseline trains on all sequence windows, while Dual-LSTM jobs train on paired windows that require a same-engine future window; manuscript claims should therefore describe branch/loss/protocol evidence rather than a pure parameter-count comparison.
