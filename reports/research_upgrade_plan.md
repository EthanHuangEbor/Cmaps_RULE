# C-MAPSS RUL Research Upgrade Plan

## Current Research Claim

The project is no longer framed as "using LSTM for RUL prediction." The working
claim is:

> Classical tree models may remain stronger on aggregate C-MAPSS FD001 error,
> while recurrent deep models may become more valuable under safety-oriented
> metrics such as critical-zone error and overestimation risk.

## Phase 1: Reproducibility

Run FD001 with seeds `42`, `43`, and `44`. Report mean and standard deviation
for RMSE, MAE, NASA S-score, critical-zone RMSE, and overestimation ratio.

Command:

```powershell
python scripts\run_research_matrix.py --subsets FD001 --seeds 42 43 44 --skip-safety --deep-epochs 60 --skip-existing
```

Question to answer:

- Does Random Forest / Gradient Boosting remain strongest on aggregate RMSE?
- Does GRU retain the critical-zone advantage?
- Is CNN consistently weak, or was the first run accidental?

## Phase 2: FD003 Extension

Run FD003 after FD001 is stable.

Command:

```powershell
python scripts\run_research_matrix.py --subsets FD003 --seeds 42 43 44 --skip-safety --deep-epochs 60 --skip-existing
```

Question to answer:

- Does the model ranking change under a more complex fault setting?
- Do recurrent models become more competitive than tree baselines?

## Phase 3: Ablation

Run controlled changes:

- window size: `20`, `30`, `50`
- RUL cap: `100`, `130`
- model family: tree baseline vs recurrent vs CNN

Use the existing `scripts/run_ablation.py` for first-pass ablations. It runs
traditional baselines plus LSTM/GRU/CNN by default, then writes aggregate tables.

Command:

```powershell
python scripts\run_ablation.py --deep-epochs 40 --skip-existing
```

## Phase 4: Safety-Aware Improvement

Use GRU as the first target model. Compare:

- `loss=mse`
- `loss=critical_mse`
- `loss=asymmetric_mse`
- `loss=safety_mse`

Command:

```powershell
python -m rul_prediction.train_deep --data-dir data\raw --subset FD001 --out-dir reports\tables\safety_fd001_gru --models gru --loss safety_mse --epochs 60 --patience 8
```

Success criterion:

- Lower NASA S-score, critical-zone RMSE, or overestimation ratio without a
  catastrophic loss in aggregate RMSE.

## Phase 5: Paper Package

Minimum publishable-student-project evidence:

- FD001 and FD003.
- Three seeds.
- At least five models.
- Safety-aware GRU variant.
- Two ablations.
- Four to six figures.
- Reproducible code and commands.
