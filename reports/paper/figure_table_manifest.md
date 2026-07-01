# Paper Figure and Table Manifest

Date: 2026-06-30

This manifest maps the FD001-FD004 safety-oriented manuscript artifacts to their source data files.

## Figures
- Figure 9: `reports/paper/figures/figure_09_metric_rank_heatmap.pdf`; source `reports/paper/matrix_safety_benchmark_summary.csv`; exists=True.
- Figure 10: `reports/paper/figures/figure_10_rmse_vs_critical_rmse50.pdf`; source `reports/paper/matrix_safety_benchmark_summary.csv`; exists=True.
- Figure 11: `reports/paper/figures/figure_11_rmse_vs_overestimation_magnitude.pdf`; source `reports/paper/matrix_safety_benchmark_summary.csv`; exists=True.
- Figure 12: `reports/paper/figures/figure_12_ablation_rmse_vs_overestimation.pdf`; source `reports/paper/deep_ablation_sarbi_summary.csv`; exists=True.
- Figure 13: `reports/paper/figures/figure_13_sarbi_weight_sensitivity.pdf`; source `reports/paper/matrix_sarbi_weight_sensitivity.csv`; exists=True.

## Tables and Numeric Claims
- Table matrix-summary: source `reports/paper/matrix_safety_benchmark_summary.csv`; traced in `reports/paper/paper_value_trace.csv`.
- Table winner-split: source `reports/paper/matrix_rmse_vs_risk_best.csv`; traced in `reports/paper/paper_value_trace.csv`.
- Table ablation-summary: source `reports/paper/deep_ablation_rmse_vs_risk_best.csv`; traced in `reports/paper/paper_value_trace.csv`.
- Bootstrap paragraph: source `reports/paper/matrix_bootstrap_rmse_vs_sarbi.csv`; traced in `reports/paper/paper_value_trace.csv`.
- Table tcn-claim-trace: source `reports/paper/tcn_claim_evidence_map.csv; tcn_safety_loss_gate.csv`; traced in `reports/paper/paper_value_trace.csv`.

## Scope Boundary
- SARBI is a transparent reporting index, not a physical RUL model or aviation certification formula.
- TCN is included as a baseline and stress test, not as a new state-of-the-art architecture claim.
- TCN safety-loss training is deferred unless manuscript scope or reviewer feedback requires architecture-transfer evidence.
- Dual-LSTM prototype work is not part of the Paper 1 contribution unless explicitly added in a later manuscript revision.
