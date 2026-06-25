from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

try:
    import seaborn as sns
except ModuleNotFoundError:  # pragma: no cover - exercised only in minimal environments
    sns = None


def _read_many(paths: list[str]) -> pd.DataFrame:
    frames = [pd.read_csv(path) for path in paths if Path(path).exists()]
    if not frames:
        raise FileNotFoundError("No input CSV files were found.")
    return pd.concat(frames, ignore_index=True)


def plot_metrics(metrics: pd.DataFrame, out_dir: Path) -> None:
    test_metrics = metrics[metrics["split"] == "test"].copy()
    for metric in ["rmse", "mae", "nasa_s_score", "critical_rmse_50"]:
        if metric not in test_metrics.columns:
            continue
        plt.figure(figsize=(9, 5))
        if sns is not None:
            sns.barplot(data=test_metrics, x="model", y=metric, hue="subset")
        else:
            pivot = test_metrics.pivot_table(index="model", columns="subset", values=metric, aggfunc="mean")
            pivot.plot(kind="bar", ax=plt.gca())
        plt.xticks(rotation=30, ha="right")
        plt.tight_layout()
        plt.savefig(out_dir / f"{metric}_bar.png", dpi=200)
        plt.close()


def plot_predictions(predictions: pd.DataFrame, out_dir: Path) -> None:
    plt.figure(figsize=(6, 6))
    if sns is not None:
        sns.scatterplot(data=predictions, x="y_true", y="y_pred", hue="model", alpha=0.75)
    else:
        for model, group in predictions.groupby("model"):
            plt.scatter(group["y_true"], group["y_pred"], alpha=0.75, label=model)
        plt.legend()
    upper = max(float(predictions["y_true"].max()), float(predictions["y_pred"].max()))
    plt.plot([0, upper], [0, upper], color="black", linestyle="--", linewidth=1)
    plt.xlabel("True RUL")
    plt.ylabel("Predicted RUL")
    plt.tight_layout()
    plt.savefig(out_dir / "prediction_scatter.png", dpi=200)
    plt.close()

    per_engine = (
        predictions.assign(abs_error=lambda df: df["error"].abs())
        .groupby(["model", "unit"], as_index=False)["abs_error"]
        .mean()
    )
    plt.figure(figsize=(10, 5))
    if sns is not None:
        sns.lineplot(data=per_engine, x="unit", y="abs_error", hue="model", marker="o")
    else:
        for model, group in per_engine.groupby("model"):
            plt.plot(group["unit"], group["abs_error"], marker="o", label=model)
        plt.legend()
    plt.xlabel("Engine unit")
    plt.ylabel("Mean absolute error")
    plt.tight_layout()
    plt.savefig(out_dir / "per_engine_abs_error.png", dpi=200)
    plt.close()

    critical = predictions[predictions["y_true"] <= 50].copy()
    if not critical.empty:
        plt.figure(figsize=(8, 5))
        if sns is not None:
            sns.boxplot(data=critical, x="model", y="error")
        else:
            grouped = [group["error"].to_numpy() for _, group in critical.groupby("model")]
            labels = [model for model, _ in critical.groupby("model")]
            try:
                plt.boxplot(grouped, tick_labels=labels)
            except TypeError:
                plt.boxplot(grouped, labels=labels)
        plt.axhline(0, color="black", linestyle="--", linewidth=1)
        plt.xticks(rotation=30, ha="right")
        plt.ylabel("Prediction error in RUL <= 50")
        plt.tight_layout()
        plt.savefig(out_dir / "critical_zone_error_box.png", dpi=200)
        plt.close()


def run(args: argparse.Namespace) -> None:
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    if sns is not None:
        sns.set_theme(style="whitegrid")
    if args.metrics:
        plot_metrics(_read_many(args.metrics), out_dir)
    if args.predictions:
        plot_predictions(_read_many(args.predictions), out_dir)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create result figures from metrics and predictions.")
    parser.add_argument("--metrics", nargs="*", default=[])
    parser.add_argument("--predictions", nargs="*", default=[])
    parser.add_argument("--out-dir", default="reports/figures")
    return parser.parse_args()


def main() -> None:
    run(parse_args())


if __name__ == "__main__":
    main()
