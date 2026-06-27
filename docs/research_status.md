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
- FD002: GRU is strongest by aggregate RMSE, while Safety-GRU improves
  critical-zone error and overestimation metrics.
- FD004: Random Forest is strongest by aggregate RMSE, while Safety-GRU improves
  late-life and overestimation-risk metrics.

The detailed current roadmap and FD002/FD004 table are in
`reports/progress_roadmap_2026-06-27.md`.

## Next Required Experiment

Run the systematic GRU safety-loss ablation across all four subsets:

```powershell
.\.venv\Scripts\python.exe scripts\run_deep_ablation_matrix.py --subsets FD001 FD002 FD003 FD004 --seeds 42 43 44 --models gru --jobs baseline_lr1e-3_h64_l1_w30 critical_w2_h64_l1_w30 critical_w3_h64_l1_w30 asymmetric_w2_h64_l1_w30 asymmetric_w3_h64_l1_w30 safety_w1p5_h64_l1_w30 safety_w2_h64_l1_w30 safety_w3_h64_l1_w30 --epochs 60 --patience 8 --skip-existing
```

Then regenerate deep-ablation summaries:

```powershell
.\.venv\Scripts\python.exe -m rul_prediction.aggregate --root reports\tables\deep_ablations --out-dir reports\tables\deep_ablations\summary
.\.venv\Scripts\python.exe -m rul_prediction.error_analysis --root reports\tables\deep_ablations --out-dir reports\tables\deep_ablations\summary
```

## Deferred Work

Uncertainty, decision simulation, domain shift, sensor robustness, and XAI are
implemented as scaffolds, but should stay secondary until the four-subset
safety-loss ablation is complete.

## Scope Boundaries

- C-MAPSS is simulated benchmark data, not real fleet telemetry.
- Safety-GRU means benchmark loss weighting, not aviation safety certification.
- The project should report strong classical baselines and negative results
  honestly, and should not claim SOTA without broader independent validation.
