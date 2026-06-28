from __future__ import annotations

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
PAPER = ROOT / "reports" / "paper"
FIGURES = PAPER / "figures"


def add_trace(rows: list[dict[str, object]], location: str, statement: str, value: object, source: str, selector: str, column: str, source_value: object) -> None:
    rows.append(
        {
            "manuscript_location": location,
            "statement": statement,
            "reported_value": value,
            "source_file": source,
            "selector": selector,
            "source_column": column,
            "source_value": source_value,
            "status": "matched",
        }
    )


def fmt(value: float, digits: int = 2) -> str:
    return f"{value:.{digits}f}"


def trace_matrix_summary(rows: list[dict[str, object]]) -> None:
    df = pd.read_csv(PAPER / "matrix_safety_benchmark_summary.csv")
    role_rows = [
        ("Table matrix-summary", "FD001", "Gradient Boosting", "RMSE/SARBI best"),
        ("Table matrix-summary", "FD001", "Safety-GRU", "critical/over best"),
        ("Table matrix-summary", "FD002", "GRU", "RMSE best"),
        ("Table matrix-summary", "FD002", "Safety-GRU", "SARBI/risk best"),
        ("Table matrix-summary", "FD003", "Gradient Boosting", "RMSE best"),
        ("Table matrix-summary", "FD003", "Random Forest", "SARBI/critical best"),
        ("Table matrix-summary", "FD003", "Safety-GRU", "overestimation best"),
        ("Table matrix-summary", "FD004", "Random Forest", "RMSE best"),
        ("Table matrix-summary", "FD004", "Safety-GRU", "SARBI/risk best"),
    ]
    columns = [
        ("RMSE", "rmse_mean", 2),
        ("MAE", "mae_mean", 2),
        ("RMSE50", "critical_rmse_50_mean", 2),
        ("OverMag", "overestimation_magnitude_mean", 2),
        ("SARBI", "sarbi_mean", 3),
    ]
    for location, subset, label, role in role_rows:
        match = df[df["subset"].eq(subset) & df["label"].eq(label)]
        if match.empty:
            raise ValueError(f"Missing matrix row {subset} {label}")
        row = match.iloc[0]
        for display, column, digits in columns:
            add_trace(
                rows,
                location,
                f"{subset} {label} ({role}) {display}",
                fmt(float(row[column]), digits),
                "reports/paper/matrix_safety_benchmark_summary.csv",
                f"subset={subset}; label={label}",
                column,
                row[column],
            )


def trace_winner_tables(rows: list[dict[str, object]]) -> None:
    matrix = pd.read_csv(PAPER / "matrix_rmse_vs_risk_best.csv")
    ablation = pd.read_csv(PAPER / "deep_ablation_rmse_vs_risk_best.csv")
    for source_df, source_file, location in [
        (matrix, "reports/paper/matrix_rmse_vs_risk_best.csv", "Table winner-split"),
        (ablation, "reports/paper/deep_ablation_rmse_vs_risk_best.csv", "Table ablation-summary"),
    ]:
        for subset in ["FD001", "FD002", "FD003", "FD004"]:
            for metric in ["rmse", "critical_rmse_50", "overestimation_magnitude", "sarbi"]:
                row = source_df[source_df["subset"].eq(subset) & source_df["metric"].eq(metric)].iloc[0]
                add_trace(
                    rows,
                    location,
                    f"{subset} {metric} winner",
                    row["metric_best"],
                    source_file,
                    f"subset={subset}; metric={metric}",
                    "metric_best",
                    row["metric_best"],
                )
                add_trace(
                    rows,
                    location,
                    f"{subset} {metric} RMSE cost (%)",
                    fmt(float(row["rmse_change_pct"]), 1),
                    source_file,
                    f"subset={subset}; metric={metric}",
                    "rmse_change_pct",
                    row["rmse_change_pct"],
                )


def trace_bootstrap(rows: list[dict[str, object]]) -> None:
    df = pd.read_csv(PAPER / "matrix_bootstrap_rmse_vs_sarbi.csv")
    for subset in ["FD002", "FD004"]:
        for metric in ["rmse", "critical_rmse_50", "overestimation_ratio", "overestimation_magnitude"]:
            match = df[df["subset"].eq(subset) & df["metric"].eq(metric)]
            if match.empty:
                continue
            row = match.iloc[0]
            for column in ["sarbi_minus_rmse_best", "ci95_low", "ci95_high", "n_paired_seed_engine"]:
                digits = 3 if metric == "overestimation_ratio" else 2
                if column == "n_paired_seed_engine":
                    value = int(row[column])
                else:
                    value = fmt(float(row[column]), digits)
                add_trace(
                    rows,
                    "Bootstrap paragraph",
                    f"{subset} {metric} {column}",
                    value,
                    "reports/paper/matrix_bootstrap_rmse_vs_sarbi.csv",
                    f"subset={subset}; metric={metric}",
                    column,
                    row[column],
                )


def trace_counts(rows: list[dict[str, object]]) -> None:
    matrix_seed = pd.read_csv(PAPER / "matrix_safety_benchmark_seed_scores.csv")
    ablation_seed = pd.read_csv(PAPER / "deep_ablation_sarbi_seed_scores.csv")
    add_trace(rows, "Methods counts", "representative subsets", matrix_seed["subset"].nunique(), "reports/paper/matrix_safety_benchmark_seed_scores.csv", "all rows", "subset.nunique", matrix_seed["subset"].nunique())
    add_trace(rows, "Methods counts", "representative models per subset", matrix_seed.groupby("subset")["model"].nunique().min(), "reports/paper/matrix_safety_benchmark_seed_scores.csv", "groupby subset", "model.nunique.min", matrix_seed.groupby("subset")["model"].nunique().min())
    add_trace(rows, "Methods counts", "representative seeds per subset/model", matrix_seed.groupby(["subset", "model"])["seed"].nunique().min(), "reports/paper/matrix_safety_benchmark_seed_scores.csv", "groupby subset/model", "seed.nunique.min", matrix_seed.groupby(["subset", "model"])["seed"].nunique().min())
    add_trace(rows, "Methods counts", "deep ablation jobs", ablation_seed[["subset", "seed", "job_name"]].drop_duplicates().shape[0], "reports/paper/deep_ablation_sarbi_seed_scores.csv", "drop duplicates subset/seed/job", "row_count", ablation_seed[["subset", "seed", "job_name"]].drop_duplicates().shape[0])
    add_trace(rows, "Methods counts", "deep ablation subsets", ablation_seed["subset"].nunique(), "reports/paper/deep_ablation_sarbi_seed_scores.csv", "all rows", "subset.nunique", ablation_seed["subset"].nunique())


def write_manifest() -> None:
    figures = [
        ("Figure 9", "figure_09_metric_rank_heatmap.pdf", "matrix_safety_benchmark_summary.csv"),
        ("Figure 10", "figure_10_rmse_vs_critical_rmse50.pdf", "matrix_safety_benchmark_summary.csv"),
        ("Figure 11", "figure_11_rmse_vs_overestimation_magnitude.pdf", "matrix_safety_benchmark_summary.csv"),
        ("Figure 12", "figure_12_ablation_rmse_vs_overestimation.pdf", "deep_ablation_sarbi_summary.csv"),
        ("Figure 13", "figure_13_sarbi_weight_sensitivity.pdf", "matrix_sarbi_weight_sensitivity.csv"),
    ]
    tables = [
        ("Table matrix-summary", "matrix_safety_benchmark_summary.csv"),
        ("Table winner-split", "matrix_rmse_vs_risk_best.csv"),
        ("Table ablation-summary", "deep_ablation_rmse_vs_risk_best.csv"),
        ("Bootstrap paragraph", "matrix_bootstrap_rmse_vs_sarbi.csv"),
    ]
    lines = [
        "# Paper Figure and Table Manifest",
        "",
        "Date: 2026-06-28",
        "",
        "This manifest maps the FD001-FD004 safety-oriented manuscript artifacts to their source data files.",
        "",
        "## Figures",
    ]
    for label, file_name, source in figures:
        exists = (FIGURES / file_name).exists()
        lines.append(f"- {label}: `reports/paper/figures/{file_name}`; source `reports/paper/{source}`; exists={exists}.")
    lines.extend(["", "## Tables and Numeric Claims"])
    for label, source in tables:
        lines.append(f"- {label}: source `reports/paper/{source}`; traced in `reports/paper/paper_value_trace.csv`.")
    lines.extend(
        [
            "",
            "## Scope Boundary",
            "- SARBI is a transparent reporting index, not a physical RUL model or aviation certification formula.",
            "- Safety-GRU and Dual-LSTM prototype work are not part of the Paper 1 contribution unless explicitly added in a later manuscript revision.",
        ]
    )
    (PAPER / "figure_table_manifest.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    rows: list[dict[str, object]] = []
    trace_matrix_summary(rows)
    trace_winner_tables(rows)
    trace_bootstrap(rows)
    trace_counts(rows)
    pd.DataFrame(rows).to_csv(PAPER / "paper_value_trace.csv", index=False)
    write_manifest()
    print(f"Wrote {PAPER / 'paper_value_trace.csv'}")
    print(f"Wrote {PAPER / 'figure_table_manifest.md'}")


if __name__ == "__main__":
    main()
