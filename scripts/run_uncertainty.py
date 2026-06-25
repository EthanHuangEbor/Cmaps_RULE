from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
import torch

from rul_prediction import data
from rul_prediction.metrics import regression_report
from rul_prediction.models_deep import predict, train_model
from rul_prediction.uncertainty import (
    ensemble_prediction,
    interval_metrics,
    prediction_intervals,
    predict_samples,
    uncertainty_error_correlation,
)


def _interval_columns(samples: np.ndarray, levels: tuple[float, ...]) -> dict[str, np.ndarray]:
    columns: dict[str, np.ndarray] = {}
    for level, bounds in prediction_intervals(samples, levels=levels).items():
        suffix = int(round(level * 100))
        columns[f"y_lower_{suffix}"] = bounds[:, 0]
        columns[f"y_upper_{suffix}"] = bounds[:, 1]
    return columns


def run(args: argparse.Namespace) -> None:
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    model_dir = out_dir / "models"
    model_dir.mkdir(exist_ok=True)
    levels = tuple(args.interval_levels)
    torch_device = args.device or ("cuda" if torch.cuda.is_available() else "cpu")

    prepared = data.prepare_data(
        args.data_dir,
        subset=args.subset,
        max_rul=args.max_rul,
        validation_fraction=args.validation_fraction,
        seed=args.seed,
    )
    x_train, y_train, _, _ = data.make_sequence_windows(
        prepared.train, prepared.feature_columns, args.window_size, args.stride
    )
    x_validation, y_validation, _, _ = data.make_sequence_windows(
        prepared.validation, prepared.feature_columns, args.window_size, args.stride
    )
    x_test, y_test, test_units, test_cycles = data.make_last_windows(
        prepared.test, prepared.feature_columns, args.window_size
    )

    if args.method == "mc_dropout":
        result = train_model(
            args.model,
            x_train,
            y_train,
            x_validation,
            y_validation,
            hidden_size=args.hidden_size,
            dropout=args.dropout,
            batch_size=args.batch_size,
            epochs=args.epochs,
            learning_rate=args.learning_rate,
            patience=args.patience,
            seed=args.seed,
            device=torch_device,
            num_layers=args.num_layers,
            loss_type=args.loss,
            critical_threshold=args.critical_threshold,
            critical_weight=args.critical_weight,
            over_weight=args.over_weight,
        )
        torch.save(result.model.state_dict(), model_dir / f"{args.model}_{args.method}_seed{args.seed}.pt")
        samples = predict_samples(
            result.model,
            x_test,
            torch_device,
            batch_size=args.batch_size,
            samples=args.mc_samples,
            mc_dropout=True,
        )
        used_seeds = [args.seed]
    else:
        ensemble_preds: list[np.ndarray] = []
        used_seeds = args.ensemble_seeds
        for seed in used_seeds:
            result = train_model(
                args.model,
                x_train,
                y_train,
                x_validation,
                y_validation,
                hidden_size=args.hidden_size,
                dropout=args.dropout,
                batch_size=args.batch_size,
                epochs=args.epochs,
                learning_rate=args.learning_rate,
                patience=args.patience,
                seed=seed,
                device=torch_device,
                num_layers=args.num_layers,
                loss_type=args.loss,
                critical_threshold=args.critical_threshold,
                critical_weight=args.critical_weight,
                over_weight=args.over_weight,
            )
            torch.save(result.model.state_dict(), model_dir / f"{args.model}_{args.method}_seed{seed}.pt")
            ensemble_preds.append(predict(result.model, x_test, torch.device(torch_device), args.batch_size))
        samples = np.stack(ensemble_preds, axis=0).astype(np.float32)

    summary = ensemble_prediction(samples)
    interval_cols = _interval_columns(samples, levels)
    predictions = pd.DataFrame(
        {
            "subset": args.subset,
            "model": f"{args.model}_{args.method}_{args.loss}",
            "seed": args.seed,
            "used_seeds": ",".join(str(seed) for seed in used_seeds),
            "window_size": args.window_size,
            "max_rul": args.max_rul,
            "unit": test_units,
            "cycle": test_cycles,
            "y_true": y_test,
            "y_pred": summary["mean"],
            "y_std": summary["std"],
            "error": summary["mean"] - y_test,
            **interval_cols,
        }
    )
    predictions.to_csv(out_dir / "predictions.csv", index=False)

    metric_row = {
        "subset": args.subset,
        "split": "test",
        "model": f"{args.model}_{args.method}_{args.loss}",
        "seed": args.seed,
        "used_seeds": ",".join(str(seed) for seed in used_seeds),
        "window_size": args.window_size,
        "max_rul": args.max_rul,
        "method": args.method,
        "loss": args.loss,
        "mean_uncertainty": float(np.mean(summary["std"])),
        "uncertainty_abs_error_corr": uncertainty_error_correlation(y_test, summary["mean"], summary["std"]),
        **regression_report(y_test, summary["mean"]),
    }
    pd.DataFrame([metric_row]).to_csv(out_dir / "metrics.csv", index=False)

    interval_rows = interval_metrics(y_test, prediction_intervals(samples, levels=levels))
    for row in interval_rows:
        row.update(
            {
                "subset": args.subset,
                "model": f"{args.model}_{args.method}_{args.loss}",
                "seed": args.seed,
                "method": args.method,
                "window_size": args.window_size,
                "max_rul": args.max_rul,
            }
        )
    pd.DataFrame(interval_rows).to_csv(out_dir / "interval_metrics.csv", index=False)
    (out_dir / "config.json").write_text(json.dumps(vars(args), indent=2), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run uncertainty-aware C-MAPSS RUL experiments.")
    parser.add_argument("--data-dir", default="data/raw")
    parser.add_argument("--subset", default="FD001")
    parser.add_argument("--out-dir", default="reports/tables/uncertainty_fd001")
    parser.add_argument("--method", choices=["mc_dropout", "deep_ensemble"], default="mc_dropout")
    parser.add_argument("--model", choices=["gru", "lstm", "cnn"], default="gru")
    parser.add_argument("--loss", choices=["mse", "critical_mse", "asymmetric_mse", "safety_mse"], default="mse")
    parser.add_argument("--max-rul", type=int, default=130)
    parser.add_argument("--window-size", type=int, default=30)
    parser.add_argument("--stride", type=int, default=1)
    parser.add_argument("--validation-fraction", type=float, default=0.2)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--ensemble-seeds", nargs="+", type=int, default=[42, 43, 44])
    parser.add_argument("--mc-samples", type=int, default=50)
    parser.add_argument("--interval-levels", nargs="+", type=float, default=[0.8, 0.9, 0.95])
    parser.add_argument("--epochs", type=int, default=100)
    parser.add_argument("--batch-size", type=int, default=128)
    parser.add_argument("--learning-rate", type=float, default=1e-3)
    parser.add_argument("--patience", type=int, default=10)
    parser.add_argument("--hidden-size", type=int, default=64)
    parser.add_argument("--num-layers", type=int, default=1)
    parser.add_argument("--dropout", type=float, default=0.2)
    parser.add_argument("--critical-threshold", type=float, default=50.0)
    parser.add_argument("--critical-weight", type=float, default=2.0)
    parser.add_argument("--over-weight", type=float, default=2.0)
    parser.add_argument("--device", default=None)
    return parser.parse_args()


if __name__ == "__main__":
    run(parse_args())
