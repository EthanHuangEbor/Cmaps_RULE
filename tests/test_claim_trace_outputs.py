from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pandas as pd


def load_module():
    path = Path("scripts/make_claim_trace_outputs.py")
    spec = importlib.util.spec_from_file_location("make_claim_trace_outputs", path)
    assert spec is not None
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_metric_improvement_count_ignores_nan_deltas() -> None:
    module = load_module()
    frame = pd.DataFrame(
        {
            "metric": ["rmse", "rmse", "rmse", "mae"],
            "delta_vs_best": [-1.0, 0.0, float("nan"), 2.0],
        }
    )

    improved, total = module._metric_improvement_count(frame, "rmse")

    assert improved == 2
    assert total == 2


def test_scenario_agreement_summary_reports_each_scenario() -> None:
    module = load_module()
    frame = pd.DataFrame(
        {
            "cost_scenario": ["a", "a", "b", "b", "b"],
            "same_model": [True, False, False, True, True],
        }
    )

    summary = module._scenario_agreement_summary(frame)

    assert summary == "a=1/2; b=2/3"


def test_safety_loss_gate_defers_immediate_tcn_safety_training() -> None:
    module = load_module()
    claim_map = pd.DataFrame(
        {
            "claim_id": ["TCN-003", "DEC-001", "SENS-001", "SENS-002"],
            "extracted_value": [
                "critical_rmse_50=1/4",
                "agreement=2/16",
                "agreement=2/16",
                "agreement=10/80",
            ],
        }
    )

    gate = module.build_safety_loss_gate(claim_map)

    immediate = gate[gate["gate_item"].eq("Recommended immediate action")].iloc[0]
    assert "defer TCN safety-loss" in immediate["decision"]
