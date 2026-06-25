from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd


def make_unit(unit: int, cycles: int, rng: np.random.Generator) -> pd.DataFrame:
    cycle = np.arange(1, cycles + 1)
    progress = cycle / cycles
    settings = rng.normal(0, 0.02, size=(cycles, 3))
    sensors = []
    for idx in range(21):
        base = 0.5 + 0.03 * idx
        trend = (idx % 5 - 2) * 0.04 * progress
        degradation = 0.25 * progress**2 if idx in {1, 5, 8, 12, 17} else 0.0
        noise = rng.normal(0, 0.02, size=cycles)
        sensors.append(base + trend + degradation + noise)
    data = np.column_stack([np.full(cycles, unit), cycle, settings, np.column_stack(sensors)])
    columns = ["unit", "cycle", *[f"setting_{i}" for i in range(1, 4)], *[f"sensor_{i}" for i in range(1, 22)]]
    return pd.DataFrame(data, columns=columns)


def write_space_table(df: pd.DataFrame, path: Path) -> None:
    df.to_csv(path, sep=" ", header=False, index=False, float_format="%.6f")


def main() -> None:
    parser = argparse.ArgumentParser(description="Create synthetic C-MAPSS-shaped smoke-test data.")
    parser.add_argument("--out-dir", default="data/raw")
    parser.add_argument("--subset", default="FD001")
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(args.seed)

    train_units = [make_unit(unit, int(rng.integers(70, 130)), rng) for unit in range(1, 13)]
    train = pd.concat(train_units, ignore_index=True)

    test_parts = []
    final_ruls = []
    for unit in range(1, 7):
        full_cycles = int(rng.integers(80, 140))
        observed_cycles = int(full_cycles * rng.uniform(0.45, 0.8))
        final_ruls.append(full_cycles - observed_cycles)
        test_parts.append(make_unit(unit, observed_cycles, rng))
    test = pd.concat(test_parts, ignore_index=True)

    subset = args.subset.upper()
    write_space_table(train, out_dir / f"train_{subset}.txt")
    write_space_table(test, out_dir / f"test_{subset}.txt")
    pd.DataFrame(final_ruls).to_csv(out_dir / f"RUL_{subset}.txt", sep=" ", header=False, index=False)
    print(f"Wrote synthetic smoke-test data to {out_dir}. Do not use it as research evidence.")


if __name__ == "__main__":
    main()

