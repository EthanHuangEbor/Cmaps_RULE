# MLP Baseline Integration Note

Date: 2026-07-02

## Purpose

This note records the first integration of a multilayer perceptron (MLP) baseline into the C-MAPSS RUL research pipeline. The goal is not to claim a new architecture or update the Paper 1 representative matrix. The MLP is introduced as a lightweight non-recurrent neural baseline for fixed-window RUL regression.

## Literature Positioning

- NASA C-MAPSS remains the simulated turbofan benchmark source for FD001-FD004 RUL experiments.
- Prior RUL studies have used MLP-style feed-forward neural networks on windowed or engineered features. Laredo et al. frame a low-complexity MLP plus evolutionary data-parameter optimization around strided time windows for mechanical-system RUL.
- Babu et al. explicitly note that MLP has been applied to RUL prediction, but argue that CNNs better learn salient temporal features from raw multichannel sensor windows.
- Therefore, this project treats MLP as a runnable baseline category, not a new SOTA method and not a replacement for GRU/Safety-GRU/Dual-LSTM evidence.

Source pointers:

- NASA PCoE data set repository: https://www.nasa.gov/intelligent-systems-division/discovery-and-systems-health/pcoe/pcoe-data-set-repository/
- Laredo et al., MLP/evolutionary RUL framework: https://arxiv.org/abs/1905.05918
- Babu et al., deep CNN RUL benchmark discussion: https://doi.org/10.1007/978-3-319-32025-0_14

## Data Handling

The MLP reuses the exact deep-model protocol already used by LSTM/GRU/CNN/TCN:

1. Engine-level validation split.
2. Train-only standard scaling.
3. Capped RUL labels with `max_rul=130`.
4. Fixed sliding windows with `window_size=30`.
5. Last-window test evaluation.
6. Shared metrics and output schema: `metrics.csv`, `predictions.csv`, `training_history.csv`, and `selected_features.csv`.

The only model-specific difference is representation: MLP flattens each `(window, features)` tensor into one vector before dense layers.

## Implementation Scope

Implemented:

- `RULSequenceModel("mlp", ...)` in `src/rul_prediction/models_deep.py`.
- `num_layers` now controls the number of MLP hidden dense blocks.
- `train_deep.py`, `run_research_matrix.py`, and `run_deep_ablation_matrix.py` accept `mlp` as a model choice.
- Matrix runners accept `--device`, so CUDA can be selected explicitly.
- Unit and CLI schema tests cover MLP forward, training, missing `window_size`, and output files.

Not changed:

- Paper 1 five-model representative matrix remains Ridge, Random Forest, Gradient Boosting, GRU, and Safety-GRU.
- `scripts/make_safety_benchmark_outputs.py` intentionally keeps `CORE_MATRIX_MODELS` unchanged.
- Full FD001-FD004 multi-seed MLP matrix is now completed as a formal neural baseline comparison, but not yet folded into Paper 1 manuscript claims.

## CUDA Check

Local environment check:

```text
torch 2.12.1+cu126
cuda_available True
cuda_version 12.6
device_count 1
device NVIDIA GeForce RTX 4060 Laptop GPU
```

## Smoke Matrix

Command:

```powershell
.\.venv\Scripts\python.exe scripts\run_research_matrix.py --out-root reports\tables\mlp_baseline --subsets FD001 FD004 --seeds 42 --deep-models mlp --deep-epochs 20 --patience 4 --skip-ml --skip-safety --device cuda
```

Completeness:

- `metrics.csv`: 2 files, one for FD001 seed42 and one for FD004 seed42.
- `predictions.csv`: 2 files.
- `training_history.csv`: 2 files.
- Aggregated rows: 4 rows in `reports/tables/mlp_baseline/summary/summary_metrics.csv`.

Small paper-facing extract:

- `reports/mlp_baseline_cuda_summary_2026-07-02.csv`

## Initial Results

Test split only:

| Subset | RMSE | MAE | NASA S-score | Critical RMSE50 | Overestimation ratio | Overestimation magnitude |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| FD001 | 16.34 | 12.71 | 506.05 | 8.71 | 0.520 | 7.29 |
| FD004 | 26.25 | 20.68 | 16401.62 | 29.70 | 0.528 | 11.36 |

These are single-seed, short-training smoke results. They verify integration and schema compatibility, but they should not be used as final paper evidence.

## Full Matrix Follow-up

The FD001-FD004 x 3-seed CUDA matrix has now been completed under `reports/tables/mlp_full_matrix`. Compact tracked summaries are available at:

- `reports/mlp_full_matrix_summary_2026-07-02.csv`
- `reports/mlp_full_matrix_vs_existing_test_ranks_2026-07-02.csv`

Current interpretation: MLP is useful as a formal fixed-window neural baseline. It is not RMSE-best, but it provides a valuable contrast point because it performs competitively on selected optimistic-risk metrics, especially overestimation magnitude on FD001 and FD003.
