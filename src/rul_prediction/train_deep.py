from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd
import torch

from rul_prediction import data
from rul_prediction.metrics import regression_report
from rul_prediction.models_deep import predict, train_model


def display_model_name(model_name: str, loss_type: str) -> str:
    return model_name if loss_type == "mse" else f"{model_name}_{loss_type}"


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
    x_train, y_train, _, _ = data.make_sequence_windows(
        prepared.train, prepared.feature_columns, args.window_size, args.stride
    )
    x_validation, y_validation, _, _ = data.make_sequence_windows(
        prepared.validation, prepared.feature_columns, args.window_size, args.stride
    )
    x_test, y_test, test_units, test_cycles = data.make_last_windows(
        prepared.test, prepared.feature_columns, args.window_size
    )

    metrics_rows: list[dict[str, object]] = []
    predictions_rows: list[pd.DataFrame] = []
    history_rows: list[pd.DataFrame] = []
    torch_device = args.device or ("cuda" if torch.cuda.is_available() else "cpu")

    for model_name in args.models:
        reported_model = display_model_name(model_name, args.loss)
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
            device=torch_device,
            num_layers=args.num_layers,
            loss_type=args.loss,
            critical_threshold=args.critical_threshold,
            critical_weight=args.critical_weight,
            over_weight=args.over_weight,
            scheduler=args.scheduler,
            scheduler_factor=args.scheduler_factor,
            scheduler_patience=args.scheduler_patience,
            min_learning_rate=args.min_learning_rate,
        )
        torch.save(result.model.state_dict(), model_dir / f"{reported_model}_seed{args.seed}.pt")

        validation_pred = predict(result.model, x_validation, torch.device(torch_device), args.batch_size)
        test_pred = predict(result.model, x_test, torch.device(torch_device), args.batch_size)

        for split, y_true, y_pred in [
            ("validation", y_validation, validation_pred),
            ("test", y_test, test_pred),
        ]:
            metrics_rows.append(
                {
                    "subset": args.subset,
                    "split": split,
                    "model": reported_model,
                    "job_name": args.job_name,
                    "seed": args.seed,
                    "window_size": args.window_size,
                    "max_rul": args.max_rul,
                    "hidden_size": args.hidden_size,
                    "num_layers": args.num_layers,
                    "dropout": args.dropout,
                    "learning_rate": args.learning_rate,
                    "scheduler": args.scheduler,
                    "loss": args.loss,
                    "critical_threshold": args.critical_threshold,
                    "critical_weight": args.critical_weight,
                    "over_weight": args.over_weight,
                    **regression_report(y_true, y_pred),
                }
            )

        predictions_rows.append(
            pd.DataFrame(
                {
                    "subset": args.subset,
                    "model": reported_model,
                    "job_name": args.job_name,
                    "seed": args.seed,
                    "window_size": args.window_size,
                    "max_rul": args.max_rul,
                    "hidden_size": args.hidden_size,
                    "num_layers": args.num_layers,
                    "dropout": args.dropout,
                    "learning_rate": args.learning_rate,
                    "scheduler": args.scheduler,
                    "loss": args.loss,
                    "critical_threshold": args.critical_threshold,
                    "critical_weight": args.critical_weight,
                    "over_weight": args.over_weight,
                    "unit": test_units,
                    "cycle": test_cycles,
                    "y_true": y_test,
                    "y_pred": test_pred,
                    "error": test_pred - y_test,
                }
            )
        )
        history_df = pd.DataFrame(result.history)
        history_df["model"] = reported_model
        history_df["job_name"] = args.job_name
        history_df["seed"] = args.seed
        history_df["loss"] = args.loss
        history_df["hidden_size"] = args.hidden_size
        history_df["num_layers"] = args.num_layers
        history_df["dropout"] = args.dropout
        history_df["scheduler"] = args.scheduler
        history_rows.append(history_df)

    pd.DataFrame(metrics_rows).to_csv(out_dir / "metrics.csv", index=False)
    pd.concat(predictions_rows, ignore_index=True).to_csv(out_dir / "predictions.csv", index=False)
    pd.concat(history_rows, ignore_index=True).to_csv(out_dir / "training_history.csv", index=False)
    pd.DataFrame({"feature": prepared.feature_columns}).to_csv(out_dir / "selected_features.csv", index=False)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Train deep sequence models for C-MAPSS RUL.")
    parser.add_argument("--data-dir", default="data/raw")
    parser.add_argument("--subset", default="FD001")
    parser.add_argument("--out-dir", default="reports/tables/fd001_deep")
    parser.add_argument("--job-name", default="", help="Optional experiment/job label for aggregation and traceability.")
    parser.add_argument("--models", nargs="+", default=["lstm", "gru", "cnn"], choices=["lstm", "gru", "cnn", "tcn", "mlp"])
    parser.add_argument("--max-rul", type=int, default=130)
    parser.add_argument("--window-size", type=int, default=30)
    parser.add_argument("--stride", type=int, default=1)
    parser.add_argument("--validation-fraction", type=float, default=0.2)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--epochs", type=int, default=100)
    parser.add_argument("--batch-size", type=int, default=128)
    parser.add_argument("--learning-rate", type=float, default=1e-3)
    parser.add_argument("--patience", type=int, default=10)
    parser.add_argument("--hidden-size", type=int, default=64)
    parser.add_argument("--num-layers", type=int, default=1)
    parser.add_argument("--dropout", type=float, default=0.2)
    parser.add_argument("--device", default=None)
    parser.add_argument("--scheduler", default="none", choices=["none", "reduce_on_plateau"])
    parser.add_argument("--scheduler-factor", type=float, default=0.5)
    parser.add_argument("--scheduler-patience", type=int, default=4)
    parser.add_argument("--min-learning-rate", type=float, default=1e-5)
    parser.add_argument(
        "--loss",
        default="mse",
        choices=["mse", "critical_mse", "asymmetric_mse", "safety_mse"],
        help="Training loss. Safety-aware losses are intended for neural follow-up experiments and should be interpreted as risk-profile shaping, not certification evidence.",
    )
    parser.add_argument("--critical-threshold", type=float, default=50.0)
    parser.add_argument("--critical-weight", type=float, default=2.0)
    parser.add_argument("--over-weight", type=float, default=2.0)
    return parser.parse_args()


def main() -> None:
    run(parse_args())


if __name__ == "__main__":
    main()
