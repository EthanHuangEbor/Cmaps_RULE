from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
from sklearn.preprocessing import StandardScaler

from rul_prediction import data


@dataclass(frozen=True)
class DomainWindows:
    x_source_train: np.ndarray
    y_source_train: np.ndarray
    x_source_validation: np.ndarray
    y_source_validation: np.ndarray
    x_source_test: np.ndarray
    y_source_test: np.ndarray
    x_target_test: np.ndarray
    y_target_test: np.ndarray
    target_units: np.ndarray
    target_cycles: np.ndarray
    feature_columns: list[str]


def prepare_domain_windows(
    data_dir: str | Path,
    *,
    source_subset: str,
    target_subset: str,
    max_rul: int = 130,
    window_size: int = 30,
    stride: int = 1,
    validation_fraction: float = 0.2,
    seed: int = 42,
    include_settings: bool = True,
) -> DomainWindows:
    source_train_raw, source_test_raw, source_rul = data.load_subset(data_dir, source_subset)
    target_train_raw, target_test_raw, target_rul = data.load_subset(data_dir, target_subset)

    source_train_labeled = data.add_train_rul(source_train_raw, max_rul=max_rul)
    source_test_labeled = data.add_test_rul(source_test_raw, source_rul, max_rul=max_rul)
    target_train_labeled = data.add_train_rul(target_train_raw, max_rul=max_rul)
    target_test_labeled = data.add_test_rul(target_test_raw, target_rul, max_rul=max_rul)

    source_fit, source_validation = data.split_by_unit(source_train_labeled, validation_fraction, seed)
    feature_columns, _ = data.select_feature_columns(source_fit, include_settings=include_settings)
    scaler = StandardScaler()
    source_fit = source_fit.copy()
    source_validation = source_validation.copy()
    source_test_labeled = source_test_labeled.copy()
    target_train_labeled = target_train_labeled.copy()
    target_test_labeled = target_test_labeled.copy()
    source_fit[feature_columns] = scaler.fit_transform(source_fit[feature_columns])
    for frame in [source_validation, source_test_labeled, target_train_labeled, target_test_labeled]:
        frame[feature_columns] = scaler.transform(frame[feature_columns])

    x_source_train, y_source_train, _, _ = data.make_sequence_windows(
        source_fit, feature_columns, window_size, stride
    )
    x_source_validation, y_source_validation, _, _ = data.make_sequence_windows(
        source_validation, feature_columns, window_size, stride
    )
    x_source_test, y_source_test, _, _ = data.make_last_windows(source_test_labeled, feature_columns, window_size)
    x_target_test, y_target_test, target_units, target_cycles = data.make_last_windows(
        target_test_labeled, feature_columns, window_size
    )
    return DomainWindows(
        x_source_train=x_source_train,
        y_source_train=y_source_train,
        x_source_validation=x_source_validation,
        y_source_validation=y_source_validation,
        x_source_test=x_source_test,
        y_source_test=y_source_test,
        x_target_test=x_target_test,
        y_target_test=y_target_test,
        target_units=target_units,
        target_cycles=target_cycles,
        feature_columns=feature_columns,
    )
