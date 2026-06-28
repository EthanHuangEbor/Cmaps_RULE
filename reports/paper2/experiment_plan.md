# Paper 2 Experiment Plan

Primary command:

```powershell
.\.venv\Scripts\python.exe scripts\run_dual_lstm_matrix.py --subsets FD001 FD002 FD003 FD004 --seeds 42 43 44 --jobs lstm_baseline_h64_l1_w30 dual_no_cycle_h64_l1_w30 dual_cycle_h64_l1_w30 dual_cycle_safety_w2_h64_l1_w30 --epochs 30 --patience 5 --skip-existing
```

Paper-facing output command:

```powershell
.\.venv\Scripts\python.exe scripts\make_dual_lstm_paper2_outputs.py --root reports\tables\dual_lstm --out-dir reports\paper2
```

Acceptance gates:

- 48 jobs with metrics, predictions, training history, and selected feature files.
- `combined_metrics.csv` has 96 rows.
- Every subset/job/split has exactly seeds 42, 43, and 44 with no duplicate rows.
- `dual_cycle_h64_l1_w30` is the RMSE-oriented representation control.
- `dual_cycle_safety_w2_h64_l1_w30` reduces critical RMSE50 or overestimation magnitude on at least 3 of 4 subsets before making a positive risk-shift claim.
