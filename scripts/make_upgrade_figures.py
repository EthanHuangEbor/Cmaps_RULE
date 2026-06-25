from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


def _save(fig, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(path, dpi=200)
    plt.close(fig)


def plot_model_heatmap(metrics_path: Path, out_dir: Path) -> None:
    df = pd.read_csv(metrics_path)
    test_df = df[df.get("split", "test").eq("test")] if "split" in df.columns else df
    if not {"subset", "model", "rmse"}.issubset(test_df.columns):
        return
    pivot = test_df.pivot_table(index="model", columns="subset", values="rmse", aggfunc="mean")
    fig, ax = plt.subplots(figsize=(8, max(3, 0.35 * len(pivot))))
    sns.heatmap(pivot, annot=True, fmt=".2f", cmap="viridis_r", ax=ax)
    ax.set_title("Test RMSE by Dataset and Model")
    _save(fig, out_dir / "model_dataset_rmse_heatmap.png")


def plot_uncertainty_calibration(interval_path: Path, out_dir: Path) -> None:
    df = pd.read_csv(interval_path)
    if not {"interval_level", "picp"}.issubset(df.columns):
        return
    fig, ax = plt.subplots(figsize=(5, 4))
    sns.lineplot(data=df, x="interval_level", y="picp", marker="o", ax=ax)
    ax.plot([0, 1], [0, 1], linestyle="--", color="gray", linewidth=1)
    ax.set_xlim(0.75, 1.0)
    ax.set_ylim(0.0, 1.0)
    ax.set_title("Prediction Interval Calibration")
    ax.set_xlabel("Nominal coverage")
    ax.set_ylabel("Empirical coverage")
    _save(fig, out_dir / "uncertainty_calibration.png")


def plot_decision_cost(decision_path: Path, out_dir: Path) -> None:
    df = pd.read_csv(decision_path)
    if not {"lead_time", "expected_cost"}.issubset(df.columns):
        return
    hue = "policy" if "policy" in df.columns else "model"
    fig, ax = plt.subplots(figsize=(7, 4))
    sns.lineplot(data=df, x="lead_time", y="expected_cost", hue=hue, marker="o", ax=ax)
    ax.set_title("Maintenance Decision Cost")
    ax.set_xlabel("Lead time")
    ax.set_ylabel("Expected cost")
    _save(fig, out_dir / "decision_cost_curve.png")


def plot_robustness(robustness_path: Path, out_dir: Path) -> None:
    df = pd.read_csv(robustness_path)
    if not {"perturbation", "level", "rmse"}.issubset(df.columns):
        return
    fig, ax = plt.subplots(figsize=(7, 4))
    sns.lineplot(data=df, x="level", y="rmse", hue="perturbation", marker="o", ax=ax)
    ax.set_title("Sensor Perturbation Robustness")
    ax.set_xlabel("Perturbation level")
    ax.set_ylabel("RMSE")
    _save(fig, out_dir / "sensor_robustness_curve.png")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate upgrade-paper figures from CSV outputs.")
    parser.add_argument("--metrics", type=Path)
    parser.add_argument("--interval-metrics", type=Path)
    parser.add_argument("--decision-metrics", type=Path)
    parser.add_argument("--robustness-metrics", type=Path)
    parser.add_argument("--out-dir", default="reports/paper/upgrade_figures", type=Path)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.metrics and args.metrics.exists():
        plot_model_heatmap(args.metrics, args.out_dir)
    if args.interval_metrics and args.interval_metrics.exists():
        plot_uncertainty_calibration(args.interval_metrics, args.out_dir)
    if args.decision_metrics and args.decision_metrics.exists():
        plot_decision_cost(args.decision_metrics, args.out_dir)
    if args.robustness_metrics and args.robustness_metrics.exists():
        plot_robustness(args.robustness_metrics, args.out_dir)


if __name__ == "__main__":
    main()
