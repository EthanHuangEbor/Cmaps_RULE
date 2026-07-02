# MLP Full Matrix Completion Note

Date: 2026-07-02

## Run

Command:

```powershell
.\.venv\Scripts\python.exe scripts\run_research_matrix.py --out-root reports\tables\mlp_full_matrix --subsets FD001 FD002 FD003 FD004 --seeds 42 43 44 --deep-models mlp --deep-epochs 60 --patience 8 --skip-ml --skip-safety --device cuda
```

Local CUDA device: NVIDIA GeForce RTX 4060 Laptop GPU.

## Completeness

- `metrics.csv`: 12 files.
- `predictions.csv`: 12 files.
- `training_history.csv`: 12 files.
- `combined_metrics.csv`: 24 rows.
- Minimum seeds per subset/model/split: 3.

## Test Summary

| Subset | RMSE | MAE | NASA S-score | Critical RMSE50 | Overestimation ratio | Overestimation magnitude |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| FD001 | 15.35 | 11.40 | 448.86 | 5.16 | 0.537 | 6.09 |
| FD002 | 20.77 | 16.42 | 2439.83 | 16.50 | 0.498 | 7.46 |
| FD003 | 14.96 | 10.87 | 507.28 | 5.96 | 0.503 | 6.32 |
| FD004 | 23.85 | 18.76 | 7817.43 | 25.20 | 0.522 | 10.28 |

## Role In The Project

MLP should be treated as a formal fixed-window neural baseline. It uses the same engine-level split, train-only scaling, RUL cap, sliding-window construction, last-window test evaluation, and metric schema as the sequence models.

It is not currently a central Paper 1 claim: MLP is generally not RMSE-best. Its value is comparative, because it provides a non-recurrent neural reference point and shows competitive optimistic-risk behavior on selected subsets, including overestimation magnitude on FD001 and FD003.

## Tracked Summary Files

- `reports/mlp_full_matrix_summary_2026-07-02.csv`
- `reports/mlp_full_matrix_vs_existing_test_ranks_2026-07-02.csv`
