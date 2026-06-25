from __future__ import annotations

import numpy as np
import pytest

from rul_prediction.robustness import add_gaussian_noise, mask_sensor_indices, random_sensor_mask


def test_mask_sensor_indices_sets_whole_channel() -> None:
    x = np.ones((2, 3, 4), dtype=np.float32)
    masked = mask_sensor_indices(x, [1, 3], value=0.0)
    assert np.all(masked[:, :, 1] == 0.0)
    assert np.all(masked[:, :, 3] == 0.0)
    assert np.all(masked[:, :, 0] == 1.0)


def test_random_sensor_mask_fraction() -> None:
    x = np.ones((2, 3, 10), dtype=np.float32)
    _, indices = random_sensor_mask(x, 0.2, seed=42)
    assert len(indices) == 2


def test_add_gaussian_noise_rejects_negative_std() -> None:
    with pytest.raises(ValueError):
        add_gaussian_noise(np.zeros((1, 2, 3), dtype=np.float32), -0.1)
