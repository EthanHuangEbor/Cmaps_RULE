from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from rul_prediction.decision import MaintenanceCost, evaluate_prediction_frame


def run(args: argparse.Namespace) -> None:
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    predictions = pd.concat([pd.read_csv(path) for path in args.predictions], ignore_index=True)
    cost = MaintenanceCost(
        preventive_cost=args.preventive_cost,
        early_cost_per_cycle=args.early_cost_per_cycle,
        late_cost=args.late_cost,
        missed_critical_cost=args.missed_critical_cost,
        critical_threshold=args.critical_threshold,
    )

    frames: list[pd.DataFrame] = []
    if "y_pred" in predictions.columns:
        frames.append(
            evaluate_prediction_frame(predictions, lead_times=args.lead_times, trigger_column="y_pred", cost=cost)
        )
    for level in args.conservative_levels:
        column = f"y_lower_{int(round(level * 100))}"
        if column in predictions.columns:
            frame = evaluate_prediction_frame(predictions, lead_times=args.lead_times, trigger_column=column, cost=cost)
            frame["policy"] = f"lower_bound_{int(round(level * 100))}"
            frames.append(frame)
    if not frames:
        raise ValueError("No usable trigger columns found. Expected y_pred or y_lower_XX columns.")
    combined = pd.concat(frames, ignore_index=True)
    if "policy" not in combined.columns:
        combined["policy"] = "mean"
    else:
        combined["policy"] = combined["policy"].fillna("mean")
    combined.to_csv(out_dir / "decision_metrics.csv", index=False)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Evaluate maintenance policy costs from RUL predictions.")
    parser.add_argument("--predictions", nargs="+", required=True, type=Path)
    parser.add_argument("--out-dir", default="reports/tables/decision")
    parser.add_argument("--lead-times", nargs="+", type=float, default=[10, 20, 30, 50])
    parser.add_argument("--conservative-levels", nargs="+", type=float, default=[0.8, 0.9, 0.95])
    parser.add_argument("--preventive-cost", type=float, default=1.0)
    parser.add_argument("--early-cost-per-cycle", type=float, default=0.02)
    parser.add_argument("--late-cost", type=float, default=10.0)
    parser.add_argument("--missed-critical-cost", type=float, default=20.0)
    parser.add_argument("--critical-threshold", type=float, default=30.0)
    return parser.parse_args()


if __name__ == "__main__":
    run(parse_args())
