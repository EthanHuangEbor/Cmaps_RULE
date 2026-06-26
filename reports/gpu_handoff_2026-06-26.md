# GPU Handoff: Safety-Oriented C-MAPSS RUL Upgrade

Date: 2026-06-26

## Current State

The project has moved from the earlier FD001/FD003 benchmark draft toward the
new safety-oriented FD001-FD004 evaluation plan.

Completed before this handoff:

- Added traceable `job_name` metadata to deep-model outputs.
- Updated aggregation and error-analysis scripts so ablation rows remain
  distinguishable by `job_name`, learning rate, capacity, scheduler, loss, and
  safety weights.
- Extended `run_deep_ablation_matrix.py` with `critical_mse`,
  `asymmetric_mse`, and weight-3 safety jobs.
- Added `--deep-models` to `run_research_matrix.py` so FD002/FD004 can run a
  representative deep-model subset without forcing CNN/LSTM.
- Verified all four C-MAPSS subsets load and window correctly.
- Ran the FD002 representative 3-seed matrix for ML, GRU, and Safety-GRU.
- Stopped the CPU matrix before FD004 so the remaining computation can continue
  on a GPU laptop.

The local FD002 result CSVs are under:

```text
reports/tables/matrix/fd002
reports/tables/matrix/summary
```

`reports/tables/**` is intentionally ignored by Git. If you want the GPU laptop
to skip the completed FD002 jobs instead of rerunning them, copy the local
`reports/tables/matrix/fd002` directory to the new machine before running with
`--skip-existing`.

## FD002 Test Summary

The FD002 representative matrix used seeds 42/43/44, window size 30, max RUL
130, and GRU-only deep baselines.

| Job | Model | RMSE mean | RMSE std | MAE mean | NASA S-score | Critical RMSE30 | Critical RMSE50 | Overestimation ratio | Overestimation magnitude |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| ML | Ridge | 21.04 | 0.06 | 17.27 | 2354.96 | 16.91 | 18.19 | 0.520 | 9.02 |
| ML | Random Forest | 18.79 | 0.18 | 14.58 | 2451.56 | 12.07 | 15.38 | 0.492 | 7.23 |
| ML | Gradient Boosting | 19.89 | 0.20 | 15.95 | 2877.03 | 15.79 | 18.10 | 0.499 | 8.44 |
| deep_default_w30 | GRU | 17.81 | 0.47 | 13.15 | 1526.64 | 6.89 | 10.12 | 0.486 | 6.31 |
| safety_w2_h64_l1_w30 | Safety-GRU | 20.35 | 0.16 | 15.19 | 1806.99 | 5.05 | 8.12 | 0.308 | 3.41 |

Early interpretation:

- GRU is the best FD002 model by aggregate RMSE among the completed
  representative models.
- Safety-GRU worsens aggregate RMSE but improves late-life safety metrics,
  especially Critical RMSE30/50, overestimation ratio, and overestimation
  magnitude.
- This supports the planned paper framing: aggregate accuracy and safety risk
  can rank models differently.

## GPU Laptop Continuation

Start from the repository root:

```powershell
cd D:\Project\Cmaps_RULE
.\.venv\Scripts\Activate.ps1
python -m pip install -e .
```

Confirm the GPU is visible:

```powershell
python -c "import torch; print(torch.cuda.is_available()); print(torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'CPU only')"
```

First, finish the FD004 representative matrix:

```powershell
python scripts\run_research_matrix.py --subsets FD004 --seeds 42 43 44 --deep-models gru --deep-epochs 60 --patience 8 --skip-existing
```

If FD002 result CSVs were not copied from the old laptop, rerun both FD002 and
FD004 on GPU:

```powershell
python scripts\run_research_matrix.py --subsets FD002 FD004 --seeds 42 43 44 --deep-models gru --deep-epochs 60 --patience 8 --skip-existing
```

Then run the systematic safety-loss ablation. This is the next core experiment
for the paper:

```powershell
python scripts\run_deep_ablation_matrix.py --subsets FD001 FD002 FD003 FD004 --seeds 42 43 44 --models gru --jobs baseline_lr1e-3_h64_l1_w30 critical_w2_h64_l1_w30 critical_w3_h64_l1_w30 asymmetric_w2_h64_l1_w30 asymmetric_w3_h64_l1_w30 safety_w1p5_h64_l1_w30 safety_w2_h64_l1_w30 safety_w3_h64_l1_w30 --epochs 60 --patience 8 --skip-existing
```

After those finish, regenerate summaries:

```powershell
python -m rul_prediction.aggregate --root reports\tables\matrix --out-dir reports\tables\matrix\summary
python -m rul_prediction.error_analysis --root reports\tables\matrix --out-dir reports\tables\matrix\summary
python -m rul_prediction.aggregate --root reports\tables\deep_ablations --out-dir reports\tables\deep_ablations\summary
python -m rul_prediction.error_analysis --root reports\tables\deep_ablations --out-dir reports\tables\deep_ablations\summary
```

## Next Experiments After FD004

1. Uncertainty and decision evaluation on FD001 and FD004 only:

```powershell
python scripts\run_uncertainty.py --subset FD001 --method mc_dropout --model gru --loss mse --epochs 80 --patience 10 --mc-samples 50 --out-dir reports\tables\uncertainty\fd001\gru_mc
python scripts\run_uncertainty.py --subset FD004 --method deep_ensemble --model gru --loss safety_mse --ensemble-seeds 42 43 44 --epochs 80 --patience 10 --out-dir reports\tables\uncertainty\fd004\safety_gru_ens
python scripts\run_decision_simulation.py --predictions reports\tables\uncertainty\fd001\gru_mc\predictions.csv --out-dir reports\tables\decision\fd001_gru_mc
```

2. Domain shift and robustness stress tests:

```powershell
python scripts\run_domain_shift.py --source-subset FD001 --target-subset FD003 --model gradient_boosting --out-dir reports\tables\domain_shift\fd001_to_fd003_gb
python scripts\run_domain_shift.py --source-subset FD002 --target-subset FD004 --model gru --epochs 60 --patience 8 --out-dir reports\tables\domain_shift\fd002_to_fd004_gru
python scripts\run_sensor_robustness.py --subset FD004 --model gru --epochs 60 --patience 8 --out-dir reports\tables\robustness\fd004_gru
```

3. Only after the above are complete, regenerate paper figures and rewrite the
   manuscript around FD001-FD004 safety-oriented evidence.

## Scope Notes

- C-MAPSS is simulated benchmark data, not real fleet telemetry.
- Safety-GRU means benchmark loss weighting, not aviation safety certification.
- Decision simulation is hypothetical cost evaluation, not deployable airline
  maintenance scheduling.
- Transformer/TCN/GNN papers remain related-work context unless implemented and
  evaluated in this repository.
