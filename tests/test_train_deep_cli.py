from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pandas as pd

from scripts.make_demo_data import main as make_demo_main


def test_train_deep_cli_writes_mlp_schema(tmp_path: Path, monkeypatch) -> None:
    data_dir = tmp_path / "demo_raw"
    out_dir = tmp_path / "deep_mlp"

    monkeypatch.setattr(sys, "argv", ["make_demo_data.py", "--out-dir", str(data_dir), "--subset", "FD001"])
    make_demo_main()

    subprocess.run(
        [
            sys.executable,
            "-m",
            "rul_prediction.train_deep",
            "--data-dir",
            str(data_dir),
            "--subset",
            "FD001",
            "--out-dir",
            str(out_dir),
            "--models",
            "mlp",
            "--epochs",
            "1",
            "--patience",
            "1",
            "--window-size",
            "20",
            "--batch-size",
            "16",
            "--device",
            "cpu",
        ],
        check=True,
    )

    expected_files = ["metrics.csv", "predictions.csv", "training_history.csv", "selected_features.csv"]
    for filename in expected_files:
        assert (out_dir / filename).exists()

    metrics = pd.read_csv(out_dir / "metrics.csv")
    predictions = pd.read_csv(out_dir / "predictions.csv")
    history = pd.read_csv(out_dir / "training_history.csv")
    features = pd.read_csv(out_dir / "selected_features.csv")

    assert set(metrics["model"]) == {"mlp"}
    assert set(metrics["split"]) == {"validation", "test"}
    assert {"rmse", "mae", "nasa_s_score", "critical_rmse_50", "overestimation_magnitude"}.issubset(metrics.columns)
    assert {"unit", "cycle", "y_true", "y_pred", "error"}.issubset(predictions.columns)
    assert set(history["model"]) == {"mlp"}
    assert "feature" in features.columns
