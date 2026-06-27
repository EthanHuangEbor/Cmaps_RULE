# Notebooks

Notebook work is optional. The reproducible path for this project is the Python
package and scripts under `scripts/`, with generated outputs under ignored
`reports/tables/` directories.

Useful future notebooks:

1. `01_eda_fd001_fd004.ipynb`: sensor trends, RUL label distributions, and
   constant-feature screening across FD001-FD004.
2. `02_results_analysis.ipynb`: matrix summaries, per-engine errors,
   critical-zone results, and overestimation-risk comparisons.
3. `03_ablation_review.ipynb`: safety-loss ablation trade-offs after
   `reports/tables/deep_ablations/summary` is generated.

Keep notebook outputs lightweight before committing. Export key figures through
package scripts so results remain reproducible.
