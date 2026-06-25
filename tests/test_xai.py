from __future__ import annotations

import numpy as np

from rul_prediction.xai import occlusion_importance


def test_occlusion_importance_returns_one_row_per_feature() -> None:
    x = np.ones((3, 2, 2), dtype=np.float32)
    y = np.array([1.0, 1.0, 1.0])

    def predict_fn(values: np.ndarray) -> np.ndarray:
        return values[:, :, 0].mean(axis=1)

    result = occlusion_importance(x, y, predict_fn, ["sensor_a", "sensor_b"])
    assert list(result["feature"]) == ["sensor_a", "sensor_b"]
