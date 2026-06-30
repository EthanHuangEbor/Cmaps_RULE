from __future__ import annotations

import argparse
import math
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

from rul_prediction.decision import MaintenanceCost, evaluate_prediction_frame


DECISION_METRICS = [
    "maintenance_rate",
    "early_maintenance_rate",
    "late_maintenance_rate",
    "missed_critical_rate",
    "expected_cost",
    "oracle_expected_cost",
    "decision_regret",
]

CRITICAL_METRICS = [
    "critical_count",
    "critical_rmse",
    "critical_mae",
    "critical_overestimation_ratio",
    "critical_overestimation_magnitude",
]


@dataclass(frozen=True)
class CostScenario:
    name: str
    preventive_cost: float
    early_cost_per_cycle: float
    late_cost: float
    missed_critical_cost: float
    critical_threshold: float

    def to_cost(self) -> MaintenanceCost:
        return MaintenanceCost(
            preventive_cost=self.preventive_cost,
            early_cost_per_cycle=self.early_cost_per_cycle,
            late_cost=self.late_cost,
            missed_critical_cost=self.missed_critical_cost,
            critical_threshold=self.critical_threshold,
        )


DEFAULT_COST_SCENARIOS = [
    CostScenario("baseline", 1.0, 0.02, 10.0, 20.0, 30.0),
    CostScenario("high_late", 1.0, 0.02, 20.0, 20.0, 30.0),
    CostScenario("high_missed", 1.0, 0.02, 10.0, 40.0, 30.0),
    CostScenario("early_penalty", 1.0, 0.05, 10.0, 20.0, 30.0),
    CostScenario("balanced_low", 1.0, 0.02, 5.0, 10.0, 30.0),
]


def find_prediction_files(roots: list[Path]) -> list[Path]:
    paths: list[Path] = []
    for root in roots:
        if root.is_file() and root.name == "predictions.csv":
            paths.append(root)
        elif root.exists():
            paths.extend(sorted(root.rglob("predictions.csv")))
    if not paths:
        raise FileNotFoundError(f"No predictions.csv files found under: {[str(root) for root in roots]}")
    return sorted(dict.fromkeys(paths))


def read_predictions(paths: list[Path]) -> pd.DataFrame:
    frames: list[pd.DataFrame] = []
    for path in paths:
        frame = pd.read_csv(path)
        frame["prediction_file"] = str(path)
        frames.append(frame)
    predictions = pd.concat(frames, ignore_index=True)
    required = {"subset", "model", "seed", "y_true", "y_pred"}
    missing = sorted(required - set(predictions.columns))
    if missing:
        raise ValueError(f"Missing required prediction columns: {missing}")
    return predictions


def _group_cols(predictions: pd.DataFrame) -> list[str]:
    return [col for col in ["subset", "model", "seed", "window_size", "max_rul"] if col in predictions.columns]


def critical_threshold_seed_metrics(predictions: pd.DataFrame, thresholds: list[float]) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    group_cols = _group_cols(predictions)
    groups = predictions.groupby(group_cols, dropna=False) if group_cols else [((), predictions)]
    for keys, group in groups:
        if group_cols:
            if len(group_cols) == 1:
                keys = (keys,)
            base = dict(zip(group_cols, keys))
        else:
            base = {}

        y_true = group["y_true"].to_numpy(dtype=float)
        y_pred = group["y_pred"].to_numpy(dtype=float)
        for threshold in thresholds:
            mask = y_true <= threshold
            count = int(mask.sum())
            if count == 0:
                rmse = math.nan
                mae = math.nan
                over_ratio = math.nan
                over_mag = math.nan
            else:
                error = y_pred[mask] - y_true[mask]
                over_error = np.maximum(error, 0.0)
                rmse = float(np.sqrt(np.mean(error**2)))
                mae = float(np.mean(np.abs(error)))
                over_ratio = float(np.mean(error > 0.0))
                over_mag = float(np.mean(over_error))
            rows.append(
                {
                    **base,
                    "critical_threshold_checked": float(threshold),
                    "critical_count": count,
                    "critical_rmse": rmse,
                    "critical_mae": mae,
                    "critical_overestimation_ratio": over_ratio,
                    "critical_overestimation_magnitude": over_mag,
                }
            )
    return pd.DataFrame(rows)


def summarize_critical_threshold_metrics(metrics: pd.DataFrame) -> pd.DataFrame:
    group_cols = ["subset", "model", "critical_threshold_checked"]
    summary = (
        metrics.groupby(group_cols, dropna=False)[CRITICAL_METRICS]
        .agg(["mean", "std"])
        .reset_index()
    )
    summary.columns = [
        "_".join([part for part in col if part]) if isinstance(col, tuple) else str(col)
        for col in summary.columns
    ]
    return summary.sort_values(group_cols).reset_index(drop=True)


def best_by_critical_rmse(summary: pd.DataFrame) -> pd.DataFrame:
    required = {"subset", "critical_threshold_checked", "critical_rmse_mean"}
    missing = sorted(required - set(summary.columns))
    if missing:
        raise ValueError(f"Missing required summary columns: {missing}")
    rows: list[pd.Series] = []
    for _, group in summary.groupby(["subset", "critical_threshold_checked"], dropna=False):
        rows.append(group.sort_values("critical_rmse_mean", ascending=True).iloc[0])
    return pd.DataFrame(rows).reset_index(drop=True)


def summarize_decision_metrics(metrics: pd.DataFrame) -> pd.DataFrame:
    group_cols = ["cost_scenario", "subset", "model", "lead_time", "policy"]
    value_cols = [col for col in DECISION_METRICS if col in metrics.columns]
    summary = (
        metrics.groupby(group_cols, dropna=False)[value_cols]
        .agg(["mean", "std"])
        .reset_index()
    )
    summary.columns = [
        "_".join([part for part in col if part]) if isinstance(col, tuple) else str(col)
        for col in summary.columns
    ]
    return summary.sort_values(group_cols).reset_index(drop=True)


def evaluate_decision_cost_sensitivity(
    predictions: pd.DataFrame,
    *,
    lead_times: list[float],
    scenarios: list[CostScenario],
) -> pd.DataFrame:
    frames: list[pd.DataFrame] = []
    for scenario in scenarios:
        frame = evaluate_prediction_frame(predictions, lead_times=lead_times, cost=scenario.to_cost())
        if "policy" not in frame.columns:
            frame["policy"] = "mean"
        frame["cost_scenario"] = scenario.name
        frame["preventive_cost"] = scenario.preventive_cost
        frame["early_cost_per_cycle"] = scenario.early_cost_per_cycle
        frame["late_cost"] = scenario.late_cost
        frame["missed_critical_cost"] = scenario.missed_critical_cost
        frame["critical_threshold"] = scenario.critical_threshold
        frames.append(frame)
    return pd.concat(frames, ignore_index=True)


def best_by_decision_cost(summary: pd.DataFrame) -> pd.DataFrame:
    required = {"cost_scenario", "subset", "lead_time", "policy", "expected_cost_mean"}
    missing = sorted(required - set(summary.columns))
    if missing:
        raise ValueError(f"Missing required summary columns: {missing}")
    rows: list[pd.Series] = []
    for _, group in summary.groupby(["cost_scenario", "subset", "lead_time", "policy"], dropna=False):
        rows.append(group.sort_values("expected_cost_mean", ascending=True).iloc[0])
    return pd.DataFrame(rows).reset_index(drop=True)


def read_test_summary(matrix_summary: Path, tcn_summary: Path) -> pd.DataFrame:
    model_metrics = pd.concat([pd.read_csv(matrix_summary), pd.read_csv(tcn_summary)], ignore_index=True)
    model_metrics = model_metrics[model_metrics["split"].eq("test")].copy()
    model_metrics = model_metrics[pd.to_numeric(model_metrics["rmse_mean"], errors="coerce").notna()]
    if model_metrics.empty:
        raise ValueError("No test summary rows with rmse_mean found.")
    return model_metrics


def rmse_vs_critical_best(critical_summary: pd.DataFrame, model_metrics: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for (subset, threshold), group in critical_summary.groupby(["subset", "critical_threshold_checked"], dropna=False):
        subset_metrics = model_metrics[model_metrics["subset"].eq(subset)]
        if subset_metrics.empty:
            continue
        rmse_best = subset_metrics.sort_values("rmse_mean", ascending=True).iloc[0]
        critical_best = group.sort_values("critical_rmse_mean", ascending=True).iloc[0]
        rows.append(
            {
                "subset": subset,
                "critical_threshold_checked": float(threshold),
                "rmse_best_model": rmse_best["model"],
                "rmse_best_rmse": float(rmse_best["rmse_mean"]),
                "critical_best_model": critical_best["model"],
                "critical_best_rmse": float(critical_best["critical_rmse_mean"]),
                "same_model": bool(rmse_best["model"] == critical_best["model"]),
            }
        )
    return pd.DataFrame(rows).sort_values(["subset", "critical_threshold_checked"]).reset_index(drop=True)


def rmse_vs_decision_best(decision_summary: pd.DataFrame, model_metrics: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for (scenario, subset, lead_time, policy), group in decision_summary.groupby(
        ["cost_scenario", "subset", "lead_time", "policy"], dropna=False
    ):
        subset_metrics = model_metrics[model_metrics["subset"].eq(subset)]
        if subset_metrics.empty:
            continue
        rmse_best = subset_metrics.sort_values("rmse_mean", ascending=True).iloc[0]
        decision_best = group.sort_values("expected_cost_mean", ascending=True).iloc[0]
        rows.append(
            {
                "cost_scenario": scenario,
                "subset": subset,
                "lead_time": float(lead_time),
                "policy": policy,
                "rmse_best_model": rmse_best["model"],
                "rmse_best_rmse": float(rmse_best["rmse_mean"]),
                "decision_best_model": decision_best["model"],
                "decision_best_expected_cost": float(decision_best["expected_cost_mean"]),
                "same_model": bool(rmse_best["model"] == decision_best["model"]),
            }
        )
    return pd.DataFrame(rows).sort_values(["cost_scenario", "subset", "lead_time", "policy"]).reset_index(drop=True)


def write_note(
    critical_best: pd.DataFrame,
    critical_discordance: pd.DataFrame,
    decision_best: pd.DataFrame,
    decision_discordance: pd.DataFrame,
    scenarios: list[CostScenario],
    out_path: Path,
) -> None:
    critical_agree = int(critical_discordance["same_model"].sum())
    decision_agree = int(decision_discordance["same_model"].sum())
    scenario_lines = [
        f"- {s.name}: preventive={s.preventive_cost}, early/cycle={s.early_cost_per_cycle}, "
        f"late={s.late_cost}, missed-critical={s.missed_critical_cost}, critical={s.critical_threshold}"
        for s in scenarios
    ]
    lines = [
        "# Sensitivity Checks Note",
        "",
        "Scope: no-retraining sensitivity checks over existing matrix and TCN test predictions.",
        "",
        "These checks test whether benchmark conclusions depend on declared critical-zone thresholds or maintenance cost weights. They are not a real fleet scheduler or aviation safety validation.",
        "",
        "## Decision Cost Scenarios",
        "",
        *scenario_lines,
        "",
        "Lead times: 10, 20, 30, and 50 cycles.",
        "",
        "## Critical-Threshold Best Models",
        "",
        "```text",
        critical_best[
            [
                "subset",
                "critical_threshold_checked",
                "model",
                "critical_rmse_mean",
                "critical_overestimation_magnitude_mean",
            ]
        ].to_string(index=False),
        "```",
        "",
        "## Critical Threshold RMSE-Best Vs Risk-Best",
        "",
        "```text",
        critical_discordance.to_string(index=False),
        "```",
        "",
        "## Decision Best Models By Cost Scenario",
        "",
        "```text",
        decision_best[
            [
                "cost_scenario",
                "subset",
                "lead_time",
                "policy",
                "model",
                "expected_cost_mean",
                "decision_regret_mean",
                "missed_critical_rate_mean",
            ]
        ].to_string(index=False),
        "```",
        "",
        "## Decision RMSE-Best Vs Cost-Best",
        "",
        "```text",
        decision_discordance.to_string(index=False),
        "```",
        "",
        "## Reading",
        "",
        f"- RMSE-best and critical-threshold-best agree in {critical_agree}/{len(critical_discordance)} subset-threshold cells.",
        f"- RMSE-best and decision-cost-best agree in {decision_agree}/{len(decision_discordance)} scenario-subset-lead-time cells.",
        "- If these agreement rates remain low, the paper can argue ranking discordance is not an artifact of one hand-picked threshold or cost schema.",
        "",
    ]
    out_path.write_text("\n".join(lines), encoding="utf-8")


def run(args: argparse.Namespace) -> None:
    roots = [Path(root) for root in args.roots]
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    prediction_paths = find_prediction_files(roots)
    predictions = read_predictions(prediction_paths)
    thresholds = [float(value) for value in args.critical_thresholds]
    lead_times = [float(value) for value in args.lead_times]
    scenarios = DEFAULT_COST_SCENARIOS
    model_metrics = read_test_summary(Path(args.matrix_summary), Path(args.tcn_summary))

    critical_seed = critical_threshold_seed_metrics(predictions, thresholds)
    critical_summary = summarize_critical_threshold_metrics(critical_seed)
    critical_best = best_by_critical_rmse(critical_summary)
    critical_discordance = rmse_vs_critical_best(critical_summary, model_metrics)

    decision_seed = evaluate_decision_cost_sensitivity(predictions, lead_times=lead_times, scenarios=scenarios)
    decision_summary = summarize_decision_metrics(decision_seed)
    decision_best = best_by_decision_cost(decision_summary)
    decision_discordance = rmse_vs_decision_best(decision_summary, model_metrics)

    critical_seed.to_csv(out_dir / "sensitivity_critical_threshold_seed_metrics.csv", index=False)
    critical_summary.to_csv(out_dir / "sensitivity_critical_threshold_summary.csv", index=False)
    critical_best.to_csv(out_dir / "sensitivity_critical_threshold_best.csv", index=False)
    critical_discordance.to_csv(out_dir / "sensitivity_critical_threshold_rmse_vs_risk_best.csv", index=False)
    decision_seed.to_csv(out_dir / "sensitivity_decision_cost_seed_metrics.csv", index=False)
    decision_summary.to_csv(out_dir / "sensitivity_decision_cost_summary.csv", index=False)
    decision_best.to_csv(out_dir / "sensitivity_decision_cost_best.csv", index=False)
    decision_discordance.to_csv(out_dir / "sensitivity_decision_cost_rmse_vs_cost_best.csv", index=False)
    write_note(
        critical_best,
        critical_discordance,
        decision_best,
        decision_discordance,
        scenarios,
        out_dir / "sensitivity_checks_note.md",
    )

    print(f"Read {len(prediction_paths)} prediction files")
    print(f"Critical-threshold cells: {len(critical_discordance)}")
    print(f"Decision-cost cells: {len(decision_discordance)}")
    print(f"Critical RMSE agreement: {int(critical_discordance['same_model'].sum())}/{len(critical_discordance)}")
    print(f"Decision cost agreement: {int(decision_discordance['same_model'].sum())}/{len(decision_discordance)}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate paper-facing sensitivity checks from existing predictions.")
    parser.add_argument("--roots", nargs="+", default=["reports/tables/matrix", "reports/tables/matrix_tcn"])
    parser.add_argument("--out-dir", default="reports/paper")
    parser.add_argument("--matrix-summary", default="reports/tables/matrix/summary/summary_metrics.csv")
    parser.add_argument("--tcn-summary", default="reports/tables/matrix_tcn/summary/summary_metrics.csv")
    parser.add_argument("--critical-thresholds", nargs="+", type=float, default=[20, 30, 50, 70])
    parser.add_argument("--lead-times", nargs="+", type=float, default=[10, 20, 30, 50])
    return parser.parse_args()


def main() -> None:
    run(parse_args())


if __name__ == "__main__":
    main()
