from __future__ import annotations

from pathlib import Path

import joblib
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from rul_prediction import data as rul_data


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
            "font.size": 8,
            "axes.titlesize": 9,
            "axes.labelsize": 8,
            "xtick.labelsize": 7,
            "ytick.labelsize": 7,
            "legend.fontsize": 7,
            "figure.dpi": 300,
            "savefig.dpi": 300,
            "savefig.bbox": "tight",
            "axes.spines.top": False,
            "axes.spines.right": False,
        }
    )


def save_figure(fig: plt.Figure, out_dir: Path, stem: str) -> None:
    fig.savefig(out_dir / f"{stem}.pdf")
    fig.savefig(out_dir / f"{stem}.png")
    plt.close(fig)


def load_main_summary(root: Path) -> pd.DataFrame:
    matrix = pd.read_csv(root / "reports" / "tables" / "matrix" / "summary" / "summary_metrics.csv")
    matrix = matrix[(matrix["split"].eq("test")) & (matrix["window_size"].eq(30)) & (matrix["max_rul"].eq(130))]
    label_map = {
        "ridge": "Ridge",
        "random_forest": "Random Forest",
        "gradient_boosting": "Gradient Boosting",
        "lstm": "LSTM",
        "gru": "GRU",
        "cnn": "1D-CNN",
        "gru_safety_mse": "GRU safety-w2",
    }
    rows: list[dict[str, object]] = []
    for _, row in matrix.iterrows():
        rows.append(
            {
                "subset": row["subset"],
                "setting": label_map.get(str(row["model"]), str(row["model"])),
                "group": "main",
                "rmse_mean": row["rmse_mean"],
                "rmse_std": row["rmse_std"],
                "mae_mean": row["mae_mean"],
                "mae_std": row["mae_std"],
                "score_mean": row["nasa_s_score_mean"],
                "score_std": row["nasa_s_score_std"],
                "crit30_mean": row["critical_rmse_30_mean"],
                "crit30_std": row["critical_rmse_30_std"],
                "crit50_mean": row["critical_rmse_50_mean"],
                "crit50_std": row["critical_rmse_50_std"],
                "over_mean": row["overestimation_ratio_mean"],
                "over_std": row["overestimation_ratio_std"],
                "count": row["rmse_count"],
            }
        )
    return pd.DataFrame(rows)


def load_deep_ablation_summary(root: Path) -> pd.DataFrame:
    path = root / "reports" / "tables" / "deep_ablations" / "summary" / "summary_metrics.csv"
    if not path.exists():
        return pd.DataFrame()
    data = pd.read_csv(path)
    data = data[data["split"].eq("test")].copy()
    data["setting"] = data.apply(
        lambda r: ablation_label(
            str(r["model"]),
            int(r["window_size"]),
            int(r["hidden_size"]),
            int(r["num_layers"]),
            str(r["loss"]),
            float(r["critical_weight"]),
            str(r["scheduler"]),
        ),
        axis=1,
    )
    return pd.DataFrame(
        {
            "subset": data["subset"],
            "setting": data["setting"],
            "group": "focused",
            "rmse_mean": data["rmse_mean"],
            "rmse_std": data["rmse_std"],
            "mae_mean": data["mae_mean"],
            "mae_std": data["mae_std"],
            "score_mean": data["nasa_s_score_mean"],
            "score_std": data["nasa_s_score_std"],
            "crit30_mean": data["critical_rmse_30_mean"],
            "crit30_std": data["critical_rmse_30_std"],
            "crit50_mean": data["critical_rmse_50_mean"],
            "crit50_std": data["critical_rmse_50_std"],
            "over_mean": data["overestimation_ratio_mean"],
            "over_std": data["overestimation_ratio_std"],
            "count": data["rmse_count"],
        }
    )


def ablation_label(
    model: str,
    window_size: int,
    hidden_size: int,
    num_layers: int,
    loss: str,
    critical_weight: float,
    scheduler: str,
) -> str:
    if loss == "safety_mse":
        suffix = "w1.5" if abs(critical_weight - 1.5) < 1e-6 else "w2"
        label = f"GRU safety-{suffix}"
        if scheduler != "none":
            label += "+plateau"
        return label
    if model == "gru" and window_size == 30 and hidden_size == 64 and num_layers == 1 and scheduler == "none":
        return "GRU ablation-base"
    if model == "gru" and window_size != 30:
        return f"GRU window{window_size}"
    if model == "gru" and hidden_size != 64:
        return f"GRU hidden{hidden_size}"
    if model == "gru" and num_layers != 1:
        return f"GRU {num_layers}layer"
    if model == "gru":
        return "GRU"
    return model.upper()


def build_summary(root: Path) -> pd.DataFrame:
    summary = pd.concat([load_main_summary(root), load_deep_ablation_summary(root)], ignore_index=True)
    summary = summary.drop_duplicates(["subset", "setting", "group"], keep="last")
    return summary


def load_predictions(root: Path) -> pd.DataFrame:
    specs = [
        ("FD001", "Gradient Boosting", "matrix", "ml", "gradient_boosting"),
        ("FD001", "Random Forest", "matrix", "ml", "random_forest"),
        ("FD001", "GRU", "matrix", "deep", "gru"),
        ("FD001", "GRU safety-w1.5", "ablation", "safety_w1p5_h64_l1_w30", "gru_safety_mse"),
        ("FD003", "Gradient Boosting", "matrix", "ml", "gradient_boosting"),
        ("FD003", "Random Forest", "matrix", "ml", "random_forest"),
        ("FD003", "GRU", "matrix", "deep", "gru"),
        ("FD003", "GRU window50", "ablation", "window50_h64_l1", "gru"),
        ("FD003", "GRU safety-w1.5", "ablation", "safety_w1p5_h64_l1_w30", "gru_safety_mse"),
    ]
    rows: list[pd.DataFrame] = []
    for subset, setting, source, folder, model_name in specs:
        for seed in [42, 43, 44]:
            if source == "matrix":
                path = root / "reports" / "tables" / "matrix" / subset.lower() / f"seed_{seed}" / folder / "predictions.csv"
            else:
                path = root / "reports" / "tables" / "deep_ablations" / subset.lower() / f"seed_{seed}" / folder / "predictions.csv"
            if not path.exists():
                continue
            data = pd.read_csv(path)
            data = data[data["model"].eq(model_name)].copy()
            if data.empty:
                continue
            data["setting"] = setting
            rows.append(data)
    if not rows:
        return pd.DataFrame()
    return pd.concat(rows, ignore_index=True)


def plot_data_overview(root: Path, out_dir: Path) -> None:
    fig, axes = plt.subplots(2, 3, figsize=(7.1, 4.2))
    for row_idx, subset in enumerate(["FD001", "FD003"]):
        train_raw, test_raw, test_rul = rul_data.load_subset(root / "data" / "raw", subset)
        train = rul_data.add_train_rul(train_raw, max_rul=130)
        test = rul_data.add_test_rul(test_raw, test_rul, max_rul=130)
        train_lengths = train.groupby("unit")["cycle"].max()
        test_lengths = test.groupby("unit")["cycle"].max()

        axes[row_idx, 0].hist(train_lengths, bins=18, alpha=0.75, color=CB_PALETTE[0], label="Train")
        axes[row_idx, 0].hist(test_lengths, bins=18, alpha=0.55, color=CB_PALETTE[3], label="Test")
        axes[row_idx, 0].set_title(f"{subset} trajectory lengths")
        axes[row_idx, 0].set_xlabel("Observed cycles")
        axes[row_idx, 0].set_ylabel("Engine count")
        axes[row_idx, 0].legend(frameon=False)

        axes[row_idx, 1].hist(train["rul"], bins=25, color=CB_PALETTE[2], edgecolor="white", linewidth=0.3)
        axes[row_idx, 1].set_title(f"{subset} capped train RUL")
        axes[row_idx, 1].set_xlabel("Capped RUL (cycles)")
        axes[row_idx, 1].set_ylabel("Sample count")

        sensor = "sensor_3"
        for unit in sorted(train["unit"].unique())[:6]:
            group = train[train["unit"].eq(unit)].sort_values("cycle")
            values = group[sensor].to_numpy(dtype=float)
            values = (values - values.mean()) / (values.std() + 1e-8)
            axes[row_idx, 2].plot(group["cycle"], values, alpha=0.75, linewidth=0.8)
        axes[row_idx, 2].set_title(f"{subset} representative {sensor}")
        axes[row_idx, 2].set_xlabel("Cycle")
        axes[row_idx, 2].set_ylabel("Standardized value")
        for ax in axes[row_idx]:
            ax.grid(alpha=0.2)
    fig.tight_layout()
    save_figure(fig, out_dir, "figure_01_data_overview")


def plot_model_comparison(summary: pd.DataFrame, out_dir: Path) -> None:
    complete = summary[pd.to_numeric(summary["count"], errors="coerce").ge(3)].copy()
    complete["group_priority"] = complete["group"].map({"main": 0, "focused": 1}).fillna(2)
    selected = complete[
        complete["setting"].isin(
            [
                "Ridge",
                "Random Forest",
                "Gradient Boosting",
                "LSTM",
                "GRU",
                "GRU safety-w1.5",
                "GRU safety-w2",
                "GRU window50",
                "1D-CNN",
            ]
        )
    ].copy()
    selected = (
        selected.sort_values(["subset", "setting", "group_priority", "count"], ascending=[True, True, True, False])
        .drop_duplicates(["subset", "setting"], keep="first")
        .copy()
    )
    order = [
        "Ridge",
        "Random Forest",
        "Gradient Boosting",
        "LSTM",
        "GRU",
        "GRU safety-w1.5",
        "GRU safety-w2",
        "GRU window50",
        "1D-CNN",
    ]
    fig, axes = plt.subplots(1, 2, figsize=(7.1, 3.0), sharey=True)
    for ax, subset in zip(axes, ["FD001", "FD003"], strict=True):
        sub = selected[selected["subset"].eq(subset)].copy()
        sub["order"] = sub["setting"].map({name: idx for idx, name in enumerate(order)})
        sub = sub.sort_values("order")
        y = np.arange(len(sub))
        colors = [CB_PALETTE[idx % len(CB_PALETTE)] for idx in range(len(sub))]
        ax.barh(y, sub["rmse_mean"], xerr=sub["rmse_std"], color=colors, edgecolor="black", linewidth=0.35)
        ax.set_yticks(y)
        ax.set_yticklabels(sub["setting"])
        ax.invert_yaxis()
        ax.set_title(subset)
        ax.set_xlabel("Test RMSE (cycles)")
        ax.grid(axis="x", alpha=0.25)
    fig.tight_layout()
    save_figure(fig, out_dir, "figure_02_model_comparison")


def plot_prediction_scatter(predictions: pd.DataFrame, out_dir: Path) -> None:
    panel_specs = [
        ("FD001", "Gradient Boosting"),
        ("FD001", "GRU safety-w1.5"),
        ("FD003", "Gradient Boosting"),
        ("FD003", "GRU window50"),
    ]
    fig, axes = plt.subplots(2, 2, figsize=(6.9, 5.2), sharex=True, sharey=True)
    for ax, (subset, setting) in zip(axes.ravel(), panel_specs, strict=True):
        sub = predictions[predictions["subset"].eq(subset) & predictions["setting"].eq(setting)]
        if sub.empty:
            ax.set_visible(False)
            continue
        ax.scatter(sub["y_true"], sub["y_pred"], s=12, alpha=0.45, color=CB_PALETTE[0], edgecolor="none")
        lo = min(float(sub["y_true"].min()), float(sub["y_pred"].min()))
        hi = max(float(sub["y_true"].max()), float(sub["y_pred"].max()))
        ax.plot([lo, hi], [lo, hi], color="black", linewidth=0.8, linestyle="--")
        ax.set_title(f"{subset}: {setting}")
        ax.set_xlabel("True RUL (cycles)")
        ax.set_ylabel("Predicted RUL (cycles)")
        ax.grid(alpha=0.2)
    fig.tight_layout()
    save_figure(fig, out_dir, "figure_03_predicted_vs_true")


def plot_critical_residuals(predictions: pd.DataFrame, out_dir: Path) -> None:
    selected = predictions[
        predictions["setting"].isin(["Gradient Boosting", "Random Forest", "GRU", "GRU safety-w1.5", "GRU window50"])
    ].copy()
    selected["zone"] = np.where(selected["y_true"] <= 50, "RUL <= 50", "RUL > 50")
    fig, axes = plt.subplots(1, 2, figsize=(7.1, 3.4), sharey=True)
    for ax, subset in zip(axes, ["FD001", "FD003"], strict=True):
        sub = selected[selected["subset"].eq(subset)].copy()
        labels = []
        values = []
        colors = []
        settings = [s for s in ["Gradient Boosting", "Random Forest", "GRU", "GRU safety-w1.5", "GRU window50"] if s in set(sub["setting"])]
        for setting_idx, setting in enumerate(settings):
            for zone, shade in [("RUL <= 50", 0), ("RUL > 50", 1)]:
                zone_values = sub[sub["setting"].eq(setting) & sub["zone"].eq(zone)]["error"].to_numpy(dtype=float)
                if len(zone_values) == 0:
                    continue
                labels.append(f"{setting}\n{zone}")
                values.append(zone_values)
                colors.append(CB_PALETTE[setting_idx % len(CB_PALETTE)] if shade == 0 else "#BBBBBB")
        box = ax.boxplot(values, tick_labels=labels, patch_artist=True, showfliers=False)
        for patch, color in zip(box["boxes"], colors, strict=True):
            patch.set_facecolor(color)
            patch.set_alpha(0.75)
        ax.axhline(0, color="black", linewidth=0.8, linestyle="--")
        ax.set_title(subset)
        ax.set_ylabel("Prediction error (predicted - true)")
        ax.tick_params(axis="x", rotation=55)
        ax.grid(axis="y", alpha=0.25)
    fig.tight_layout()
    save_figure(fig, out_dir, "figure_04_critical_residuals")


def plot_hardest_engines(predictions: pd.DataFrame, out_dir: Path) -> None:
    panel_specs = [
        ("FD001", "Gradient Boosting"),
        ("FD001", "GRU safety-w1.5"),
        ("FD003", "Gradient Boosting"),
        ("FD003", "GRU window50"),
    ]
    fig, axes = plt.subplots(2, 2, figsize=(7.1, 5.2))
    for ax, (subset, setting) in zip(axes.ravel(), panel_specs, strict=True):
        sub = predictions[predictions["subset"].eq(subset) & predictions["setting"].eq(setting)].copy()
        if sub.empty:
            ax.set_visible(False)
            continue
        sub["abs_error"] = sub["error"].abs()
        worst = sub.groupby("unit", as_index=False)["abs_error"].mean().sort_values("abs_error", ascending=False).head(8)
        y = np.arange(len(worst))
        ax.barh(y, worst["abs_error"], color=CB_PALETTE[3], edgecolor="black", linewidth=0.35)
        ax.set_yticks(y)
        ax.set_yticklabels([f"Unit {int(u)}" for u in worst["unit"]])
        ax.invert_yaxis()
        ax.set_title(f"{subset}: {setting}")
        ax.set_xlabel("Mean absolute error (cycles)")
        ax.grid(axis="x", alpha=0.25)
    fig.tight_layout()
    save_figure(fig, out_dir, "figure_05_hardest_engines")


def plot_safety_tradeoff(summary: pd.DataFrame, out_dir: Path) -> None:
    complete = summary[pd.to_numeric(summary["count"], errors="coerce").ge(3)].copy()
    selected = summary[
        summary["setting"].isin(
            [
                "Random Forest",
                "Gradient Boosting",
                "LSTM",
                "GRU",
                "GRU safety-w1.5",
                "GRU safety-w2",
                "GRU window50",
                "1D-CNN",
            ]
        )
    ].copy()
    selected = complete[complete["setting"].isin(selected["setting"])].copy()
    fig, axes = plt.subplots(1, 2, figsize=(7.1, 3.2), sharey=True)
    handles_by_label = {}
    for ax, subset in zip(axes, ["FD001", "FD003"], strict=True):
        sub = selected[selected["subset"].eq(subset)].copy()
        for idx, (_, row) in enumerate(sub.iterrows()):
            marker = "o" if row["group"] == "main" else "s"
            size = max(35.0, min(160.0, float(row["rmse_mean"]) * 5.0))
            xerr = None if pd.isna(row["over_std"]) else float(row["over_std"])
            yerr = None if pd.isna(row["crit50_std"]) else float(row["crit50_std"])
            artist = ax.errorbar(
                row["over_mean"],
                row["crit50_mean"],
                xerr=xerr,
                yerr=yerr,
                fmt=marker,
                markersize=np.sqrt(size) / 1.8,
                color=CB_PALETTE[idx % len(CB_PALETTE)],
                markeredgecolor="black",
                markeredgewidth=0.4,
                elinewidth=0.7,
                capsize=2,
                alpha=0.85,
                label=row["setting"],
            )
            handles_by_label.setdefault(row["setting"], artist)
        ax.set_title(subset)
        ax.set_xlabel("Overestimation ratio")
        ax.set_ylabel("Critical RMSE, RUL <= 50")
        ax.grid(alpha=0.25)
    legend_order = [
        "Random Forest",
        "Gradient Boosting",
        "LSTM",
        "GRU",
        "GRU safety-w1.5",
        "GRU safety-w2",
        "GRU window50",
        "1D-CNN",
    ]
    legend_labels = [label for label in legend_order if label in handles_by_label]
    fig.legend(
        [handles_by_label[label] for label in legend_labels],
        legend_labels,
        loc="lower center",
        ncol=4,
        frameon=False,
        bbox_to_anchor=(0.5, 0.0),
    )
    fig.tight_layout(rect=[0, 0.18, 1, 1])
    save_figure(fig, out_dir, "figure_06_safety_tradeoff")


def load_history(root: Path) -> pd.DataFrame:
    specs = [
        ("FD001", "LSTM", "matrix", "deep", "lstm"),
        ("FD001", "GRU", "matrix", "deep", "gru"),
        ("FD001", "1D-CNN", "matrix", "deep", "cnn"),
        ("FD001", "GRU safety-w1.5", "ablation", "safety_w1p5_h64_l1_w30", "gru_safety_mse"),
        ("FD003", "LSTM", "matrix", "deep", "lstm"),
        ("FD003", "GRU", "matrix", "deep", "gru"),
        ("FD003", "1D-CNN", "matrix", "deep", "cnn"),
        ("FD003", "GRU window50", "ablation", "window50_h64_l1", "gru"),
    ]
    rows: list[pd.DataFrame] = []
    for subset, setting, source, folder, model_name in specs:
        for seed in [42, 43, 44]:
            if source == "matrix":
                path = root / "reports" / "tables" / "matrix" / subset.lower() / f"seed_{seed}" / folder / "training_history.csv"
            else:
                path = root / "reports" / "tables" / "deep_ablations" / subset.lower() / f"seed_{seed}" / folder / "training_history.csv"
            if not path.exists():
                continue
            data = pd.read_csv(path)
            data = data[data["model"].eq(model_name)].copy()
            if data.empty:
                continue
            data["subset"] = subset
            data["setting"] = setting
            rows.append(data)
    if not rows:
        return pd.DataFrame()
    return pd.concat(rows, ignore_index=True)


def plot_learning_curves(history: pd.DataFrame, out_dir: Path) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(7.1, 3.2), sharey=True)
    for ax, subset in zip(axes, ["FD001", "FD003"], strict=True):
        sub = history[history["subset"].eq(subset)]
        for idx, (setting, group) in enumerate(sub.groupby("setting")):
            curve = group.groupby("epoch", as_index=False)["validation_loss"].mean()
            ax.plot(curve["epoch"], curve["validation_loss"], label=setting, color=CB_PALETTE[idx % len(CB_PALETTE)], linewidth=1.2)
        ax.set_title(subset)
        ax.set_xlabel("Epoch")
        ax.set_ylabel("Validation loss")
        ax.set_yscale("log")
        ax.grid(alpha=0.25)
        ax.legend(frameon=False)
    fig.tight_layout()
    save_figure(fig, out_dir, "figure_07_learning_curves")


def summarize_rf_importance(root: Path, out_path: Path) -> pd.DataFrame:
    rows: list[pd.DataFrame] = []
    for subset in ["FD001", "FD003"]:
        for seed in [42, 43, 44]:
            base = root / "reports" / "tables" / "matrix" / subset.lower() / f"seed_{seed}" / "ml"
            model_path = base / "random_forest.joblib"
            feature_path = base / "tabular_features.csv"
            if not model_path.exists() or not feature_path.exists():
                continue
            model = joblib.load(model_path)
            features = pd.read_csv(feature_path)["feature"].to_numpy()
            values = np.asarray(model.feature_importances_, dtype=float)
            data = pd.DataFrame({"subset": subset, "seed": seed, "feature": features, "importance": values})
            rows.append(data)
    if not rows:
        return pd.DataFrame()
    all_importance = pd.concat(rows, ignore_index=True)
    summary = (
        all_importance.groupby(["subset", "feature"], as_index=False)
        .agg(importance_mean=("importance", "mean"), importance_std=("importance", "std"))
        .sort_values(["subset", "importance_mean"], ascending=[True, False])
    )
    summary.to_csv(out_path, index=False)
    return summary


def plot_feature_importance(importance: pd.DataFrame, out_dir: Path) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(7.1, 3.5), sharex=True)
    for ax, subset in zip(axes, ["FD001", "FD003"], strict=True):
        sub = importance[importance["subset"].eq(subset)].head(12).iloc[::-1]
        y = np.arange(len(sub))
        ax.barh(y, sub["importance_mean"], xerr=sub["importance_std"], color=CB_PALETTE[2], edgecolor="black", linewidth=0.35)
        ax.set_yticks(y)
        ax.set_yticklabels(sub["feature"])
        ax.set_title(subset)
        ax.set_xlabel("Mean random forest importance")
        ax.grid(axis="x", alpha=0.25)
    fig.tight_layout()
    save_figure(fig, out_dir, "figure_08_feature_importance")


def paired_bootstrap_rmse(
    predictions: pd.DataFrame,
    subset: str,
    model_a: str,
    model_b: str,
    n_boot: int = 5000,
    seed: int = 123,
) -> dict[str, object]:
    a = predictions[predictions["subset"].eq(subset) & predictions["setting"].eq(model_a)].copy()
    b = predictions[predictions["subset"].eq(subset) & predictions["setting"].eq(model_b)].copy()
    merged = a.merge(b, on=["subset", "seed", "unit", "cycle", "y_true"], suffixes=("_a", "_b"))
    if merged.empty:
        return {"subset": subset, "model_a": model_a, "model_b": model_b, "n": 0}
    rng = np.random.default_rng(seed)
    units = merged[["seed", "unit"]].drop_duplicates().reset_index(drop=True)
    observed = rmse(merged["error_a"]) - rmse(merged["error_b"])
    boot = np.empty(n_boot, dtype=float)
    for idx in range(n_boot):
        sample_idx = rng.integers(0, len(units), size=len(units))
        sampled_units = units.iloc[sample_idx].assign(sample_id=np.arange(len(sample_idx)))
        sampled = sampled_units.merge(merged, on=["seed", "unit"], how="left")
        boot[idx] = rmse(sampled["error_a"]) - rmse(sampled["error_b"])
    lo, hi = np.percentile(boot, [2.5, 97.5])
    return {
        "subset": subset,
        "model_a": model_a,
        "model_b": model_b,
        "n_engine_seed_pairs": len(units),
        "rmse_diff_a_minus_b": observed,
        "ci95_low": lo,
        "ci95_high": hi,
    }


def rmse(errors: pd.Series | np.ndarray) -> float:
    arr = np.asarray(errors, dtype=float)
    return float(np.sqrt(np.mean(arr**2)))


def write_arxiv_tables(root: Path, out_dir: Path, summary: pd.DataFrame, predictions: pd.DataFrame) -> None:
    summary.to_csv(out_dir / "arxiv_metric_summary.csv", index=False)
    complete = summary[pd.to_numeric(summary["count"], errors="coerce").ge(3)].copy()
    safety = []
    for subset in ["FD001", "FD003"]:
        sub = complete[complete["subset"].eq(subset)].copy()
        if sub.empty:
            continue
        safety.append(
            {
                "subset": subset,
                "best_rmse_model": sub.sort_values("rmse_mean").iloc[0]["setting"],
                "best_rmse": sub.sort_values("rmse_mean").iloc[0]["rmse_mean"],
                "best_critical_rmse50_model": sub.sort_values("crit50_mean").iloc[0]["setting"],
                "best_critical_rmse50": sub.sort_values("crit50_mean").iloc[0]["crit50_mean"],
                "lowest_over_ratio_model": sub.sort_values("over_mean").iloc[0]["setting"],
                "lowest_over_ratio": sub.sort_values("over_mean").iloc[0]["over_mean"],
            }
        )
    pd.DataFrame(safety).to_csv(out_dir / "safety_tradeoff_summary.csv", index=False)
    bootstrap_rows = [
        paired_bootstrap_rmse(predictions, "FD003", "GRU window50", "Gradient Boosting"),
        paired_bootstrap_rmse(predictions, "FD001", "GRU safety-w1.5", "Gradient Boosting"),
    ]
    pd.DataFrame(bootstrap_rows).to_csv(out_dir / "paired_bootstrap_rmse.csv", index=False)


def write_figure_trace(out_dir: Path) -> None:
    trace = [
        ("figure_01_data_overview", "data/raw train/test/RUL files", "C-MAPSS subset scope and sensor trajectory context"),
        ("figure_02_model_comparison", "reports/tables/*/summary_metrics.csv", "Aggregate model comparison under RMSE"),
        ("figure_03_predicted_vs_true", "reports/tables/**/predictions.csv", "Prediction calibration against official test RUL"),
        ("figure_04_critical_residuals", "reports/tables/**/predictions.csv", "Residual behavior inside and outside RUL <= 50"),
        ("figure_05_hardest_engines", "reports/tables/**/predictions.csv", "Engine-level failure cases"),
        ("figure_06_safety_tradeoff", "reports/paper/arxiv_metric_summary.csv", "Critical error and overestimation trade-off"),
        ("figure_07_learning_curves", "reports/tables/**/training_history.csv", "Deep model optimization dynamics"),
        ("figure_08_feature_importance", "reports/paper/rf_feature_importance_summary.csv", "Tree-model feature importance"),
    ]
    pd.DataFrame(trace, columns=["artifact_id", "source_data", "caption_claim"]).to_csv(
        out_dir / "figure_trace.csv", index=False
    )


def main() -> None:
    configure_matplotlib()
    root = Path(__file__).resolve().parents[1]
    out_dir = root / "reports" / "paper"
    figure_dir = out_dir / "figures"
    figure_dir.mkdir(parents=True, exist_ok=True)
    summary = build_summary(root)
    predictions = load_predictions(root)
    history = load_history(root)
    importance = summarize_rf_importance(root, out_dir / "rf_feature_importance_summary.csv")
    write_arxiv_tables(root, out_dir, summary, predictions)
    write_figure_trace(out_dir)

    plot_data_overview(root, figure_dir)
    plot_model_comparison(summary, figure_dir)
    plot_prediction_scatter(predictions, figure_dir)
    plot_critical_residuals(predictions, figure_dir)
    plot_hardest_engines(predictions, figure_dir)
    plot_safety_tradeoff(summary, figure_dir)
    plot_learning_curves(history, figure_dir)
    if not importance.empty:
        plot_feature_importance(importance, figure_dir)
    print(f"Wrote arXiv figures and tables to {out_dir}")


if __name__ == "__main__":
    main()
