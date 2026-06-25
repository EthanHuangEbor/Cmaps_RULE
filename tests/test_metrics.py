import math

from rul_prediction.metrics import critical_zone_rmse, mae, overestimation_magnitude, overestimation_ratio, rmse


def test_basic_metrics():
    y_true = [10, 20, 40]
    y_pred = [12, 18, 41]
    assert math.isclose(mae(y_true, y_pred), 5 / 3)
    assert rmse(y_true, y_pred) > 0
    assert critical_zone_rmse(y_true, y_pred, threshold=30) > 0
    assert math.isclose(overestimation_ratio(y_true, y_pred), 2 / 3)
    assert math.isclose(overestimation_magnitude(y_true, y_pred), 1.0)
