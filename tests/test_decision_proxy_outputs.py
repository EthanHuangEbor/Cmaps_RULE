from __future__ import annotations

import importlib.util
from pathlib import Path

import pandas as pd


def load_module():
    path = Path("scripts/make_decision_proxy_outputs.py")
    spec = importlib.util.spec_from_file_location("make_decision_proxy_outputs", path)
    assert spec is not None
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_summarize_decision_metrics_averages_seed_level_rows() -> None:
    module = load_module()
    metrics = pd.DataFrame(
        {
            "subset": ["FD001", "FD001"],
            "model": ["a", "a"],
            "lead_time": [20.0, 20.0],
            "policy": ["mean", "mean"],
            "expected_cost": [2.0, 4.0],
            "decision_regret": [1.0, 3.0],
            "missed_critical_rate": [0.1, 0.3],
            "late_maintenance_rate": [0.2, 0.4],
            "early_maintenance_rate": [0.0, 0.2],
            "maintenance_rate": [0.5, 0.7],
        }
    )

    summary = module.summarize_decision_metrics(metrics)

    assert len(summary) == 1
    assert summary.loc[0, "expected_cost_mean"] == 3.0
    assert summary.loc[0, "decision_regret_mean"] == 2.0
    assert summary.loc[0, "missed_critical_rate_mean"] == 0.2


def test_best_by_decision_cost_picks_lowest_expected_cost() -> None:
    module = load_module()
    summary = pd.DataFrame(
        {
            "subset": ["FD001", "FD001", "FD002"],
            "model": ["slow", "cheap", "only"],
            "lead_time": [30.0, 30.0, 30.0],
            "policy": ["mean", "mean", "mean"],
            "expected_cost_mean": [5.0, 2.0, 3.0],
        }
    )

    best = module.best_by_decision_cost(summary)

    assert best.loc[best["subset"].eq("FD001"), "model"].iloc[0] == "cheap"
    assert best.loc[best["subset"].eq("FD002"), "model"].iloc[0] == "only"
