from __future__ import annotations

from pathlib import Path

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


CB_PALETTE = [
    "#0077BB",
    "#33BBEE",
    "#009988",
    "#EE7733",
    "#CC3311",
    "#EE3377",
    "#BBBBBB",
    "#000000",
]


def configure_matplotlib() -> None:
    matplotlib.rcParams.update(
        {
            "font.family": "sans-serif",
            "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans"],
            "font.size": 9,
            "axes.titlesize": 11,
            "axes.labelsize": 10,
            "xtick.labelsize": 8,
            "ytick.labelsize": 8,
            "legend.fontsize": 8,
            "figure.dpi": 300,
            "savefig.dpi": 300,
            "savefig.bbox": "tight",
            "axes.spines.top": False,
            "axes.spines.right": False,
        }
    )


def load_focused_rows(root: Path) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for metrics_path in (root / "reports" / "tables" / "deep_ablations").glob("fd*/seed_*/*/metrics.csv"):
        metrics = pd.read_csv(metrics_path)
        test = metrics[metrics["split"].eq("test")]
        if test.empty:
            continue
        row = test.iloc[0].to_dict()
        row["job"] = metrics_path.parent.name
        rows.append(row)
    return pd.DataFrame(rows)


def build_summary(root: Path) -> pd.DataFrame:
    matrix = pd.read_csv(root / "reports" / "tables" / "matrix" / "summary" / "summary_metrics.csv")
    matrix = matrix[(matrix["split"].eq("test")) & (matrix["window_size"].eq(30)) & (matrix["max_rul"].eq(130))]
    label_map = {
        "gradient_boosting": "Gradient Boosting",
        "random_forest": "Random Forest",
        "ridge": "Ridge",
        "lstm": "LSTM",
        "gru": "GRU",
        "cnn": "1D-CNN",
        "gru_safety_mse": "GRU safety-w2",
    }
    baseline_rows = []
    for _, row in matrix.iterrows():
        model = str(row["model"])
        baseline_rows.append(
            {
                "subset": row["subset"],
                "setting": label_map.get(model, model),
                "group": "main",
                "rmse_mean": row["rmse_mean"],
                "rmse_std": row["rmse_std"],
                "mae_mean": row["mae_mean"],
                "score_mean": row["nasa_s_score_mean"],
                "crit50_mean": row["critical_rmse_50_mean"],
                "over_mean": row["overestimation_ratio_mean"],
            }
        )

    focused = load_focused_rows(root)
    targets = {
        ("FD001", "safety_w1p5_h64_l1_w30"): "GRU safety-w1.5",
        ("FD003", "window50_h64_l1"): "GRU window50",
        ("FD003", "capacity_h128_l1_w30"): "GRU hidden128",
        ("FD003", "safety_w1p5_h64_l1_w30"): "GRU safety-w1.5",
    }
    focus = focused[focused.apply(lambda r: (r["subset"], r["job"]) in targets, axis=1)].copy()
    focus["setting"] = focus.apply(lambda r: targets[(r["subset"], r["job"])], axis=1)
    focus_summary = (
        focus.groupby(["subset", "setting"])
        .agg(
            rmse_mean=("rmse", "mean"),
            rmse_std=("rmse", "std"),
            mae_mean=("mae", "mean"),
            score_mean=("nasa_s_score", "mean"),
            crit50_mean=("critical_rmse_50", "mean"),
            over_mean=("overestimation_ratio", "mean"),
        )
        .reset_index()
    )
    focus_summary["group"] = "focused"
    columns = [
        "subset",
        "setting",
        "group",
        "rmse_mean",
        "rmse_std",
        "mae_mean",
        "score_mean",
        "crit50_mean",
        "over_mean",
    ]
    return pd.concat([pd.DataFrame(baseline_rows), focus_summary[columns]], ignore_index=True)


def plot_model_comparison(summary: pd.DataFrame, out_dir: Path) -> None:
    selected = summary[
        summary.apply(
            lambda r: (r["subset"], r["setting"])
            in {
                ("FD001", "Gradient Boosting"),
                ("FD001", "Random Forest"),
                ("FD001", "GRU safety-w1.5"),
                ("FD001", "GRU"),
                ("FD001", "LSTM"),
                ("FD001", "1D-CNN"),
                ("FD003", "Gradient Boosting"),
                ("FD003", "Random Forest"),
                ("FD003", "GRU window50"),
                ("FD003", "GRU safety-w1.5"),
                ("FD003", "GRU"),
                ("FD003", "LSTM"),
            },
            axis=1,
        )
    ].copy()
    order = ["Gradient Boosting", "Random Forest", "GRU safety-w1.5", "GRU window50", "GRU", "LSTM", "1D-CNN"]
    fig, axes = plt.subplots(1, 2, figsize=(7.0, 3.1), sharey=True)
    for ax, subset in zip(axes, ["FD001", "FD003"], strict=True):
        sub = selected[selected["subset"].eq(subset)].copy()
        sub["order"] = sub["setting"].map({name: i for i, name in enumerate(order)})
        sub = sub.sort_values("order")
        colors = [CB_PALETTE[i % len(CB_PALETTE)] for i in range(len(sub))]
        ax.bar(
            np.arange(len(sub)),
            sub["rmse_mean"],
            yerr=sub["rmse_std"],
            color=colors,
            edgecolor="black",
            linewidth=0.4,
            capsize=3,
        )
        ax.set_title(subset)
        ax.set_xticks(np.arange(len(sub)))
        ax.set_xticklabels(sub["setting"], rotation=35, ha="right")
        ax.set_ylabel("Test RMSE (cycles)")
        ax.set_ylim(0, max(25, float(selected["rmse_mean"].max()) + 3))
        ax.grid(axis="y", alpha=0.25)
    fig.suptitle("Model comparison under three random seeds", y=1.02)
    fig.tight_layout()
    fig.savefig(out_dir / "figure_1_model_comparison.pdf")
    fig.savefig(out_dir / "figure_1_model_comparison.png")
    plt.close(fig)


def plot_safety_tradeoff(summary: pd.DataFrame, out_dir: Path) -> None:
    selected = summary[
        summary["setting"].isin(
            [
                "Gradient Boosting",
                "Random Forest",
                "GRU",
                "LSTM",
                "GRU safety-w1.5",
                "GRU window50",
            ]
        )
    ].copy()
    fig, ax = plt.subplots(figsize=(5.2, 3.7))
    markers = {"FD001": "o", "FD003": "s"}
    colors = {"main": CB_PALETTE[0], "focused": CB_PALETTE[3]}
    for _, row in selected.iterrows():
        ax.scatter(
            row["over_mean"],
            row["rmse_mean"],
            marker=markers.get(row["subset"], "o"),
            s=55,
            color=colors.get(row["group"], CB_PALETTE[2]),
            edgecolor="black",
            linewidth=0.5,
            alpha=0.9,
        )
        ax.annotate(
            f"{row['subset']} {row['setting']}",
            (row["over_mean"], row["rmse_mean"]),
            xytext=(4, 3),
            textcoords="offset points",
            fontsize=7,
        )
    ax.set_xlabel("Overestimation ratio")
    ax.set_ylabel("Test RMSE (cycles)")
    ax.set_title("Accuracy and overestimation trade-off")
    ax.grid(alpha=0.25)
    fig.tight_layout()
    fig.savefig(out_dir / "figure_2_safety_tradeoff.pdf")
    fig.savefig(out_dir / "figure_2_safety_tradeoff.png")
    plt.close(fig)


def plot_focused_ablation(summary: pd.DataFrame, out_dir: Path) -> None:
    focused = summary[summary["group"].eq("focused")].copy()
    focused["label"] = focused["subset"] + " " + focused["setting"]
    focused = focused.sort_values(["subset", "rmse_mean"])
    metrics = [
        ("rmse_mean", "RMSE"),
        ("crit50_mean", "Critical RMSE <= 50"),
        ("over_mean", "Overestimation ratio"),
    ]
    fig, axes = plt.subplots(1, 3, figsize=(7.0, 3.3))
    y = np.arange(len(focused))
    for ax, (column, title) in zip(axes, metrics, strict=True):
        ax.barh(y, focused[column], color=CB_PALETTE[: len(focused)], edgecolor="black", linewidth=0.4)
        ax.set_title(title)
        ax.grid(axis="x", alpha=0.25)
        ax.invert_yaxis()
        if column == "rmse_mean":
            ax.errorbar(focused[column], y, xerr=focused["rmse_std"], fmt="none", ecolor="black", capsize=3)
    axes[0].set_yticks(y)
    axes[0].set_yticklabels(focused["label"])
    for ax in axes[1:]:
        ax.set_yticks(y)
        ax.set_yticklabels([])
    fig.suptitle("Focused GRU ablation results", y=1.02)
    fig.tight_layout()
    fig.savefig(out_dir / "figure_3_focused_ablation.pdf")
    fig.savefig(out_dir / "figure_3_focused_ablation.png")
    plt.close(fig)


def main() -> None:
    configure_matplotlib()
    root = Path(__file__).resolve().parents[1]
    out_dir = root / "reports" / "paper" / "figures"
    out_dir.mkdir(parents=True, exist_ok=True)
    summary = build_summary(root)
    summary.to_csv(root / "reports" / "paper" / "figure_data_summary.csv", index=False)
    plot_model_comparison(summary, out_dir)
    plot_safety_tradeoff(summary, out_dir)
    plot_focused_ablation(summary, out_dir)
    print(f"Wrote figures to {out_dir}")


if __name__ == "__main__":
    main()
