# Safety- and Policy-Oriented RUL Upgrade Plan

This document tracks the 8-week upgrade from a C-MAPSS model-comparison project
to a safety-, uncertainty-, and maintenance-policy-oriented RUL study.

## Revised Positioning

The project should no longer be framed as "LSTM/GRU versus classical models".
That comparison is useful as a baseline, but recent C-MAPSS work has already
shown that ordinary benchmark comparisons are crowded. The upgraded paper asks:

> Do RUL models remain useful when judged by late-life safety, optimistic
> overestimation risk, uncertainty calibration, cross-subset transfer, sensor
> perturbation robustness, and maintenance-trigger decision cost?

Working title:

**Safety- and Policy-Oriented Evaluation of Deep Learning Models for Turbofan
Engine Remaining Useful Life Prediction**

## Anchor Literature

| Theme | Anchor | Use in this project |
|---|---|---|
| NASA benchmark | NASA PCoE C-MAPSS repository | Dataset source and scope boundary |
| LSTM/preprocessing baseline | Asif et al. 2022, IEEE Access, DOI `10.1109/ACCESS.2022.3203406` | Shows that preprocessing and RUL label strategy are publishable design points |
| Risk-aware RUL | Xiang et al. 2024, ESWA, DOI `10.1016/j.eswa.2023.121859` | Motivates overestimation risk and uncertainty |
| Domain adaptation | da Costa et al. 2020, RESS, DOI `10.1016/j.ress.2019.106682` | Motivates source-target FD stress tests |
| Realistic flight profiles | Arias Chao et al. 2021, Data, DOI `10.3390/data6010005` | Future bridge to N-CMAPSS |
| Maintenance decisions | Lee and Mitici 2023, RESS, DOI `10.1016/j.ress.2022.108908` | Motivates policy-oriented evaluation |
| Sensor graph/XAI | Zhang et al. 2022, IEEE Sensors Journal, DOI `10.1109/JSEN.2021.3136622` | Motivates sensor-level robustness and explanation |

## Contribution Targets

1. Leakage-safe multi-dataset benchmark on FD001-FD004 where feasible.
2. Safety-aware evaluation with critical-zone RMSE, NASA S-score,
   overestimation ratio, and overestimation magnitude.
3. Uncertainty-aware GRU variants using MC Dropout and Deep Ensemble intervals.
4. Maintenance policy simulation from point predictions and lower confidence
   bounds.
5. Cross-subset and sensor-perturbation stress tests.
6. Figure and table package generated from CSV outputs, not hand-edited values.

## Week-by-Week Execution

| Week | Focus | Main outputs |
|---|---|---|
| 1 | Reframe and sanity-check | Gap analysis vs. Asif 2022; FD002/FD004 loader check; RF/GB/GRU smoke rerun |
| 2 | Multi-subset baseline | FD001/FD003 full 3-seed table; FD002/FD004 representative models if feasible |
| 3 | Safety losses | MSE vs. weighted/asymmetric losses; safety trade-off curves |
| 4 | Uncertainty calibration | MC Dropout / ensemble predictions; PICP, MPIW, Winkler, calibration plots |
| 5 | Maintenance decision simulation | Lead-time cost curves; late maintenance and regret tables |
| 6 | Domain shift and robustness | FD source-target stress tests; sensor noise/masking curves |
| 7 | XAI and failure cases | Feature/occlusion importance; worst-engine diagnostics; final figure set |
| 8 | Paper rewrite and review | Revised LaTeX paper; expanded references; two reviewer rounds |

## Implementation Map

New modules:

- `rul_prediction.uncertainty`: MC Dropout, ensemble intervals, calibration
  metrics.
- `rul_prediction.decision`: threshold and confidence-bound maintenance
  policies.
- `rul_prediction.domain_shift`: source-target FD window preparation.
- `rul_prediction.robustness`: sensor noise and masking perturbations.
- `rul_prediction.xai`: feature importance aggregation and occlusion
  importance.

New scripts:

- `scripts/run_uncertainty.py`
- `scripts/run_decision_simulation.py`
- `scripts/run_domain_shift.py`
- `scripts/run_sensor_robustness.py`
- `scripts/make_upgrade_figures.py`

## Minimum Acceptance Criteria

- Main experimental claims use three seeds or are explicitly marked
  exploratory.
- Every table and figure is reproducible from CSV outputs.
- Claims remain scoped to C-MAPSS simulation data.
- The paper does not claim SOTA, real safety certification, safe RL, or a
  digital twin.
- If FD002/FD004 experiments are too expensive, the final paper reports them as
  representative stress tests rather than full benchmark coverage.

## Fast-Run Examples

```powershell
python scripts/run_uncertainty.py --subset FD001 --method mc_dropout --epochs 3 --mc-samples 5 --out-dir reports/tables/smoke_uncertainty
python scripts/run_decision_simulation.py --predictions reports/tables/smoke_uncertainty/predictions.csv --out-dir reports/tables/smoke_decision
python scripts/run_domain_shift.py --source-subset FD001 --target-subset FD003 --model gradient_boosting --out-dir reports/tables/smoke_domain
python scripts/run_sensor_robustness.py --subset FD001 --model gradient_boosting --out-dir reports/tables/smoke_robustness
```

## 2026-06-26 GPU Handoff Checkpoint

FD002 representative 3-seed experiments are complete for ML baselines, GRU, and
Safety-GRU. The CPU run was stopped before FD004 so the remaining computation
can continue on a GPU laptop.

Key FD002 finding: GRU is best by aggregate RMSE among completed representative
models, while Safety-GRU improves critical-zone and overestimation-risk metrics
at the cost of worse aggregate RMSE. This is direct evidence for the upgraded
paper thesis that accuracy and safety-oriented ranking can diverge.

Next priority on GPU:

1. Finish FD004 representative matrix with RF/GB/GRU/Safety-GRU.
2. Run FD001-FD004 systematic GRU safety-loss ablation.
3. Regenerate matrix and deep-ablation summaries.
4. Add uncertainty/decision experiments on FD001 and FD004.
5. Rewrite the paper around FD001-FD004 safety-oriented benchmark evidence.

See `reports/gpu_handoff_2026-06-26.md` for exact commands.
