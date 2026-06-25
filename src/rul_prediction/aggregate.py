from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


METRICS = [
    "rmse",
    "mae",
    "nasa_s_score",
    "critical_rmse_30",
    "critical_rmse_50",
    "overestimation_ratio",
    "overestimation_magnitude",
]


def read_metrics(paths: list[Path]) -> pd.DataFrame:
    frames: list[pd.DataFrame] = []
    for path in paths:
        df = pd.read_csv(path)
        df["source_file"] = str(path)
        frames.append(df)
    if not frames:
        raise FileNotFoundError("No metrics.csv files found.")
    return pd.concat(frames, ignore_index=True)


def aggregate_metrics(metrics: pd.DataFrame) -> pd.DataFrame:
    group_cols = [
        col
        for col in [
            "subset",
            "split",
            "model",
            "window_size",
            "max_rul",
            "hidden_size",
            "num_layers",
            "dropout",
            "learning_rate",
            "scheduler",
            "loss",
            "critical_weight",
            "over_weight",
        ]
        if col in metrics.columns
    ]
    present_metrics = [metric for metric in METRICS if metric in metrics.columns]
    summary = (
        metrics.groupby(group_cols, dropna=False)[present_metrics]
        .agg(["mean", "std", "min", "max", "count"])
        .reset_index()
    )
    summary.columns = [
        "_".join(str(part) for part in column if part != "") if isinstance(column, tuple) else str(column)
        for column in summary.columns
    ]
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description="Aggregate C-MAPSS experiment metrics.")
    parser.add_argument("--root", default="reports/tables")
    parser.add_argument("--out-dir", default="reports/tables/summary")
    args = parser.parse_args()

    root = Path(args.root)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    metrics = read_metrics(sorted(root.glob("**/metrics.csv")))
    metrics.to_csv(out_dir / "combined_metrics.csv", index=False)
    aggregate_metrics(metrics).to_csv(out_dir / "summary_metrics.csv", index=False)
    print(f"Wrote {out_dir / 'combined_metrics.csv'}")
    print(f"Wrote {out_dir / 'summary_metrics.csv'}")


if __name__ == "__main__":
    main()
