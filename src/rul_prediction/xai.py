from __future__ import annotations

from collections.abc import Callable

import numpy as np
import pandas as pd

from rul_prediction.metrics import rmse


def aggregate_feature_importance(paths: list[str]) -> pd.DataFrame:
    frames: list[pd.DataFrame] = []
    for path in paths:
        frame = pd.read_csv(path)
        if not {"feature", "importance"}.issubset(frame.columns):
            raise ValueError(f"{path} must contain feature and importance columns.")
        frame["source_file"] = path
        frames.append(frame)
    if not frames:
        raise ValueError("No feature importance files were provided.")
    combined = pd.concat(frames, ignore_index=True)
    return (
        combined.groupby("feature", as_index=False)["importance"]
        .agg(["mean", "std", "count"])
        .reset_index()
        .sort_values("mean", ascending=False)
    )


def occlusion_importance(
    x: np.ndarray,
    y_true: np.ndarray,
    predict_fn: Callable[[np.ndarray], np.ndarray],
    feature_names: list[str],
    *,
    baseline_value: float = 0.0,
) -> pd.DataFrame:
    if x.shape[2] != len(feature_names):
        raise ValueError("feature_names length must match x.shape[2].")
    clean_pred = predict_fn(x)
    clean_rmse = rmse(y_true, clean_pred)
    rows: list[dict[str, float | str]] = []
    for idx, feature in enumerate(feature_names):
        perturbed = np.array(x, copy=True)
        perturbed[:, :, idx] = baseline_value
        perturbed_pred = predict_fn(perturbed)
        perturbed_rmse = rmse(y_true, perturbed_pred)
        rows.append(
            {
                "feature": feature,
                "clean_rmse": clean_rmse,
                "occluded_rmse": perturbed_rmse,
                "rmse_increase": perturbed_rmse - clean_rmse,
            }
        )
    return pd.DataFrame(rows).sort_values("rmse_increase", ascending=False)
