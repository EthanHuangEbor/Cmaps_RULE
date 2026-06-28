# Progress Roadmap: Safety-Oriented C-MAPSS RUL Evaluation Paper

Date: 2026-06-28

## Current Position

The first paper direction is fixed as a safety-oriented C-MAPSS RUL evaluation
benchmark. The paper asks whether aggregate RMSE selects the same model as
late-life error and optimistic overestimation-risk metrics on FD001-FD004.

The contribution is evaluation protocol plus risk-trade-off evidence. It is not
a Transformer/TCN/GNN architecture race, not a new SOTA claim, and not aviation
safety certification.

## What Was Completed Today

- Merged the completed FD001-FD004 safety-ablation record into the current paper
  branch.
- Added `scripts/make_safety_benchmark_outputs.py` to regenerate paper-facing
  SARBI tables, ranking-discordance tables, bootstrap checks, and figures.
- Generated representative matrix safety benchmark summaries under
  `reports/paper/`.
- Generated deep-ablation SARBI and RMSE-vs-risk summaries under
  `reports/paper/`.
- Generated four main trade-off/rank figures and one SARBI sensitivity figure.
- Rewrote `reports/paper/main.tex` around FD001-FD004 ranking reversals.
- Added 2023-2025 literature references for SAE-TCN, hierarchical Transformer,
  Koopman Transformer, Bayesian risk-aware RUL, and maintenance decision work.

## Paper-Facing Data Products

Representative matrix:

- `matrix_safety_benchmark_summary.csv`
- `matrix_safety_benchmark_seed_scores.csv`
- `matrix_rmse_vs_risk_best.csv`
- `matrix_rank_discordance.csv`
- `matrix_bootstrap_rmse_vs_sarbi.csv`
- `matrix_sarbi_weight_sensitivity.csv`

GRU safety-loss ablation:

- `deep_ablation_sarbi_summary.csv`
- `deep_ablation_sarbi_seed_scores.csv`
- `deep_ablation_rmse_vs_risk_best.csv`
- `deep_ablation_rank_discordance.csv`

Main figures:

- `figure_09_metric_rank_heatmap`
- `figure_10_rmse_vs_critical_rmse50`
- `figure_11_rmse_vs_overestimation_magnitude`
- `figure_12_ablation_rmse_vs_overestimation`
- `figure_13_sarbi_weight_sensitivity`

## Evidence Snapshot

Representative matrix:

- FD001: Gradient Boosting is RMSE/SARBI-best, but Safety-GRU is best for
  Critical RMSE30/50 and overestimation metrics.
- FD002: GRU is RMSE-best, while Safety-GRU is SARBI-best and risk-best.
- FD003: Gradient Boosting is RMSE-best, Random Forest is SARBI/critical-best,
  and Safety-GRU has the lowest overestimation magnitude.
- FD004: Random Forest is RMSE-best, while Safety-GRU is SARBI-best and wins
  critical/overestimation metrics.

Deep ablation:

- FD001: safety-w3 is SARBI-best and wins NASA, critical, and overestimation
  metrics with about 2.6% RMSE cost versus the RMSE-best job.
- FD002: critical/asymmetric/safety losses split the risk wins; best risk
  reductions can cost substantial RMSE.
- FD003: critical-w3 is RMSE/SARBI-best, but other risk metrics still choose
  different jobs.
- FD004: baseline GRU is RMSE-best, while safety-w2 or safety-w3 wins SARBI,
  NASA, critical, and overestimation metrics.

Bootstrap checks:

- FD002 SARBI-best Safety-GRU has higher RMSE than RMSE-best GRU, but lower
  critical RMSE50, overestimation ratio, and overestimation magnitude.
- FD004 SARBI-best Safety-GRU has higher RMSE than RMSE-best Random Forest, but
  lower overestimation ratio and magnitude. The critical RMSE50 interval is
  directionally favorable but crosses zero, so it should be stated cautiously.

## Manuscript Argument

One-sentence argument:

> In C-MAPSS RUL prediction, we show that aggregate RMSE is an incomplete model
> selection criterion by evaluating classical and GRU-based models across
> FD001-FD004 with late-life and overestimation-risk metrics, supported by
> multi-seed matrix results, a 96-job safety-loss ablation, SARBI ranking, and
> bootstrap checks, with claims bounded to simulated benchmark evidence.

Results are now organized by ranking reversal, not by model marketing:

1. Representative FD001-FD004 matrix.
2. RMSE-best versus risk-best winner split.
3. RMSE-vs-critical and RMSE-vs-overestimation trade-off plots.
4. Safety-loss ablation as risk movement.
5. Bootstrap and SARBI sensitivity checks.

## Next Steps

- Compile `reports/paper/main.tex` and fix any LaTeX/table layout issues.
- Run the Python script and lightweight tests before commit.
- Optionally add a supplementary table with all representative matrix metrics.
- After manuscript text stabilizes, polish figure captions and ensure every
  numeric claim traces to a CSV row.
- Keep UQ, decision simulation, domain shift, robustness, and XAI as future work
  rather than expanding the first paper.

## Decision Rules Going Forward

- Do not tune preprocessing or RUL cap to chase a higher headline score.
- Do not call Safety-GRU a new architecture.
- Do not claim SARBI is a physical RUL predictor; it is a transparent reporting
  index.
- Preserve negative and mixed results because they strengthen the benchmark
  paper's credibility.