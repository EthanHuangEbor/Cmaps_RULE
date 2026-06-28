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

- `reports/paper/dual_lstm_fd001_prototype_summary.csv`

FD001 seed 42 test snapshot:

| Job | RMSE | Critical RMSE50 | Overestimation ratio | Overestimation magnitude |
| --- | ---: | ---: | ---: | ---: |
| LSTM baseline | 15.38 | 6.07 | 0.66 | 7.97 |
| Dual-LSTM no-cycle | 14.55 | 5.31 | 0.58 | 5.27 |
| Dual-LSTM cycle | 14.28 | 5.77 | 0.66 | 6.95 |
| Dual-LSTM cycle safety-w2 | 14.92 | 4.58 | 0.43 | 3.07 |

Interpretation: the prototype is technically viable and meets the gate for small validation. The result should not yet be written as a stable scientific claim because it is one subset and one seed only.

## Next Gate

Run small validation only after Paper 1 remains stable:

```powershell
.\.venv\Scripts\python.exe scripts\run_dual_lstm_matrix.py --subsets FD001 FD004 --seeds 42 43 44 --jobs lstm_baseline_h64_l1_w30 dual_no_cycle_h64_l1_w30 dual_cycle_h64_l1_w30 dual_cycle_safety_w2_h64_l1_w30 --epochs 30 --patience 5 --skip-existing
```

Proceed to the full FD001-FD004 matrix only if FD001/FD004 small validation shows a repeatable improvement in at least one safety-risk metric with explainable RMSE cost.
