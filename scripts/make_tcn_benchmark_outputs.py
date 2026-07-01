from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


METRICS = [
    "rmse_mean",
    "mae_mean",
    "nasa_s_score_mean",
    "critical_rmse_50_mean",
    "overestimation_ratio_mean",
    "overestimation_magnitude_mean",
]


def read_summary(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Missing summary file: {path}")
    return pd.read_csv(path)


def make_tcn_summary(tcn_summary: pd.DataFrame) -> pd.DataFrame:
    rows = tcn_summary[(tcn_summary["split"] == "test") & (tcn_summary["model"] == "tcn")].copy()
    keep = ["subset", "model", "split", *METRICS]
    return rows[keep].sort_values(["subset", "model"]).reset_index(drop=True)


def compare_to_representative_best(tcn_test: pd.DataFrame, matrix_summary: pd.DataFrame) -> pd.DataFrame:
    matrix_test = matrix_summary[matrix_summary["split"] == "test"].copy()
    rows: list[dict[str, object]] = []
    for _, tcn_row in tcn_test.iterrows():
        subset = str(tcn_row["subset"])
        subset_matrix = matrix_test[matrix_test["subset"] == subset]
        for metric in METRICS:
            tcn_value = pd.to_numeric(pd.Series([tcn_row[metric]]), errors="coerce").iloc[0]
            metric_values = pd.to_numeric(subset_matrix[metric], errors="coerce")
            valid = subset_matrix.loc[metric_values.notna()].copy()
            if valid.empty or pd.isna(tcn_value):
                rows.append(
                    {
                        "subset": subset,
                        "metric": metric.replace("_mean", ""),
                        "tcn_value": tcn_value,
                        "representative_best_model": "",
                        "representative_best_value": float("nan"),
                        "delta_vs_best": float("nan"),
                        "pct_delta_vs_best": float("nan"),
                    }
                )
                continue
            valid[metric] = pd.to_numeric(valid[metric], errors="coerce")
            best = valid.sort_values(metric, ascending=True).iloc[0]
            best_value = float(best[metric])
            delta = float(tcn_value - best_value)
            pct_delta = float(delta / best_value * 100.0) if best_value != 0 else float("nan")
            rows.append(
                {
                    "subset": subset,
                    "metric": metric.replace("_mean", ""),
                    "tcn_value": float(tcn_value),
                    "representative_best_model": best["model"],
                    "representative_best_value": best_value,
                    "delta_vs_best": delta,
                    "pct_delta_vs_best": pct_delta,
                }
            )
    return pd.DataFrame(rows)


def write_note(tcn_test: pd.DataFrame, comparison: pd.DataFrame, out_path: Path) -> None:
    rmse = comparison[comparison["metric"] == "rmse"].copy()
    critical = comparison[comparison["metric"] == "critical_rmse_50"].copy()
    overmag = comparison[comparison["metric"] == "overestimation_magnitude"].copy()
    lines = [
        "# TCN Matrix Extension Note",
        "",
        "Scope: baseline TCN only, FD001-FD004, seeds 42/43/44, window size 30, max RUL 130, hidden size 64, 4 temporal blocks, epochs 60, patience 8.",
        "",
        "This extension should be read as a stronger sequence baseline for the Paper 1/Paper 2 safety-oriented benchmark, not as a new SOTA claim.",
        "",
        "## Test Summary",
        "",
        "```text",
        tcn_test.to_string(index=False),
        "```",
        "",
        "## Comparison To Representative Matrix Best",
        "",
        "Lower is better for every listed metric. Positive deltas mean TCN is worse than the best representative-matrix model for that metric.",
        "",
        "```text",
        comparison.to_string(index=False),
        "```",
        "",
        "## Initial Reading",
        "",
        f"- RMSE: TCN matches or improves the representative-matrix best on {(rmse['delta_vs_best'] <= 0).sum()}/{len(rmse)} subsets.",
        f"- Critical RMSE50: TCN matches or improves the representative-matrix best on {(critical['delta_vs_best'] <= 0).sum()}/{len(critical)} subsets.",
        f"- Overestimation magnitude: comparable values are available on {(~overmag['representative_best_value'].isna()).sum()}/{len(overmag)} subsets.",
        "- Do not promote TCN into the main claim until a decision proxy and sensitivity checks are regenerated.",
        "- Safety-loss TCN has not been run in this extension; risk-shaping claims should still refer to Safety-GRU and Dual-LSTM safety-w2 unless new TCN safety jobs are added.",
        "",
    ]
    out_path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate paper-facing TCN benchmark summary outputs.")
    parser.add_argument("--tcn-root", default="reports/tables/matrix_tcn")
    parser.add_argument("--matrix-root", default="reports/tables/matrix")
    parser.add_argument("--out-dir", default="reports/paper")
    args = parser.parse_args()

    tcn_root = Path(args.tcn_root)
    matrix_root = Path(args.matrix_root)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    tcn_summary = read_summary(tcn_root / "summary" / "summary_metrics.csv")
    matrix_summary = read_summary(matrix_root / "summary" / "summary_metrics.csv")
    tcn_test = make_tcn_summary(tcn_summary)
    comparison = compare_to_representative_best(tcn_test, matrix_summary)

    tcn_test.to_csv(out_dir / "tcn_matrix_summary.csv", index=False)
    comparison.to_csv(out_dir / "tcn_vs_representative_best.csv", index=False)
    write_note(tcn_test, comparison, out_dir / "tcn_matrix_extension_note.md")
    print(f"Wrote {out_dir / 'tcn_matrix_summary.csv'}")
    print(f"Wrote {out_dir / 'tcn_vs_representative_best.csv'}")
    print(f"Wrote {out_dir / 'tcn_matrix_extension_note.md'}")


if __name__ == "__main__":
    main()
