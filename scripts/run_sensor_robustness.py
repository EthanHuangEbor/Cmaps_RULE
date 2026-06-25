from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd
import torch

from rul_prediction import data
from rul_prediction.features import window_summary_features
from rul_prediction.metrics import regression_report
from rul_prediction.models_deep import predict, train_model
from rul_prediction.robustness import PerturbationSpec, performance_drop, perturb_windows
from rul_prediction.train_ml import build_models


def run(args: argparse.Namespace) -> None:
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
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

    model_name = args.model.lower()
    if model_name in {"ridge", "random_forest", "gradient_boosting", "xgboost"}:
        models = build_models(
            args.seed,
            n_jobs=args.n_jobs,
            model_names=[model_name],
            rf_n_estimators=args.rf_n_estimators,
            gb_n_estimators=args.gb_n_estimators,
        )
        model = models[model_name]
        model.fit(window_summary_features(x_train, prepared.feature_columns), y_train)

        def predict_fn(windows):
            return model.predict(window_summary_features(windows, prepared.feature_columns))

    else:
        device = args.device or ("cuda" if torch.cuda.is_available() else "cpu")
        result = train_model(
            model_name,
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
            device=device,
            num_layers=args.num_layers,
            loss_type=args.loss,
        )

        def predict_fn(windows):
            return predict(result.model, windows, torch.device(device), args.batch_size)

    clean_pred = predict_fn(x_test)
    clean_report = regression_report(y_test, clean_pred)
    rows = [
        {
            "subset": args.subset,
            "model": model_name,
            "seed": args.seed,
            "perturbation": "clean",
            "level": 0.0,
            "details": "",
            **clean_report,
            "rmse_drop": 0.0,
        }
    ]
    prediction_frames = [
        pd.DataFrame(
            {
                "subset": args.subset,
                "model": model_name,
                "seed": args.seed,
                "perturbation": "clean",
                "level": 0.0,
                "unit": test_units,
                "cycle": test_cycles,
                "y_true": y_test,
                "y_pred": clean_pred,
                "error": clean_pred - y_test,
            }
        )
    ]

    specs: list[PerturbationSpec] = []
    specs += [PerturbationSpec("noise", level, seed=args.seed) for level in args.noise_levels]
    specs += [PerturbationSpec("random_mask", level, seed=args.seed) for level in args.mask_fractions]
    if args.important_indices:
        specs.append(PerturbationSpec("important_mask", 1.0, seed=args.seed, sensor_indices=tuple(args.important_indices)))

    for spec in specs:
        perturbed, details = perturb_windows(x_test, spec)
        y_pred = predict_fn(perturbed)
        report = regression_report(y_test, y_pred)
        rows.append(
            {
                "subset": args.subset,
                "model": model_name,
                "seed": args.seed,
                "perturbation": spec.kind,
                "level": spec.level,
                "details": str(details),
                **report,
                "rmse_drop": performance_drop(clean_report["rmse"], report["rmse"]),
            }
        )
        prediction_frames.append(
            pd.DataFrame(
                {
                    "subset": args.subset,
                    "model": model_name,
                    "seed": args.seed,
                    "perturbation": spec.kind,
                    "level": spec.level,
                    "unit": test_units,
                    "cycle": test_cycles,
                    "y_true": y_test,
                    "y_pred": y_pred,
                    "error": y_pred - y_test,
                }
            )
        )

    pd.DataFrame(rows).to_csv(out_dir / "robustness_metrics.csv", index=False)
    pd.concat(prediction_frames, ignore_index=True).to_csv(out_dir / "robustness_predictions.csv", index=False)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run sensor noise and masking robustness checks.")
    parser.add_argument("--data-dir", default="data/raw")
    parser.add_argument("--subset", default="FD001")
    parser.add_argument("--out-dir", default="reports/tables/robustness_fd001")
    parser.add_argument("--model", default="gradient_boosting", choices=["ridge", "random_forest", "gradient_boosting", "xgboost", "gru", "lstm", "cnn"])
    parser.add_argument("--max-rul", type=int, default=130)
    parser.add_argument("--window-size", type=int, default=30)
    parser.add_argument("--stride", type=int, default=1)
    parser.add_argument("--validation-fraction", type=float, default=0.2)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--n-jobs", type=int, default=1)
    parser.add_argument("--rf-n-estimators", type=int, default=300)
    parser.add_argument("--gb-n-estimators", type=int, default=300)
    parser.add_argument("--noise-levels", nargs="+", type=float, default=[0.05, 0.1, 0.2])
    parser.add_argument("--mask-fractions", nargs="+", type=float, default=[0.1, 0.2, 0.3])
    parser.add_argument("--important-indices", nargs="*", type=int, default=[])
    parser.add_argument("--epochs", type=int, default=100)
    parser.add_argument("--batch-size", type=int, default=128)
    parser.add_argument("--learning-rate", type=float, default=1e-3)
    parser.add_argument("--patience", type=int, default=10)
    parser.add_argument("--hidden-size", type=int, default=64)
    parser.add_argument("--num-layers", type=int, default=1)
    parser.add_argument("--dropout", type=float, default=0.2)
    parser.add_argument("--loss", choices=["mse", "critical_mse", "asymmetric_mse", "safety_mse"], default="mse")
    parser.add_argument("--device", default=None)
    return parser.parse_args()


if __name__ == "__main__":
    run(parse_args())
