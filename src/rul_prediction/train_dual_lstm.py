from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd
import torch

from rul_prediction import data
from rul_prediction.metrics import regression_report
from rul_prediction.models_dual_lstm import predict_current, train_dual_lstm_model


def run(args: argparse.Namespace) -> None:
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    model_dir = out_dir / "models"
    model_dir.mkdir(parents=True, exist_ok=True)

    prepared = data.prepare_data(
        args.data_dir,
        subset=args.subset,
        max_rul=args.max_rul,
        validation_fraction=args.validation_fraction,
        seed=args.seed,
    )
    train_pairs = data.make_paired_sequence_windows(
        prepared.train,
        prepared.feature_columns,
        window_size=args.window_size,
        stride=args.stride,
        pair_horizon=args.pair_horizon,
    )
    validation_pairs = data.make_paired_sequence_windows(
        prepared.validation,
        prepared.feature_columns,
        window_size=args.window_size,
        stride=args.stride,
        pair_horizon=args.pair_horizon,
    )
    x_validation, y_validation, _, _ = data.make_sequence_windows(
        prepared.validation, prepared.feature_columns, args.window_size, args.stride
    )
    x_test, y_test, test_units, test_cycles = data.make_last_windows(
        prepared.test, prepared.feature_columns, args.window_size
    )

    torch_device = args.device or ("cuda" if torch.cuda.is_available() else "cpu")
    result = train_dual_lstm_model(
        train_pairs,
        validation_pairs,
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
        lambda_cycle=args.lambda_cycle,
        lambda_latent=args.lambda_latent,
        lambda_mono=args.lambda_mono,
    )
    model_name = args.model_name
    torch.save(result.model.state_dict(), model_dir / f"{model_name}_seed{args.seed}.pt")

    validation_pred = predict_current(result.model, x_validation, torch.device(torch_device), args.batch_size)
    test_pred = predict_current(result.model, x_test, torch.device(torch_device), args.batch_size)

    common = {
        "subset": args.subset,
        "model": model_name,
        "job_name": args.job_name,
        "seed": args.seed,
        "window_size": args.window_size,
        "max_rul": args.max_rul,
        "hidden_size": args.hidden_size,
        "num_layers": args.num_layers,
        "dropout": args.dropout,
        "learning_rate": args.learning_rate,
        "scheduler": "none",
        "loss": args.loss,
        "critical_threshold": args.critical_threshold,
        "critical_weight": args.critical_weight,
        "over_weight": args.over_weight,
        "pair_horizon": args.pair_horizon,
        "lambda_cycle": args.lambda_cycle,
        "lambda_latent": args.lambda_latent,
        "lambda_mono": args.lambda_mono,
    }
    metrics_rows: list[dict[str, object]] = []
    for split, y_true, y_pred in [
        ("validation", y_validation, validation_pred),
        ("test", y_test, test_pred),
    ]:
        metrics_rows.append({**common, "split": split, **regression_report(y_true, y_pred)})

    predictions = pd.DataFrame(
        {
            **common,
            "unit": test_units,
            "cycle": test_cycles,
            "y_true": y_test,
            "y_pred": test_pred,
            "error": test_pred - y_test,
        }
    )
    history = pd.DataFrame(result.history)
    history["model"] = model_name
    history["job_name"] = args.job_name
    history["seed"] = args.seed
    history["loss"] = args.loss
    history["hidden_size"] = args.hidden_size
    history["num_layers"] = args.num_layers
    history["dropout"] = args.dropout
    history["pair_horizon"] = args.pair_horizon
    history["lambda_cycle"] = args.lambda_cycle
    history["lambda_latent"] = args.lambda_latent
    history["lambda_mono"] = args.lambda_mono

    pd.DataFrame(metrics_rows).to_csv(out_dir / "metrics.csv", index=False)
    predictions.to_csv(out_dir / "predictions.csv", index=False)
    history.to_csv(out_dir / "training_history.csv", index=False)
    pd.DataFrame({"feature": prepared.feature_columns}).to_csv(out_dir / "selected_features.csv", index=False)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Train cycle-consistent Dual-LSTM models for C-MAPSS RUL.")
    parser.add_argument("--data-dir", default="data/raw")
    parser.add_argument("--subset", default="FD001")
    parser.add_argument("--out-dir", default="reports/tables/dual_lstm/fd001/seed_42/dual_cycle")
    parser.add_argument("--job-name", default="dual_cycle")
    parser.add_argument("--model-name", default="Dual-LSTM")
    parser.add_argument("--max-rul", type=int, default=130)
    parser.add_argument("--window-size", type=int, default=30)
    parser.add_argument("--stride", type=int, default=1)
    parser.add_argument("--pair-horizon", type=int, default=1)
    parser.add_argument("--validation-fraction", type=float, default=0.2)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--epochs", type=int, default=30)
    parser.add_argument("--batch-size", type=int, default=128)
    parser.add_argument("--learning-rate", type=float, default=1e-3)
    parser.add_argument("--patience", type=int, default=5)
    parser.add_argument("--hidden-size", type=int, default=64)
    parser.add_argument("--num-layers", type=int, default=1)
    parser.add_argument("--dropout", type=float, default=0.2)
    parser.add_argument("--device", default=None)
    parser.add_argument("--loss", default="mse", choices=["mse", "critical_mse", "asymmetric_mse", "safety_mse"])
    parser.add_argument("--critical-threshold", type=float, default=50.0)
    parser.add_argument("--critical-weight", type=float, default=2.0)
    parser.add_argument("--over-weight", type=float, default=2.0)
    parser.add_argument("--lambda-cycle", type=float, default=1.0)
    parser.add_argument("--lambda-latent", type=float, default=0.25)
    parser.add_argument("--lambda-mono", type=float, default=0.1)
    return parser.parse_args()


def main() -> None:
    run(parse_args())


if __name__ == "__main__":
    main()
