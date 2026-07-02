# Notebooks

Notebook work is optional. The reproducible path for this project is the Python
package and scripts under `scripts/`, with generated outputs under ignored
`reports/tables/` directories.

Useful future notebooks:

1. `01_eda_fd001_fd004.ipynb`: sensor trends, RUL label distributions, and
   constant-feature screening across FD001-FD004.
2. `02_results_analysis.ipynb`: matrix summaries, per-engine errors,
   critical-zone results, and overestimation-risk comparisons. Include
   `reports/mlp_full_matrix_summary_2026-07-02.csv` and
   `reports/mlp_full_matrix_vs_existing_test_ranks_2026-07-02.csv` when
   demonstrating formal neural baselines.
3. `03_ablation_review.ipynb`: safety-loss ablation trade-offs after
   `reports/tables/deep_ablations/summary` is generated.
4. `04_baseline_extensions.ipynb`: TCN/MLP extension review, showing why these
   models strengthen benchmark coverage without automatically becoming the
   manuscript headline claim.

Keep notebook outputs lightweight before committing. Export key figures through
package scripts so results remain reproducible. Do not commit full ignored
`reports/tables/**` outputs from notebooks; commit only compact CSV/figure
artifacts that are intentionally paper-facing or README-facing.
