from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class PerturbationSpec:
    kind: str
    level: float
    seed: int = 42
    sensor_indices: tuple[int, ...] | None = None


def add_gaussian_noise(x: np.ndarray, std: float, seed: int = 42) -> np.ndarray:
    if std < 0:
        raise ValueError("std must be non-negative.")
    rng = np.random.default_rng(seed)
    return (x + rng.normal(0.0, std, size=x.shape)).astype(np.float32)


def mask_sensor_indices(x: np.ndarray, sensor_indices: list[int] | tuple[int, ...], value: float = 0.0) -> np.ndarray:
    perturbed = np.array(x, copy=True)
    if not sensor_indices:
        return perturbed.astype(np.float32)
    max_index = perturbed.shape[2] - 1
    bad = [idx for idx in sensor_indices if idx < 0 or idx > max_index]
    if bad:
        raise IndexError(f"sensor_indices out of range: {bad}; max index is {max_index}.")
    perturbed[:, :, list(sensor_indices)] = value
    return perturbed.astype(np.float32)


def random_sensor_mask(x: np.ndarray, fraction: float, seed: int = 42, value: float = 0.0) -> tuple[np.ndarray, list[int]]:
    if not 0.0 <= fraction <= 1.0:
        raise ValueError("fraction must be in [0, 1].")
    feature_count = x.shape[2]
    mask_count = int(round(feature_count * fraction))
    rng = np.random.default_rng(seed)
    indices = sorted(rng.choice(feature_count, size=mask_count, replace=False).tolist()) if mask_count else []
    return mask_sensor_indices(x, indices, value=value), indices


def perturb_windows(x: np.ndarray, spec: PerturbationSpec) -> tuple[np.ndarray, dict[str, object]]:
    kind = spec.kind.lower()
    if kind == "noise":
        return add_gaussian_noise(x, spec.level, seed=spec.seed), {"noise_std": spec.level}
    if kind == "random_mask":
        perturbed, indices = random_sensor_mask(x, spec.level, seed=spec.seed)
        return perturbed, {"masked_indices": indices, "mask_fraction": spec.level}
    if kind == "important_mask":
        if spec.sensor_indices is None:
            raise ValueError("important_mask requires sensor_indices.")
        return mask_sensor_indices(x, spec.sensor_indices), {"masked_indices": list(spec.sensor_indices)}
    raise ValueError(f"Unsupported perturbation kind: {spec.kind}")


def performance_drop(clean_metric: float, perturbed_metric: float) -> float:
    return float(perturbed_metric - clean_metric)
