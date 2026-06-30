from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pandas as pd


def load_module():
    path = Path("scripts/make_sensitivity_outputs.py")
    spec = importlib.util.spec_from_file_location("make_sensitivity_outputs", path)
    assert spec is not None
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_critical_threshold_seed_metrics_uses_threshold_mask() -> None:
    module = load_module()
    predictions = pd.DataFrame(
        {
            "subset": ["FD001", "FD001", "FD001"],
            "model": ["toy", "toy", "toy"],
            "seed": [42, 42, 42],
            "y_true": [10.0, 30.0, 80.0],
            "y_pred": [12.0, 20.0, 90.0],
        }
    )

    metrics = module.critical_threshold_seed_metrics(predictions, thresholds=[20.0, 50.0])

    threshold_20 = metrics[metrics["critical_threshold_checked"].eq(20.0)].iloc[0]
    threshold_50 = metrics[metrics["critical_threshold_checked"].eq(50.0)].iloc[0]
    assert threshold_20["critical_count"] == 1
    assert threshold_20["critical_rmse"] == 2.0
    assert threshold_20["critical_overestimation_ratio"] == 1.0
    assert threshold_50["critical_count"] == 2
    assert round(threshold_50["critical_rmse"], 6) == 7.211103
    assert threshold_50["critical_overestimation_magnitude"] == 1.0


def test_best_by_critical_rmse_picks_lowest_summary_value() -> None:
    module = load_module()
    summary = pd.DataFrame(
        {
            "subset": ["FD001", "FD001", "FD002"],
            "model": ["bad", "good", "only"],
            "critical_threshold_checked": [50.0, 50.0, 50.0],
            "critical_rmse_mean": [4.0, 2.0, 3.0],
        }
    )

    best = module.best_by_critical_rmse(summary)

    assert best.loc[best["subset"].eq("FD001"), "model"].iloc[0] == "good"
    assert best.loc[best["subset"].eq("FD002"), "model"].iloc[0] == "only"


def test_decision_cost_sensitivity_adds_scenario_columns() -> None:
    module = load_module()
    predictions = pd.DataFrame(
        {
            "subset": ["FD001", "FD001"],
            "model": ["toy", "toy"],
            "seed": [42, 42],
            "y_true": [5.0, 40.0],
            "y_pred": [50.0, 5.0],
        }
    )
    scenarios = [
        module.CostScenario("cheap_late", 1.0, 0.0, 1.0, 2.0, 30.0),
        module.CostScenario("costly_late", 1.0, 0.0, 10.0, 20.0, 30.0),
    ]

    seed_metrics = module.evaluate_decision_cost_sensitivity(
        predictions,
        lead_times=[10.0],
        scenarios=scenarios,
    )
    summary = module.summarize_decision_metrics(seed_metrics)

    assert set(seed_metrics["cost_scenario"]) == {"cheap_late", "costly_late"}
    assert set(summary["cost_scenario"]) == {"cheap_late", "costly_late"}
    assert "expected_cost_mean" in summary.columns
