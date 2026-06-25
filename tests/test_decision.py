from __future__ import annotations

import pandas as pd

from rul_prediction.decision import MaintenanceCost, evaluate_policy, evaluate_prediction_frame


def test_evaluate_policy_counts_late_decision() -> None:
    report = evaluate_policy([5, 50], [20, 20], lead_time=10, cost=MaintenanceCost())
    assert report["late_maintenance_rate"] == 0.5
    assert report["expected_cost"] > report["oracle_expected_cost"]


def test_evaluate_prediction_frame_groups_models() -> None:
    predictions = pd.DataFrame(
        {
            "subset": ["FD001", "FD001"],
            "model": ["a", "a"],
            "seed": [42, 42],
            "y_true": [5, 50],
            "y_pred": [20, 20],
        }
    )
    result = evaluate_prediction_frame(predictions, lead_times=[10])
    assert len(result) == 1
    assert result.loc[0, "model"] == "a"
