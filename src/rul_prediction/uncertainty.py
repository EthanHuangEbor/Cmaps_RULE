from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np
import torch
from torch import nn
from torch.utils.data import DataLoader

from rul_prediction.metrics import _as_1d, rmse
from rul_prediction.models_deep import SequenceDataset


INTERVAL_LEVELS = (0.80, 0.90, 0.95)


@dataclass(frozen=True)
class IntervalMetrics:
    level: float
    lower: float
    upper: float
    picp: float
    mpiw: float
    winkler: float
    critical_picp_30: float
    critical_picp_50: float


def enable_dropout_layers(model: nn.Module) -> None:
    """Keep dropout stochastic while leaving other layers in eval mode."""
    for module in model.modules():
        if isinstance(module, nn.Dropout):
            module.train()


def predict_samples(
    model: nn.Module,
    x: np.ndarray,
    device: torch.device | str,
    *,
    batch_size: int = 512,
    samples: int = 50,
    mc_dropout: bool = True,
) -> np.ndarray:
    if samples <= 0:
        raise ValueError("samples must be positive.")
    torch_device = torch.device(device)
    dataset = SequenceDataset(x, np.zeros(len(x), dtype=np.float32))
    loader = DataLoader(dataset, batch_size=batch_size, shuffle=False)
    all_samples: list[np.ndarray] = []
    for _ in range(samples):
        preds: list[np.ndarray] = []
        model.eval()
        if mc_dropout:
            enable_dropout_layers(model)
        with torch.no_grad():
            for batch_x, _ in loader:
                pred = model(batch_x.to(torch_device)).detach().cpu().numpy().reshape(-1)
                preds.append(pred)
        all_samples.append(np.concatenate(preds))
    return np.stack(all_samples, axis=0).astype(np.float32)


def ensemble_prediction(samples: np.ndarray) -> dict[str, np.ndarray]:
    sample_arr = np.asarray(samples, dtype=float)
    if sample_arr.ndim != 2:
        raise ValueError("samples must have shape [n_samples, n_observations].")
    return {
        "mean": sample_arr.mean(axis=0),
        "std": sample_arr.std(axis=0, ddof=1) if sample_arr.shape[0] > 1 else np.zeros(sample_arr.shape[1]),
    }


def prediction_intervals(samples: np.ndarray, levels: tuple[float, ...] = INTERVAL_LEVELS) -> dict[float, np.ndarray]:
    sample_arr = np.asarray(samples, dtype=float)
    if sample_arr.ndim != 2:
        raise ValueError("samples must have shape [n_samples, n_observations].")
    intervals: dict[float, np.ndarray] = {}
    for level in levels:
        if not 0.0 < level < 1.0:
            raise ValueError("interval levels must be in (0, 1).")
        alpha = 1.0 - level
        lower = np.quantile(sample_arr, alpha / 2.0, axis=0)
        upper = np.quantile(sample_arr, 1.0 - alpha / 2.0, axis=0)
        intervals[level] = np.vstack([lower, upper]).T
    return intervals


def winkler_score(y_true: Any, lower: Any, upper: Any, level: float) -> float:
    y_true_arr = _as_1d(y_true)
    lower_arr = _as_1d(lower)
    upper_arr = _as_1d(upper)
    alpha = 1.0 - level
    width = upper_arr - lower_arr
    below = y_true_arr < lower_arr
    above = y_true_arr > upper_arr
    score = width.copy()
    score[below] += (2.0 / alpha) * (lower_arr[below] - y_true_arr[below])
    score[above] += (2.0 / alpha) * (y_true_arr[above] - upper_arr[above])
    return float(np.mean(score))


def interval_metrics(
    y_true: Any,
    intervals: dict[float, np.ndarray],
    *,
    critical_thresholds: tuple[float, float] = (30.0, 50.0),
) -> list[dict[str, float]]:
    y_true_arr = _as_1d(y_true)
    rows: list[dict[str, float]] = []
    for level, bounds in intervals.items():
        lower = bounds[:, 0]
        upper = bounds[:, 1]
        covered = (y_true_arr >= lower) & (y_true_arr <= upper)
        row = {
            "interval_level": float(level),
            "picp": float(np.mean(covered)),
            "mpiw": float(np.mean(upper - lower)),
            "winkler_score": winkler_score(y_true_arr, lower, upper, level),
        }
        for threshold in critical_thresholds:
            mask = y_true_arr <= threshold
            key = f"critical_picp_{int(threshold)}"
            row[key] = float(np.mean(covered[mask])) if np.any(mask) else float("nan")
        rows.append(row)
    return rows


def uncertainty_error_correlation(y_true: Any, y_mean: Any, y_std: Any) -> float:
    y_true_arr = _as_1d(y_true)
    mean_arr = _as_1d(y_mean)
    std_arr = _as_1d(y_std)
    abs_error = np.abs(mean_arr - y_true_arr)
    if np.allclose(std_arr, std_arr[0]) or np.allclose(abs_error, abs_error[0]):
        return float("nan")
    return float(np.corrcoef(std_arr, abs_error)[0, 1])


def interval_report(y_true: Any, samples: np.ndarray, levels: tuple[float, ...] = INTERVAL_LEVELS) -> dict[str, float]:
    summary = ensemble_prediction(samples)
    intervals = prediction_intervals(samples, levels=levels)
    metrics: dict[str, float] = {
        "mean_rmse": rmse(y_true, summary["mean"]),
        "mean_uncertainty": float(np.mean(summary["std"])),
        "uncertainty_abs_error_corr": uncertainty_error_correlation(y_true, summary["mean"], summary["std"]),
    }
    for row in interval_metrics(y_true, intervals):
        level = int(round(row.pop("interval_level") * 100))
        for key, value in row.items():
            metrics[f"{key}_{level}"] = value
    return metrics
