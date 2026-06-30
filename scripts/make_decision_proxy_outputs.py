from __future__ import annotations

import argparse
from pathlib import Path

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


def summarize_decision_metrics(metrics: pd.DataFrame) -> pd.DataFrame:
    group_cols = ["subset", "model", "lead_time", "policy"]
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


def best_by_decision_cost(summary: pd.DataFrame) -> pd.DataFrame:
    required = {"subset", "lead_time", "policy", "expected_cost_mean"}
    missing = sorted(required - set(summary.columns))
    if missing:
        raise ValueError(f"Missing required summary columns: {missing}")
    rows: list[pd.Series] = []
    for _, group in summary.groupby(["subset", "lead_time", "policy"], dropna=False):
        rows.append(group.sort_values("expected_cost_mean", ascending=True).iloc[0])
    return pd.DataFrame(rows).reset_index(drop=True)


def rmse_vs_decision_best(summary: pd.DataFrame, matrix_summary: pd.DataFrame, tcn_summary: pd.DataFrame) -> pd.DataFrame:
    model_metrics = pd.concat([matrix_summary, tcn_summary], ignore_index=True)
    model_metrics = model_metrics[model_metrics["split"].eq("test")].copy()
    if "rmse_mean" not in model_metrics.columns:
        raise ValueError("Expected rmse_mean in summary metrics.")

    rows: list[dict[str, object]] = []
    for (subset, lead_time, policy), group in summary.groupby(["subset", "lead_time", "policy"], dropna=False):
        cost_best = group.sort_values("expected_cost_mean", ascending=True).iloc[0]
        subset_metrics = model_metrics[model_metrics["subset"].eq(subset)].copy()
        subset_metrics = subset_metrics[pd.to_numeric(subset_metrics["rmse_mean"], errors="coerce").notna()]
        if subset_metrics.empty:
            continue
        rmse_best = subset_metrics.sort_values("rmse_mean", ascending=True).iloc[0]
        rows.append(
            {
                "subset": subset,
                "lead_time": lead_time,
                "policy": policy,
                "rmse_best_model": rmse_best["model"],
                "rmse_best_rmse": float(rmse_best["rmse_mean"]),
                "decision_best_model": cost_best["model"],
                "decision_best_expected_cost": float(cost_best["expected_cost_mean"]),
                "same_model": bool(rmse_best["model"] == cost_best["model"]),
            }
        )
    return pd.DataFrame(rows).sort_values(["subset", "lead_time", "policy"]).reset_index(drop=True)


def write_note(summary: pd.DataFrame, best: pd.DataFrame, discordance: pd.DataFrame, out_path: Path) -> None:
    lines = [
        "# Decision Proxy Extension Note",
        "",
        "Scope: benchmark-derived maintenance decision proxy using existing test predictions. This is not a real fleet cost model.",
        "",
        "Cost schema: preventive cost = 1, early cost per cycle = 0.02, late cost = 10, missed-critical cost = 20, critical threshold = 30 cycles.",
        "",
        "Lead times: 10, 20, 30, and 50 cycles. Lower expected cost and decision regret are better.",
        "",
        "## Best By Expected Cost",
        "",
        "```text",
        best[["subset", "lead_time", "policy", "model", "expected_cost_mean", "decision_regret_mean", "missed_critical_rate_mean"]].to_string(index=False),
        "```",
        "",
        "## RMSE-Best Vs Decision-Best",
        "",
        "```text",
        discordance.to_string(index=False),
        "```",
        "",
        "## Initial Reading",
        "",
        f"- RMSE-best and decision-best agree in {int(discordance['same_model'].sum())}/{len(discordance)} subset-lead-time cells.",
        "- Treat this as a declared-preference decision proxy, not as a validated maintenance scheduler.",
        "- If decision-best changes after adding TCN, report the raw cost components alongside RMSE and risk metrics.",
        "",
    ]
    out_path.write_text("\n".join(lines), encoding="utf-8")


def run(args: argparse.Namespace) -> None:
    roots = [Path(root) for root in args.roots]
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    prediction_paths = find_prediction_files(roots)
    predictions = read_predictions(prediction_paths)
    cost = MaintenanceCost(
        preventive_cost=args.preventive_cost,
        early_cost_per_cycle=args.early_cost_per_cycle,
        late_cost=args.late_cost,
        missed_critical_cost=args.missed_critical_cost,
        critical_threshold=args.critical_threshold,
    )
    seed_metrics = evaluate_prediction_frame(predictions, lead_times=args.lead_times, cost=cost)
    if "policy" not in seed_metrics.columns:
        seed_metrics["policy"] = "mean"

    summary = summarize_decision_metrics(seed_metrics)
    best = best_by_decision_cost(summary)
    matrix_summary = pd.read_csv(Path(args.matrix_summary))
    tcn_summary = pd.read_csv(Path(args.tcn_summary))
    discordance = rmse_vs_decision_best(summary, matrix_summary, tcn_summary)

    seed_metrics.to_csv(out_dir / "decision_proxy_seed_metrics.csv", index=False)
    summary.to_csv(out_dir / "decision_proxy_summary.csv", index=False)
    best.to_csv(out_dir / "decision_proxy_best_by_cost.csv", index=False)
    discordance.to_csv(out_dir / "decision_proxy_rmse_vs_cost_best.csv", index=False)
    write_note(summary, best, discordance, out_dir / "decision_proxy_note.md")
    print(f"Read {len(prediction_paths)} prediction files")
    print(f"Wrote {out_dir / 'decision_proxy_seed_metrics.csv'}")
    print(f"Wrote {out_dir / 'decision_proxy_summary.csv'}")
    print(f"Wrote {out_dir / 'decision_proxy_best_by_cost.csv'}")
    print(f"Wrote {out_dir / 'decision_proxy_rmse_vs_cost_best.csv'}")
    print(f"Wrote {out_dir / 'decision_proxy_note.md'}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate paper-facing decision proxy outputs.")
    parser.add_argument("--roots", nargs="+", default=["reports/tables/matrix", "reports/tables/matrix_tcn"])
    parser.add_argument("--out-dir", default="reports/paper")
    parser.add_argument("--matrix-summary", default="reports/tables/matrix/summary/summary_metrics.csv")
    parser.add_argument("--tcn-summary", default="reports/tables/matrix_tcn/summary/summary_metrics.csv")
    parser.add_argument("--lead-times", nargs="+", type=float, default=[10, 20, 30, 50])
    parser.add_argument("--preventive-cost", type=float, default=1.0)
    parser.add_argument("--early-cost-per-cycle", type=float, default=0.02)
    parser.add_argument("--late-cost", type=float, default=10.0)
    parser.add_argument("--missed-critical-cost", type=float, default=20.0)
    parser.add_argument("--critical-threshold", type=float, default=30.0)
    return parser.parse_args()


def main() -> None:
    run(parse_args())


if __name__ == "__main__":
    main()
