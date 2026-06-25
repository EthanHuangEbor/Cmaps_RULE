from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd
import torch

from rul_prediction.domain_shift import prepare_domain_windows
from rul_prediction.features import window_summary_features
from rul_prediction.metrics import regression_report
from rul_prediction.models_deep import predict, train_model
from rul_prediction.train_ml import build_models


def run(args: argparse.Namespace) -> None:
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    windows = prepare_domain_windows(
        args.data_dir,
        source_subset=args.source_subset,
        target_subset=args.target_subset,
        max_rul=args.max_rul,
        window_size=args.window_size,
        stride=args.stride,
        validation_fraction=args.validation_fraction,
        seed=args.seed,
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
        train_features = window_summary_features(windows.x_source_train, windows.feature_columns)
        source_features = window_summary_features(windows.x_source_test, windows.feature_columns)
        target_features = window_summary_features(windows.x_target_test, windows.feature_columns)
        model.fit(train_features, windows.y_source_train)
        source_pred = model.predict(source_features)
        target_pred = model.predict(target_features)
    else:
        device = args.device or ("cuda" if torch.cuda.is_available() else "cpu")
        result = train_model(
            model_name,
            windows.x_source_train,
            windows.y_source_train,
            windows.x_source_validation,
            windows.y_source_validation,
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
        source_pred = predict(result.model, windows.x_source_test, torch.device(device), args.batch_size)
        target_pred = predict(result.model, windows.x_target_test, torch.device(device), args.batch_size)

    metrics = []
    for split, subset, y_true, y_pred in [
        ("source_test", args.source_subset, windows.y_source_test, source_pred),
        ("target_test", args.target_subset, windows.y_target_test, target_pred),
    ]:
        metrics.append(
            {
                "source_subset": args.source_subset,
                "target_subset": args.target_subset,
                "evaluated_subset": subset,
                "split": split,
                "model": model_name,
                "seed": args.seed,
                "window_size": args.window_size,
                "max_rul": args.max_rul,
                **regression_report(y_true, y_pred),
            }
        )
    pd.DataFrame(metrics).to_csv(out_dir / "metrics.csv", index=False)
    pd.DataFrame(
        {
            "source_subset": args.source_subset,
            "target_subset": args.target_subset,
            "model": model_name,
            "seed": args.seed,
            "window_size": args.window_size,
            "max_rul": args.max_rul,
            "unit": windows.target_units,
            "cycle": windows.target_cycles,
            "y_true": windows.y_target_test,
            "y_pred": target_pred,
            "error": target_pred - windows.y_target_test,
        }
    ).to_csv(out_dir / "target_predictions.csv", index=False)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run source-to-target C-MAPSS domain-shift stress tests.")
    parser.add_argument("--data-dir", default="data/raw")
    parser.add_argument("--source-subset", default="FD001")
    parser.add_argument("--target-subset", default="FD003")
    parser.add_argument("--out-dir", default="reports/tables/domain_shift")
    parser.add_argument("--model", default="gradient_boosting", choices=["ridge", "random_forest", "gradient_boosting", "xgboost", "gru", "lstm", "cnn"])
    parser.add_argument("--max-rul", type=int, default=130)
    parser.add_argument("--window-size", type=int, default=30)
    parser.add_argument("--stride", type=int, default=1)
    parser.add_argument("--validation-fraction", type=float, default=0.2)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--n-jobs", type=int, default=1)
    parser.add_argument("--rf-n-estimators", type=int, default=300)
    parser.add_argument("--gb-n-estimators", type=int, default=300)
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
