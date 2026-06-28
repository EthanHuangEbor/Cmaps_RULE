from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
PAPER_DIR = ROOT / "reports" / "paper"
FIG_DIR = PAPER_DIR / "figures"
os.environ.setdefault("MPLCONFIGDIR", str(ROOT / ".matplotlib-cache"))

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

MATRIX_SUMMARY = ROOT / "reports" / "tables" / "matrix" / "summary"
ABLATION_SUMMARY = ROOT / "reports" / "tables" / "deep_ablations" / "summary"

CORE_MATRIX_MODELS = ["ridge", "random_forest", "gradient_boosting", "gru", "gru_safety_mse"]
BASELINE_PORTFOLIO = ["ridge", "random_forest", "gradient_boosting", "gru"]
ABLATION_REFERENCE_JOB = "baseline_lr1e-3_h64_l1_w30"

METRIC_COLUMNS = [
    "rmse",
    "mae",
    "nasa_per_engine",
    "critical_rmse_30",
    "critical_rmse_50",
    "overestimation_ratio",
    "overestimation_magnitude",
]

DISPLAY_METRICS = [
    ("rmse", "RMSE"),
    ("mae", "MAE"),
    ("nasa_per_engine", "NASA/engine"),
    ("critical_rmse_30", "Critical RMSE30"),
    ("critical_rmse_50", "Critical RMSE50"),
    ("overestimation_ratio", "Over. ratio"),
    ("overestimation_magnitude", "Over. magnitude"),
    ("sarbi", "SARBI"),
]

MODEL_LABELS = {
    "ridge": "Ridge",
    "random_forest": "Random Forest",
    "gradient_boosting": "Gradient Boosting",
    "gru": "GRU",
    "gru_safety_mse": "Safety-GRU",
}

JOB_LABELS = {
    "baseline_lr1e-3_h64_l1_w30": "Baseline GRU",
    "critical_w2_h64_l1_w30": "Critical w2",
    "critical_w3_h64_l1_w30": "Critical w3",
    "asymmetric_w2_h64_l1_w30": "Asymmetric w2",
    "asymmetric_w3_h64_l1_w30": "Asymmetric w3",
    "safety_w1p5_h64_l1_w30": "Safety w1.5",
    "safety_w2_h64_l1_w30": "Safety w2",
    "safety_w3_h64_l1_w30": "Safety w3",
}

PALETTE = {
    "Ridge": "#7F7F7F",
    "Random Forest": "#4C78A8",
    "Gradient Boosting": "#F58518",
    "GRU": "#54A24B",
    "Safety-GRU": "#B279A2",
    "Baseline GRU": "#54A24B",
    "Critical w2": "#72B7B2",
    "Critical w3": "#2CB1BC",
    "Asymmetric w2": "#FF9DA6",
    "Asymmetric w3": "#E45756",
    "Safety w1.5": "#B279A2",
    "Safety w2": "#9D755D",
    "Safety w3": "#8E6C8A",
}


@dataclass(frozen=True)
class ScoreWeights:
    accuracy: float = 1.0 / 3.0
    critical: float = 1.0 / 3.0
    risk: float = 1.0 / 3.0


def configure_matplotlib() -> None:
    matplotlib.rcParams.update(
        {
            "font.family": "sans-serif",
            "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans", "sans-serif"],
            "svg.fonttype": "none",
            "pdf.fonttype": 42,
            "font.size": 7,
            "axes.titlesize": 8,
            "axes.labelsize": 7,
            "xtick.labelsize": 6,
            "ytick.labelsize": 6,
            "legend.fontsize": 6,
            "figure.dpi": 300,
            "savefig.dpi": 600,
            "savefig.bbox": "tight",
            "axes.spines.top": False,
            "axes.spines.right": False,
            "axes.linewidth": 0.7,
            "axes.grid": True,
            "grid.alpha": 0.22,
            "grid.linewidth": 0.4,
        }
    )


def save_figure(fig: plt.Figure, stem: str) -> None:
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    fig.savefig(FIG_DIR / f"{stem}.png")
    fig.savefig(FIG_DIR / f"{stem}.pdf")
    plt.close(fig)


def load_seed_metrics(summary_dir: Path, models: list[str] | None = None) -> pd.DataFrame:
    data = pd.read_csv(summary_dir / "combined_metrics.csv")
    data = data[data["split"].eq("test")].copy()
    if models is not None:
        data = data[data["model"].isin(models)].copy()
    return data


def load_per_engine(summary_dir: Path, models: list[str] | None = None) -> pd.DataFrame:
    data = pd.read_csv(summary_dir / "per_engine_errors.csv")
    if models is not None:
        data = data[data["model"].isin(models)].copy()
    return data


def fill_overestimation_magnitude(metrics: pd.DataFrame, per_engine: pd.DataFrame) -> pd.DataFrame:
    over = per_engine.copy()
    over["over_error"] = np.maximum(over["pred_rul"] - over["true_rul"], 0.0)
    grouped = (
        over.groupby(["subset", "model", "seed"], as_index=False)["over_error"]
        .mean()
        .rename(columns={"over_error": "overestimation_magnitude"})
    )
    merged = metrics.merge(
        grouped,
        on=["subset", "model", "seed"],
        how="left",
        suffixes=("", "_filled"),
    )
    if "overestimation_magnitude" not in merged:
        merged["overestimation_magnitude"] = np.nan
    merged["overestimation_magnitude"] = merged["overestimation_magnitude"].fillna(
        merged["overestimation_magnitude_filled"]
    )
    return merged.drop(columns=[c for c in ["overestimation_magnitude_filled"] if c in merged])


def add_nasa_per_engine(metrics: pd.DataFrame, per_engine: pd.DataFrame) -> pd.DataFrame:
    n_test = per_engine.groupby("subset")["unit"].nunique().to_dict()
    out = metrics.copy()
    out["n_test_engines"] = out["subset"].map(n_test).astype(float)
    out["nasa_per_engine"] = out["nasa_s_score"] / out["n_test_engines"]
    return out


def reference_from_portfolio(metrics: pd.DataFrame, group_col: str, portfolio: list[str]) -> pd.DataFrame:
    refs = []
    ref_rows = metrics[metrics[group_col].isin(portfolio)]
    for subset, sub in ref_rows.groupby("subset"):
        row: dict[str, object] = {"subset": subset}
        for metric in METRIC_COLUMNS:
            row[f"{metric}_ref"] = float(sub[metric].median())
        refs.append(row)
    return pd.DataFrame(refs)


def reference_from_job(metrics: pd.DataFrame, job_name: str) -> pd.DataFrame:
    refs = []
    ref_rows = metrics[metrics["job_name"].eq(job_name)]
    for subset, sub in ref_rows.groupby("subset"):
        row: dict[str, object] = {"subset": subset}
        for metric in METRIC_COLUMNS:
            row[f"{metric}_ref"] = float(sub[metric].median())
        refs.append(row)
    return pd.DataFrame(refs)


def compute_sarbi(metrics: pd.DataFrame, refs: pd.DataFrame, weights: ScoreWeights = ScoreWeights()) -> pd.DataFrame:
    data = metrics.merge(refs, on="subset", how="left")
    eps = 1e-9
    for metric in METRIC_COLUMNS:
        data[f"z_{metric}"] = np.log((data[metric].astype(float) + eps) / (data[f"{metric}_ref"].astype(float) + eps))

    data["sarbi_accuracy_log"] = 0.5 * data["z_rmse"] + 0.5 * data["z_mae"]
    data["sarbi_critical_log"] = 0.5 * data["z_critical_rmse_30"] + 0.5 * data["z_critical_rmse_50"]
    data["sarbi_risk_log"] = (
        0.5 * data["z_nasa_per_engine"]
        + 0.25 * data["z_overestimation_ratio"]
        + 0.25 * data["z_overestimation_magnitude"]
    )
    data["sarbi_log"] = (
        weights.accuracy * data["sarbi_accuracy_log"]
        + weights.critical * data["sarbi_critical_log"]
        + weights.risk * data["sarbi_risk_log"]
    )
    data["sarbi"] = np.exp(data["sarbi_log"])
    return data


def summarize_scores(data: pd.DataFrame, group_cols: list[str], label_col: str) -> pd.DataFrame:
    aggregations = {metric: [("mean", "mean"), ("std", "std")] for metric in METRIC_COLUMNS + ["sarbi"]}
    flat_aggs = {}
    for metric, specs in aggregations.items():
        for suffix, func in specs:
            flat_aggs[f"{metric}_{suffix}"] = (metric, func)
    out = data.groupby(group_cols, as_index=False).agg(**flat_aggs)
    out["label"] = out[label_col].map({**MODEL_LABELS, **JOB_LABELS}).fillna(out[label_col])
    return out


def best_by_metric(summary: pd.DataFrame, entity_col: str, metrics: list[str]) -> pd.DataFrame:
    rows = []
    for subset, sub in summary.groupby("subset"):
        rmse_best = sub.loc[sub["rmse_mean"].idxmin()]
        for metric in metrics:
            metric_best = sub.loc[sub[f"{metric}_mean"].idxmin()]
            rows.append(
                {
                    "subset": subset,
                    "metric": metric,
                    "rmse_best": rmse_best[entity_col],
                    "metric_best": metric_best[entity_col],
                    "same_as_rmse_best": bool(rmse_best[entity_col] == metric_best[entity_col]),
                    "rmse_best_metric_value": rmse_best[f"{metric}_mean"],
                    "metric_best_value": metric_best[f"{metric}_mean"],
                    "rmse_at_rmse_best": rmse_best["rmse_mean"],
                    "rmse_at_metric_best": metric_best["rmse_mean"],
                    "rmse_change_pct": 100.0 * (metric_best["rmse_mean"] - rmse_best["rmse_mean"]) / rmse_best["rmse_mean"],
                }
            )
    return pd.DataFrame(rows)


def rank_discordance(summary: pd.DataFrame, entity_col: str) -> pd.DataFrame:
    rows = []
    metrics = ["mae", "nasa_per_engine", "critical_rmse_30", "critical_rmse_50", "overestimation_ratio", "overestimation_magnitude", "sarbi"]
    for subset, sub in summary.groupby("subset"):
        ranked = sub.copy()
        ranked["rmse_rank"] = ranked["rmse_mean"].rank(method="min")
        rmse_best = ranked.loc[ranked["rmse_rank"].idxmin(), entity_col]
        for metric in metrics:
            ranked[f"{metric}_rank"] = ranked[f"{metric}_mean"].rank(method="min")
            metric_best = ranked.loc[ranked[f"{metric}_rank"].idxmin(), entity_col]
            rows.append(
                {
                    "subset": subset,
                    "metric": metric,
                    "rmse_best": rmse_best,
                    "metric_best": metric_best,
                    "same_top1": bool(rmse_best == metric_best),
                    "spearman_vs_rmse": ranked["rmse_rank"].corr(ranked[f"{metric}_rank"], method="pearson"),
                }
            )
    return pd.DataFrame(rows)


def plot_rank_heatmap(summary: pd.DataFrame) -> None:
    fig, axes = plt.subplots(2, 2, figsize=(7.0, 5.6), constrained_layout=True)
    for ax, subset in zip(axes.flat, ["FD001", "FD002", "FD003", "FD004"], strict=True):
        sub = summary[summary["subset"].eq(subset)].copy()
        sub = sub.sort_values("sarbi_mean")
        rank_matrix = []
        for _, row in sub.iterrows():
            ranks = []
            for metric, _ in DISPLAY_METRICS:
                ranks.append(float(sub[f"{metric}_mean"].rank(method="min").loc[row.name]))
            rank_matrix.append(ranks)
        image = ax.imshow(np.asarray(rank_matrix), cmap="YlGnBu_r", vmin=1, vmax=len(sub))
        ax.set_title(subset)
        ax.set_yticks(np.arange(len(sub)))
        ax.set_yticklabels(sub["label"])
        ax.set_xticks(np.arange(len(DISPLAY_METRICS)))
        ax.set_xticklabels([label for _, label in DISPLAY_METRICS], rotation=35, ha="right")
        for i in range(len(sub)):
            for j in range(len(DISPLAY_METRICS)):
                ax.text(j, i, f"{rank_matrix[i][j]:.0f}", ha="center", va="center", fontsize=6)
        ax.grid(False)
    cbar = fig.colorbar(image, ax=axes.ravel().tolist(), shrink=0.72, pad=0.02)
    cbar.set_label("Rank (1 = best)")
    save_figure(fig, "figure_09_metric_rank_heatmap")


def plot_matrix_tradeoffs(summary: pd.DataFrame) -> None:
    fig, axes = plt.subplots(2, 2, figsize=(7.0, 5.6), constrained_layout=True)
    for ax, subset in zip(axes.flat, ["FD001", "FD002", "FD003", "FD004"], strict=True):
        sub = summary[summary["subset"].eq(subset)].copy()
        for _, row in sub.iterrows():
            label = row["label"]
            ax.scatter(
                row["rmse_mean"],
                row["critical_rmse_50_mean"],
                s=52,
                color=PALETTE.get(label, "#777777"),
                edgecolor="black",
                linewidth=0.4,
                alpha=0.92,
            )
            ax.annotate(label, (row["rmse_mean"], row["critical_rmse_50_mean"]), xytext=(3, 3), textcoords="offset points")
        ax.set_title(subset)
        ax.set_xlabel("RMSE")
        ax.set_ylabel("Critical RMSE50")
    save_figure(fig, "figure_10_rmse_vs_critical_rmse50")

    fig, axes = plt.subplots(2, 2, figsize=(7.0, 5.6), constrained_layout=True)
    for ax, subset in zip(axes.flat, ["FD001", "FD002", "FD003", "FD004"], strict=True):
        sub = summary[summary["subset"].eq(subset)].copy()
        for _, row in sub.iterrows():
            label = row["label"]
            ax.scatter(
                row["rmse_mean"],
                row["overestimation_magnitude_mean"],
                s=52,
                color=PALETTE.get(label, "#777777"),
                edgecolor="black",
                linewidth=0.4,
                alpha=0.92,
            )
            ax.annotate(label, (row["rmse_mean"], row["overestimation_magnitude_mean"]), xytext=(3, 3), textcoords="offset points")
        ax.set_title(subset)
        ax.set_xlabel("RMSE")
        ax.set_ylabel("Overestimation magnitude")
    save_figure(fig, "figure_11_rmse_vs_overestimation_magnitude")


def plot_ablation_tradeoff(summary: pd.DataFrame) -> None:
    fig, axes = plt.subplots(2, 2, figsize=(7.0, 5.6), constrained_layout=True)
    for ax, subset in zip(axes.flat, ["FD001", "FD002", "FD003", "FD004"], strict=True):
        sub = summary[summary["subset"].eq(subset)].copy()
        for _, row in sub.iterrows():
            label = row["label"]
            ax.scatter(
                row["rmse_mean"],
                row["overestimation_magnitude_mean"],
                s=46,
                color=PALETTE.get(label, "#777777"),
                edgecolor="black",
                linewidth=0.35,
                alpha=0.9,
            )
            ax.annotate(label, (row["rmse_mean"], row["overestimation_magnitude_mean"]), xytext=(3, 3), textcoords="offset points")
        ax.set_title(subset)
        ax.set_xlabel("RMSE")
        ax.set_ylabel("Overestimation magnitude")
    save_figure(fig, "figure_12_ablation_rmse_vs_overestimation")


def weight_sensitivity(metrics: pd.DataFrame, refs: pd.DataFrame, entity_col: str) -> pd.DataFrame:
    rows = []
    grid = np.arange(0.2, 0.61, 0.1)
    for critical_weight in grid:
        for risk_weight in grid:
            accuracy_weight = 1.0 - critical_weight - risk_weight
            if accuracy_weight < 0.2 or accuracy_weight > 0.6:
                continue
            scored = compute_sarbi(
                metrics,
                refs,
                ScoreWeights(accuracy=accuracy_weight, critical=critical_weight, risk=risk_weight),
            )
            summary = summarize_scores(scored, ["subset", entity_col], entity_col)
            for subset, sub in summary.groupby("subset"):
                best = sub.loc[sub["sarbi_mean"].idxmin()]
                rows.append(
                    {
                        "subset": subset,
                        "accuracy_weight": round(float(accuracy_weight), 3),
                        "critical_weight": round(float(critical_weight), 3),
                        "risk_weight": round(float(risk_weight), 3),
                        "best_entity": best[entity_col],
                        "best_label": best["label"],
                        "best_sarbi": best["sarbi_mean"],
                    }
                )
    return pd.DataFrame(rows)


def plot_weight_sensitivity(sensitivity: pd.DataFrame) -> None:
    labels = sorted(sensitivity["best_label"].unique())
    label_to_code = {label: i for i, label in enumerate(labels)}
    fig, axes = plt.subplots(2, 2, figsize=(7.0, 5.5), constrained_layout=True)
    cmap = plt.get_cmap("tab10", len(labels))
    for ax, subset in zip(axes.flat, ["FD001", "FD002", "FD003", "FD004"], strict=True):
        sub = sensitivity[sensitivity["subset"].eq(subset)]
        xs = sorted(sub["critical_weight"].unique())
        ys = sorted(sub["risk_weight"].unique())
        matrix = np.full((len(ys), len(xs)), np.nan)
        for _, row in sub.iterrows():
            x = xs.index(row["critical_weight"])
            y = ys.index(row["risk_weight"])
            matrix[y, x] = label_to_code[row["best_label"]]
        ax.imshow(matrix, cmap=cmap, vmin=-0.5, vmax=len(labels) - 0.5, origin="lower")
        ax.set_title(subset)
        ax.set_xticks(np.arange(len(xs)))
        ax.set_xticklabels([f"{x:.1f}" for x in xs])
        ax.set_yticks(np.arange(len(ys)))
        ax.set_yticklabels([f"{y:.1f}" for y in ys])
        ax.set_xlabel("Critical weight")
        ax.set_ylabel("Risk weight")
        ax.grid(False)
    handles = [
        plt.Line2D([0], [0], marker="s", color="none", markerfacecolor=cmap(label_to_code[label]), markersize=6, label=label)
        for label in labels
    ]
    fig.legend(handles=handles, loc="lower center", ncol=3, frameon=False, bbox_to_anchor=(0.5, -0.02))
    save_figure(fig, "figure_13_sarbi_weight_sensitivity")


def metric_from_arrays(true: np.ndarray, pred: np.ndarray, metric: str) -> float:
    diff = pred - true
    if metric == "rmse":
        return float(np.sqrt(np.mean(diff**2)))
    if metric == "critical_rmse_50":
        mask = true <= 50
        return float(np.sqrt(np.mean(diff[mask] ** 2))) if np.any(mask) else np.nan
    if metric == "overestimation_ratio":
        return float(np.mean(diff > 0))
    if metric == "overestimation_magnitude":
        return float(np.mean(np.maximum(diff, 0.0)))
    if metric == "nasa_per_engine":
        score = np.where(diff < 0, np.exp(-diff / 13.0) - 1.0, np.exp(diff / 10.0) - 1.0)
        return float(np.mean(score))
    raise ValueError(f"Unsupported metric: {metric}")


def bootstrap_rmse_vs_sarbi(per_engine: pd.DataFrame, matrix_summary: pd.DataFrame, n_boot: int = 2000) -> pd.DataFrame:
    rng = np.random.default_rng(20260628)
    rows = []
    metrics = ["rmse", "nasa_per_engine", "critical_rmse_50", "overestimation_ratio", "overestimation_magnitude"]
    for subset, sub in matrix_summary.groupby("subset"):
        rmse_best = sub.loc[sub["rmse_mean"].idxmin(), "model"]
        sarbi_best = sub.loc[sub["sarbi_mean"].idxmin(), "model"]
        base = per_engine[per_engine["subset"].eq(subset) & per_engine["model"].isin([rmse_best, sarbi_best])].copy()
        pivot = base.pivot_table(
            index=["seed", "unit"],
            columns="model",
            values=["true_rul", "pred_rul"],
            aggfunc="first",
        )
        if ("pred_rul", rmse_best) not in pivot.columns or ("pred_rul", sarbi_best) not in pivot.columns:
            continue
        pivot = pivot.dropna()
        clusters = np.arange(len(pivot))
        true = pivot[("true_rul", rmse_best)].to_numpy(dtype=float)
        pred_rmse = pivot[("pred_rul", rmse_best)].to_numpy(dtype=float)
        pred_sarbi = pivot[("pred_rul", sarbi_best)].to_numpy(dtype=float)
        for metric in metrics:
            observed = metric_from_arrays(true, pred_sarbi, metric) - metric_from_arrays(true, pred_rmse, metric)
            boot = []
            for _ in range(n_boot):
                idx = rng.choice(clusters, size=len(clusters), replace=True)
                boot.append(metric_from_arrays(true[idx], pred_sarbi[idx], metric) - metric_from_arrays(true[idx], pred_rmse[idx], metric))
            lower, upper = np.nanpercentile(boot, [2.5, 97.5])
            rows.append(
                {
                    "subset": subset,
                    "rmse_best_model": rmse_best,
                    "sarbi_best_model": sarbi_best,
                    "metric": metric,
                    "sarbi_minus_rmse_best": observed,
                    "ci95_low": lower,
                    "ci95_high": upper,
                    "n_paired_seed_engine": len(pivot),
                }
            )
    return pd.DataFrame(rows)


def main() -> None:
    configure_matplotlib()
    PAPER_DIR.mkdir(parents=True, exist_ok=True)

    matrix_engine = load_per_engine(MATRIX_SUMMARY, CORE_MATRIX_MODELS)
    matrix_metrics = load_seed_metrics(MATRIX_SUMMARY, CORE_MATRIX_MODELS)
    matrix_metrics = fill_overestimation_magnitude(matrix_metrics, matrix_engine)
    matrix_metrics = add_nasa_per_engine(matrix_metrics, matrix_engine)
    matrix_refs = reference_from_portfolio(matrix_metrics, "model", BASELINE_PORTFOLIO)
    matrix_scored = compute_sarbi(matrix_metrics, matrix_refs)
    matrix_scored["model_label"] = matrix_scored["model"].map(MODEL_LABELS)
    matrix_summary = summarize_scores(matrix_scored, ["subset", "model"], "model")

    ablation_engine = load_per_engine(ABLATION_SUMMARY)
    ablation_metrics = load_seed_metrics(ABLATION_SUMMARY)
    ablation_metrics = add_nasa_per_engine(ablation_metrics, ablation_engine)
    ablation_refs = reference_from_job(ablation_metrics, ABLATION_REFERENCE_JOB)
    ablation_scored = compute_sarbi(ablation_metrics, ablation_refs)
    ablation_scored["job_label"] = ablation_scored["job_name"].map(JOB_LABELS)
    ablation_summary = summarize_scores(ablation_scored, ["subset", "job_name"], "job_name")

    matrix_summary.to_csv(PAPER_DIR / "matrix_safety_benchmark_summary.csv", index=False)
    matrix_scored.to_csv(PAPER_DIR / "matrix_safety_benchmark_seed_scores.csv", index=False)
    best_by_metric(matrix_summary, "model", [m for m, _ in DISPLAY_METRICS]).to_csv(
        PAPER_DIR / "matrix_rmse_vs_risk_best.csv", index=False
    )
    rank_discordance(matrix_summary, "model").to_csv(PAPER_DIR / "matrix_rank_discordance.csv", index=False)

    ablation_summary.to_csv(PAPER_DIR / "deep_ablation_sarbi_summary.csv", index=False)
    ablation_scored.to_csv(PAPER_DIR / "deep_ablation_sarbi_seed_scores.csv", index=False)
    best_by_metric(ablation_summary, "job_name", [m for m, _ in DISPLAY_METRICS]).to_csv(
        PAPER_DIR / "deep_ablation_rmse_vs_risk_best.csv", index=False
    )
    rank_discordance(ablation_summary, "job_name").to_csv(PAPER_DIR / "deep_ablation_rank_discordance.csv", index=False)

    sensitivity = weight_sensitivity(matrix_metrics, matrix_refs, "model")
    sensitivity.to_csv(PAPER_DIR / "matrix_sarbi_weight_sensitivity.csv", index=False)
    bootstrap_rmse_vs_sarbi(matrix_engine, matrix_summary).to_csv(PAPER_DIR / "matrix_bootstrap_rmse_vs_sarbi.csv", index=False)

    plot_rank_heatmap(matrix_summary)
    plot_matrix_tradeoffs(matrix_summary)
    plot_ablation_tradeoff(ablation_summary)
    plot_weight_sensitivity(sensitivity)

    print("Wrote safety benchmark tables and figures to reports/paper")


if __name__ == "__main__":
    main()
