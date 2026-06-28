# Paper 2 Figure Manifest

Core conclusion: cycle-consistent Dual-LSTM and safety weighting reshape RUL risk profiles, but do not prove full-portfolio SOTA superiority.
Figure archetype: schematic-led composite plus quantitative grids.
Backend: Python/matplotlib only.
Exports: SVG and PDF for editable manuscript use; PNG and TIFF for preview/submission checks.
Source data: reports/paper2 CSV outputs and reports/tables/dual_lstm/summary/per_engine_errors.csv.

## Figures

1. figure_01_dual_lstm_architecture: method schematic and inference boundary.
2. figure_02_dual_lstm_metric_rank_heatmap: metric ranks within each subset.
3. figure_03_rmse_vs_critical_rmse50: RMSE versus late-life error trade-off.
4. figure_04_rmse_vs_overestimation_magnitude: RMSE versus optimistic-risk trade-off.
5. figure_05_paper1_paper2_bridge: Paper 1/Paper 2 metric bridge.

## Reviewer Risks

- LSTM baseline and Dual-LSTM jobs do not use identical training support because paired windows are required by Dual-LSTM.
- Pairwise bootstrap resamples seed-engine rows; it is a benchmark robustness check.
- Paper 2 should not claim it replaces the full Paper 1 classical/deep portfolio.
