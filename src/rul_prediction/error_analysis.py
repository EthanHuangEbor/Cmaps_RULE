from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


def infer_job_name(path: Path) -> str:
    parent = path.parent.name
    if parent in {"ml", "deep", "deep_safety_gru"}:
        return parent
    if path.parent.parent.name.startswith("seed_"):
        return parent
    return ""


def read_predictions(paths: list[Path]) -> pd.DataFrame:
    frames: list[pd.DataFrame] = []
    for path in paths:
        df = pd.read_csv(path)
        df["source_file"] = str(path)
        inferred_job = infer_job_name(path)
        if "job_name" not in df.columns:
            df["job_name"] = inferred_job
        else:
            df["job_name"] = df["job_name"].fillna("").replace("", inferred_job)
        frames.append(df)
    if not frames:
        raise FileNotFoundError("No predictions.csv files found.")
    return pd.concat(frames, ignore_index=True)


def main() -> None:
    parser = argparse.ArgumentParser(description="Summarize hardest engines and critical-zone errors.")
    parser.add_argument("--root", default="reports/tables")
    parser.add_argument("--out-dir", default="reports/tables/summary")
    parser.add_argument("--critical-threshold", type=float, default=50.0)
    args = parser.parse_args()

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    predictions = read_predictions(sorted(Path(args.root).glob("**/predictions.csv")))
    predictions["abs_error"] = predictions["error"].abs()
    group_cols = [
        col
        for col in [
            "job_name",
            "subset",
            "model",
            "seed",
            "window_size",
            "max_rul",
            "hidden_size",
            "num_layers",
            "dropout",
            "learning_rate",
            "scheduler",
            "loss",
            "critical_threshold",
            "critical_weight",
            "over_weight",
        ]
        if col in predictions.columns
    ]
    per_engine = (
        predictions.groupby([*group_cols, "unit"], as_index=False, dropna=False)
        .agg(
            mean_abs_error=("abs_error", "mean"),
            mean_error=("error", "mean"),
            true_rul=("y_true", "mean"),
            pred_rul=("y_pred", "mean"),
        )
        .sort_values([*group_cols, "mean_abs_error"], ascending=[*[True] * len(group_cols), False])
    )
    critical = predictions[predictions["y_true"] <= args.critical_threshold].copy()
    critical_summary = (
        critical.groupby(group_cols, as_index=False, dropna=False)
        .agg(
            critical_count=("error", "size"),
            critical_mae=("abs_error", "mean"),
            critical_mean_error=("error", "mean"),
            critical_over_ratio=("error", lambda values: float((values > 0).mean())),
        )
        .sort_values([*group_cols, "critical_mae"], ascending=[*[True] * len(group_cols), True])
    )
    per_engine.to_csv(out_dir / "per_engine_errors.csv", index=False)
    critical_summary.to_csv(out_dir / "critical_error_summary.csv", index=False)
    print(f"Wrote {out_dir / 'per_engine_errors.csv'}")
    print(f"Wrote {out_dir / 'critical_error_summary.csv'}")


if __name__ == "__main__":
    main()
