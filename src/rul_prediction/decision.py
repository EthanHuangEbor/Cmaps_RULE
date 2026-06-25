from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np
import pandas as pd

from rul_prediction.metrics import _as_1d


@dataclass(frozen=True)
class MaintenanceCost:
    preventive_cost: float = 1.0
    early_cost_per_cycle: float = 0.02
    late_cost: float = 10.0
    missed_critical_cost: float = 20.0
    critical_threshold: float = 30.0


def maintenance_decisions(predicted_rul: Any, lead_time: float) -> np.ndarray:
    pred = _as_1d(predicted_rul)
    return pred <= lead_time


def oracle_decisions(true_rul: Any, lead_time: float) -> np.ndarray:
    true = _as_1d(true_rul)
    return true <= lead_time


def evaluate_policy(
    y_true: Any,
    trigger_rul: Any,
    *,
    lead_time: float,
    cost: MaintenanceCost = MaintenanceCost(),
) -> dict[str, float]:
    true = _as_1d(y_true)
    trigger = _as_1d(trigger_rul)
    decisions = maintenance_decisions(trigger, lead_time)
    oracle = oracle_decisions(true, lead_time)

    early = decisions & ~oracle
    late = ~decisions & oracle
    missed_critical = ~decisions & (true <= cost.critical_threshold)

    cost_values = np.zeros_like(true, dtype=float)
    cost_values[decisions] += cost.preventive_cost
    cost_values[early] += cost.early_cost_per_cycle * np.maximum(true[early] - lead_time, 0.0)
    cost_values[late] += cost.late_cost
    cost_values[missed_critical] += cost.missed_critical_cost

    oracle_cost_values = np.zeros_like(true, dtype=float)
    oracle_cost_values[oracle] += cost.preventive_cost
    return {
        "lead_time": float(lead_time),
        "maintenance_rate": float(np.mean(decisions)),
        "early_maintenance_rate": float(np.mean(early)),
        "late_maintenance_rate": float(np.mean(late)),
        "missed_critical_rate": float(np.mean(missed_critical)),
        "expected_cost": float(np.mean(cost_values)),
        "oracle_expected_cost": float(np.mean(oracle_cost_values)),
        "decision_regret": float(np.mean(cost_values - oracle_cost_values)),
    }


def evaluate_prediction_frame(
    predictions: pd.DataFrame,
    *,
    lead_times: list[float],
    trigger_column: str = "y_pred",
    cost: MaintenanceCost = MaintenanceCost(),
) -> pd.DataFrame:
    required = {"y_true", trigger_column}
    missing = sorted(required - set(predictions.columns))
    if missing:
        raise ValueError(f"Missing required prediction columns: {missing}")

    group_cols = [col for col in ["subset", "model", "seed", "window_size", "max_rul"] if col in predictions.columns]
    rows: list[dict[str, float | str | int]] = []
    groups = predictions.groupby(group_cols, dropna=False) if group_cols else [((), predictions)]
    for keys, group in groups:
        base: dict[str, float | str | int] = {}
        if group_cols:
            if len(group_cols) == 1:
                keys = (keys,)
            base = dict(zip(group_cols, keys))
        for lead_time in lead_times:
            rows.append(
                {
                    **base,
                    "trigger_column": trigger_column,
                    **evaluate_policy(group["y_true"], group[trigger_column], lead_time=lead_time, cost=cost),
                }
            )
    return pd.DataFrame(rows)
