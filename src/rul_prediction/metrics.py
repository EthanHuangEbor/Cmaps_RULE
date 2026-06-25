from __future__ import annotations

import math
from typing import Any

import numpy as np


def _as_1d(values: Any) -> np.ndarray:
    arr = np.asarray(values, dtype=float).reshape(-1)
    if arr.size == 0:
        raise ValueError("Metric input is empty.")
    return arr


def rmse(y_true: Any, y_pred: Any) -> float:
    y_true_arr = _as_1d(y_true)
    y_pred_arr = _as_1d(y_pred)
    return float(np.sqrt(np.mean((y_pred_arr - y_true_arr) ** 2)))


def mae(y_true: Any, y_pred: Any) -> float:
    y_true_arr = _as_1d(y_true)
    y_pred_arr = _as_1d(y_pred)
    return float(np.mean(np.abs(y_pred_arr - y_true_arr)))


def nasa_score(y_true: Any, y_pred: Any) -> float:
    """Compute the asymmetric NASA PHM scoring function.

    Positive error means RUL overestimation, which is penalized more strongly
    because it is safety-critical.
    """
    y_true_arr = _as_1d(y_true)
    y_pred_arr = _as_1d(y_pred)
    diff = y_pred_arr - y_true_arr
    score = np.where(diff < 0, np.exp(-diff / 13.0) - 1.0, np.exp(diff / 10.0) - 1.0)
    return float(np.sum(score))


def critical_zone_rmse(y_true: Any, y_pred: Any, threshold: float = 50.0) -> float:
    y_true_arr = _as_1d(y_true)
    y_pred_arr = _as_1d(y_pred)
    mask = y_true_arr <= threshold
    if not np.any(mask):
        return math.nan
    return rmse(y_true_arr[mask], y_pred_arr[mask])


def overestimation_ratio(y_true: Any, y_pred: Any) -> float:
    y_true_arr = _as_1d(y_true)
    y_pred_arr = _as_1d(y_pred)
    return float(np.mean(y_pred_arr > y_true_arr))


def overestimation_magnitude(y_true: Any, y_pred: Any) -> float:
    y_true_arr = _as_1d(y_true)
    y_pred_arr = _as_1d(y_pred)
    over_errors = np.maximum(y_pred_arr - y_true_arr, 0.0)
    return float(np.mean(over_errors))


def regression_report(y_true: Any, y_pred: Any) -> dict[str, float]:
    return {
        "rmse": rmse(y_true, y_pred),
        "mae": mae(y_true, y_pred),
        "nasa_s_score": nasa_score(y_true, y_pred),
        "critical_rmse_30": critical_zone_rmse(y_true, y_pred, threshold=30),
        "critical_rmse_50": critical_zone_rmse(y_true, y_pred, threshold=50),
        "overestimation_ratio": overestimation_ratio(y_true, y_pred),
        "overestimation_magnitude": overestimation_magnitude(y_true, y_pred),
    }
