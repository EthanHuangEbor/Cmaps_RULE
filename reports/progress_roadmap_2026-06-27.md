# Progress Roadmap: Safety-Oriented C-MAPSS RUL Research

Date: 2026-06-27

## Current Position

This repository is now a safety-oriented C-MAPSS RUL benchmark rather than a
plain "deep learning versus classical ML" comparison. The central question is:

> Do model rankings change when RUL predictors are judged by aggregate accuracy,
> late-life error, optimistic overestimation risk, and policy-oriented metrics?

The current evidence covers FD001-FD004. FD001 and FD003 contain the broader
model comparison used in the earlier report. FD002 and FD004 now have a
representative 3-seed stress matrix with ML baselines, GRU, and Safety-GRU.

## Completed Assets

- Leakage-controlled preprocessing with engine-level validation splits.
- Train-only scaling, capped RUL labels, sliding windows, and last-window test
  evaluation.
- Classical baselines: Ridge, Random Forest, and scikit-learn Gradient
  Boosting fallback.
- Deep baselines: LSTM, GRU, and 1D-CNN for the primary FD001/FD003 matrix.
- Safety-aware GRU variants using critical-zone, asymmetric, and combined
  safety losses.
- Metrics: RMSE, MAE, NASA S-score, Critical RMSE30/50, overestimation ratio,
  and overestimation magnitude.
- Runners for matrix experiments, deep ablations, uncertainty, decisions,
  domain shift, sensor robustness, and figure generation.

Generated tables, trained models, and raw NASA files remain local-only and are
ignored by Git.

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

## Interpretation

- FD002: GRU is the aggregate RMSE winner among representative models, while
  Safety-GRU gives the best late-life and overestimation-risk profile.
- FD004: Random Forest is the aggregate RMSE winner. Safety-GRU is not the
  aggregate winner, but it substantially improves Critical RMSE30/50 and
  overestimation risk compared with ordinary GRU.
- Across FD002/FD004, aggregate accuracy and safety-oriented risk metrics rank
  models differently. This is the strongest current paper thread.

## Next Priority: Four-Subset Safety-Loss Ablation

The next core experiment is the systematic GRU safety-loss ablation across
FD001-FD004. This tests whether the observed safety trade-off is stable across
subsets and loss types.

```powershell
.\.venv\Scripts\python.exe scripts\run_deep_ablation_matrix.py --subsets FD001 FD002 FD003 FD004 --seeds 42 43 44 --models gru --jobs baseline_lr1e-3_h64_l1_w30 critical_w2_h64_l1_w30 critical_w3_h64_l1_w30 asymmetric_w2_h64_l1_w30 asymmetric_w3_h64_l1_w30 safety_w1p5_h64_l1_w30 safety_w2_h64_l1_w30 safety_w3_h64_l1_w30 --epochs 60 --patience 8 --skip-existing
```

After it finishes:

```powershell
.\.venv\Scripts\python.exe -m rul_prediction.aggregate --root reports\tables\deep_ablations --out-dir reports\tables\deep_ablations\summary
.\.venv\Scripts\python.exe -m rul_prediction.error_analysis --root reports\tables\deep_ablations --out-dir reports\tables\deep_ablations\summary
```

## Decision Rules for the Ablation

- Do not choose models by RMSE alone.
- Report RMSE/MAE together with NASA S-score, Critical RMSE30/50,
  overestimation ratio, and overestimation magnitude.
- Treat safety losses as trade-off mechanisms: they may reduce dangerous
  overestimation and late-life error while worsening aggregate RMSE.
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
the four-subset ablation is complete.

## Scope Boundaries

- C-MAPSS is simulated benchmark data, not real fleet telemetry.
- Safety-GRU means benchmark loss weighting, not aviation safety certification.
- Decision simulation is hypothetical cost evaluation, not deployable airline
  maintenance scheduling.
- Transformer, TCN, and GNN papers remain related-work context unless
  implemented and evaluated in this repository.
