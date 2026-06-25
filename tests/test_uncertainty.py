from __future__ import annotations

import numpy as np

from rul_prediction.uncertainty import interval_metrics, prediction_intervals, uncertainty_error_correlation


def test_prediction_intervals_have_expected_bounds() -> None:
    samples = np.array([[0.0, 10.0], [2.0, 12.0], [4.0, 14.0]])
    intervals = prediction_intervals(samples, levels=(0.8,))
    assert intervals[0.8].shape == (2, 2)
    assert intervals[0.8][0, 0] < intervals[0.8][0, 1]


def test_interval_metrics_reports_coverage() -> None:
    intervals = {0.9: np.array([[0.0, 2.0], [0.0, 2.0]])}
    rows = interval_metrics([1.0, 3.0], intervals)
    assert rows[0]["picp"] == 0.5
    assert "winkler_score" in rows[0]


def test_uncertainty_error_correlation_constant_returns_nan() -> None:
    value = uncertainty_error_correlation([1, 2], [1, 3], [0.5, 0.5])
    assert np.isnan(value)
