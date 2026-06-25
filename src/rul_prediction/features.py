from __future__ import annotations

import numpy as np
import pandas as pd


def _linear_slope(values: np.ndarray) -> np.ndarray:
    t = np.arange(values.shape[1], dtype=np.float32)
    t = t - t.mean()
    denom = float(np.sum(t**2))
    if denom == 0.0:
        return np.zeros(values.shape[2], dtype=np.float32)
    return np.sum(values * t[None, :, None], axis=1) / denom


def window_summary_features(windows: np.ndarray, feature_columns: list[str]) -> pd.DataFrame:
    """Convert sequence windows into tabular features for traditional models."""
    if windows.ndim != 3:
        raise ValueError("windows must have shape [n_windows, window_size, n_features].")
    if windows.shape[2] != len(feature_columns):
        raise ValueError("feature_columns length does not match windows shape.")

    parts: list[np.ndarray] = [
        windows.mean(axis=1),
        windows.std(axis=1),
        windows[:, -1, :],
        windows[:, -1, :] - windows[:, 0, :],
        _linear_slope(windows),
    ]
    suffixes = ["mean", "std", "last", "delta", "slope"]
    data = np.concatenate(parts, axis=1)
    names = [f"{column}_{suffix}" for suffix in suffixes for column in feature_columns]
    return pd.DataFrame(data, columns=names)

