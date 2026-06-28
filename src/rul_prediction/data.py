from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler


SETTING_COLUMNS = [f"setting_{idx}" for idx in range(1, 4)]
SENSOR_COLUMNS = [f"sensor_{idx}" for idx in range(1, 22)]
CMAPSS_COLUMNS = ["unit", "cycle", *SETTING_COLUMNS, *SENSOR_COLUMNS]


@dataclass(frozen=True)
class PreparedData:
    train: pd.DataFrame
    validation: pd.DataFrame
    test: pd.DataFrame
    feature_columns: list[str]
    dropped_columns: list[str]
    scaler: StandardScaler


@dataclass(frozen=True)
class PairedSequenceWindows:
    x_current: np.ndarray
    y_current: np.ndarray
    x_future: np.ndarray
    y_future: np.ndarray
    horizon: np.ndarray
    units_current: np.ndarray
    units_future: np.ndarray
    cycles_current: np.ndarray
    cycles_future: np.ndarray


def _subset_path(data_dir: str | Path, subset: str, prefix: str) -> Path:
    subset = subset.upper()
    return Path(data_dir) / f"{prefix}_{subset}.txt"


def read_cmaps_table(path: str | Path) -> pd.DataFrame:
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(
            f"Missing C-MAPSS file: {path}. Download the official NASA data and place it in data/raw."
        )
    df = pd.read_csv(path, sep=r"\s+", header=None)
    if df.shape[1] != len(CMAPSS_COLUMNS):
        raise ValueError(f"Expected {len(CMAPSS_COLUMNS)} columns in {path}, got {df.shape[1]}.")
    df.columns = CMAPSS_COLUMNS
    return df


def read_rul_table(path: str | Path) -> pd.DataFrame:
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Missing C-MAPSS RUL file: {path}.")
    return pd.read_csv(path, sep=r"\s+", header=None, names=["final_rul"])


def load_subset(data_dir: str | Path, subset: str) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    train = read_cmaps_table(_subset_path(data_dir, subset, "train"))
    test = read_cmaps_table(_subset_path(data_dir, subset, "test"))
    rul = read_rul_table(_subset_path(data_dir, subset, "RUL"))
    return train, test, rul


def add_train_rul(train: pd.DataFrame, max_rul: int = 130) -> pd.DataFrame:
    df = train.copy()
    max_cycles = df.groupby("unit")["cycle"].transform("max")
    df["rul"] = (max_cycles - df["cycle"]).clip(upper=max_rul)
    return df


def add_test_rul(test: pd.DataFrame, rul: pd.DataFrame, max_rul: int = 130) -> pd.DataFrame:
    df = test.copy()
    final_rul_by_unit = dict(zip(sorted(df["unit"].unique()), rul["final_rul"].to_numpy()))
    max_cycle_by_unit = df.groupby("unit")["cycle"].transform("max")
    final_rul = df["unit"].map(final_rul_by_unit)
    if final_rul.isna().any():
        missing = sorted(df.loc[final_rul.isna(), "unit"].unique())
        raise ValueError(f"Missing final RUL values for units: {missing}")
    df["rul"] = (max_cycle_by_unit - df["cycle"] + final_rul).clip(upper=max_rul)
    return df


def select_feature_columns(
    train: pd.DataFrame,
    include_settings: bool = True,
    variance_threshold: float = 1e-10,
) -> tuple[list[str], list[str]]:
    candidates = [*SETTING_COLUMNS, *SENSOR_COLUMNS] if include_settings else SENSOR_COLUMNS.copy()
    variances = train[candidates].var(axis=0)
    feature_columns = [col for col in candidates if variances[col] > variance_threshold]
    dropped_columns = [col for col in candidates if col not in feature_columns]
    return feature_columns, dropped_columns


def split_by_unit(
    train: pd.DataFrame,
    validation_fraction: float = 0.2,
    seed: int = 42,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    if not 0.0 < validation_fraction < 1.0:
        raise ValueError("validation_fraction must be between 0 and 1.")
    units = np.array(sorted(train["unit"].unique()))
    rng = np.random.default_rng(seed)
    rng.shuffle(units)
    val_count = max(1, int(round(len(units) * validation_fraction)))
    validation_units = set(units[:val_count])
    validation = train[train["unit"].isin(validation_units)].copy()
    fit_train = train[~train["unit"].isin(validation_units)].copy()
    return fit_train, validation


def fit_transform_scaler(
    train: pd.DataFrame,
    validation: pd.DataFrame,
    test: pd.DataFrame,
    feature_columns: list[str],
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, StandardScaler]:
    scaler = StandardScaler()
    train_scaled = train.copy()
    validation_scaled = validation.copy()
    test_scaled = test.copy()
    train_scaled[feature_columns] = scaler.fit_transform(train_scaled[feature_columns])
    validation_scaled[feature_columns] = scaler.transform(validation_scaled[feature_columns])
    test_scaled[feature_columns] = scaler.transform(test_scaled[feature_columns])
    return train_scaled, validation_scaled, test_scaled, scaler


def prepare_data(
    data_dir: str | Path,
    subset: str = "FD001",
    max_rul: int = 130,
    validation_fraction: float = 0.2,
    seed: int = 42,
    include_settings: bool = True,
) -> PreparedData:
    train_raw, test_raw, test_rul = load_subset(data_dir, subset)
    train_labeled = add_train_rul(train_raw, max_rul=max_rul)
    test_labeled = add_test_rul(test_raw, test_rul, max_rul=max_rul)
    fit_train, validation = split_by_unit(train_labeled, validation_fraction, seed)
    feature_columns, dropped_columns = select_feature_columns(fit_train, include_settings=include_settings)
    fit_train, validation, test_labeled, scaler = fit_transform_scaler(
        fit_train, validation, test_labeled, feature_columns
    )
    return PreparedData(
        train=fit_train,
        validation=validation,
        test=test_labeled,
        feature_columns=feature_columns,
        dropped_columns=dropped_columns,
        scaler=scaler,
    )


def make_sequence_windows(
    df: pd.DataFrame,
    feature_columns: list[str],
    window_size: int = 30,
    stride: int = 1,
    label_column: str = "rul",
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    windows: list[np.ndarray] = []
    labels: list[float] = []
    units: list[int] = []
    cycles: list[int] = []
    for unit, group in df.sort_values(["unit", "cycle"]).groupby("unit"):
        values = group[feature_columns].to_numpy(dtype=np.float32)
        label_values = group[label_column].to_numpy(dtype=np.float32)
        cycle_values = group["cycle"].to_numpy(dtype=np.int32)
        if len(group) < window_size:
            continue
        for end_idx in range(window_size, len(group) + 1, stride):
            windows.append(values[end_idx - window_size : end_idx])
            labels.append(label_values[end_idx - 1])
            units.append(int(unit))
            cycles.append(int(cycle_values[end_idx - 1]))
    if not windows:
        raise ValueError("No sequence windows were created. Reduce window_size or check the data.")
    return (
        np.stack(windows).astype(np.float32),
        np.asarray(labels, dtype=np.float32),
        np.asarray(units, dtype=np.int32),
        np.asarray(cycles, dtype=np.int32),
    )


def make_paired_sequence_windows(
    df: pd.DataFrame,
    feature_columns: list[str],
    window_size: int = 30,
    stride: int = 1,
    pair_horizon: int = 1,
    label_column: str = "rul",
) -> PairedSequenceWindows:
    if pair_horizon < 1:
        raise ValueError("pair_horizon must be at least 1.")
    x_current: list[np.ndarray] = []
    y_current: list[float] = []
    x_future: list[np.ndarray] = []
    y_future: list[float] = []
    horizons: list[int] = []
    units_current: list[int] = []
    units_future: list[int] = []
    cycles_current: list[int] = []
    cycles_future: list[int] = []

    for unit, group in df.sort_values(["unit", "cycle"]).groupby("unit"):
        values = group[feature_columns].to_numpy(dtype=np.float32)
        labels = group[label_column].to_numpy(dtype=np.float32)
        cycles = group["cycle"].to_numpy(dtype=np.int32)
        if len(group) < window_size + pair_horizon:
            continue
        end_indices = list(range(window_size, len(group) + 1, stride))
        index_by_cycle = {int(cycles[end_idx - 1]): end_idx for end_idx in end_indices}
        for end_idx in end_indices:
            current_cycle = int(cycles[end_idx - 1])
            future_cycle = current_cycle + pair_horizon
            future_end_idx = index_by_cycle.get(future_cycle)
            if future_end_idx is None:
                continue
            x_current.append(values[end_idx - window_size : end_idx])
            y_current.append(float(labels[end_idx - 1]))
            x_future.append(values[future_end_idx - window_size : future_end_idx])
            y_future.append(float(labels[future_end_idx - 1]))
            horizons.append(pair_horizon)
            units_current.append(int(unit))
            units_future.append(int(unit))
            cycles_current.append(current_cycle)
            cycles_future.append(future_cycle)

    if not x_current:
        raise ValueError("No paired sequence windows were created. Reduce window_size or pair_horizon.")
    return PairedSequenceWindows(
        x_current=np.stack(x_current).astype(np.float32),
        y_current=np.asarray(y_current, dtype=np.float32),
        x_future=np.stack(x_future).astype(np.float32),
        y_future=np.asarray(y_future, dtype=np.float32),
        horizon=np.asarray(horizons, dtype=np.float32),
        units_current=np.asarray(units_current, dtype=np.int32),
        units_future=np.asarray(units_future, dtype=np.int32),
        cycles_current=np.asarray(cycles_current, dtype=np.int32),
        cycles_future=np.asarray(cycles_future, dtype=np.int32),
    )


def make_last_windows(
    df: pd.DataFrame,
    feature_columns: list[str],
    window_size: int = 30,
    label_column: str = "rul",
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    windows: list[np.ndarray] = []
    labels: list[float] = []
    units: list[int] = []
    cycles: list[int] = []
    for unit, group in df.sort_values(["unit", "cycle"]).groupby("unit"):
        values = group[feature_columns].to_numpy(dtype=np.float32)
        if len(values) < window_size:
            pad = np.repeat(values[:1], window_size - len(values), axis=0)
            values = np.vstack([pad, values])
        last_window = values[-window_size:]
        windows.append(last_window)
        labels.append(float(group[label_column].iloc[-1]))
        units.append(int(unit))
        cycles.append(int(group["cycle"].iloc[-1]))
    return (
        np.stack(windows).astype(np.float32),
        np.asarray(labels, dtype=np.float32),
        np.asarray(units, dtype=np.int32),
        np.asarray(cycles, dtype=np.int32),
    )

