from __future__ import annotations

import argparse
from pathlib import Path

import joblib
import pandas as pd
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.linear_model import Ridge

from rul_prediction import data
from rul_prediction.features import window_summary_features
from rul_prediction.metrics import regression_report


def build_models(seed: int, n_jobs: int = 1) -> dict[str, object]:
    models: dict[str, object] = {
        "ridge": Ridge(alpha=1.0),
        "random_forest": RandomForestRegressor(
            n_estimators=300,
            random_state=seed,
            n_jobs=n_jobs,
            min_samples_leaf=2,
        ),
        "gradient_boosting": GradientBoostingRegressor(
            n_estimators=300,
            learning_rate=0.05,
            max_depth=3,
            random_state=seed,
        ),
    }
    try:
        from xgboost import XGBRegressor

        models["xgboost"] = XGBRegressor(
            n_estimators=500,
            max_depth=4,
            learning_rate=0.03,
            subsample=0.8,
            colsample_bytree=0.8,
            objective="reg:squarederror",
            random_state=seed,
            n_jobs=n_jobs,
        )
    except Exception:
        pass
    return models


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

    train_features = window_summary_features(x_train, prepared.feature_columns)
    validation_features = window_summary_features(x_validation, prepared.feature_columns)
    test_features = window_summary_features(x_test, prepared.feature_columns)

    metrics_rows: list[dict[str, object]] = []
    predictions_rows: list[pd.DataFrame] = []
    models = build_models(args.seed, n_jobs=args.n_jobs)

    for model_name, model in models.items():
        model.fit(train_features, y_train)
        joblib.dump(model, out_dir / f"{model_name}.joblib")

        for split, features, y_true, units, cycles in [
            ("validation", validation_features, y_validation, None, None),
            ("test", test_features, y_test, test_units, test_cycles),
        ]:
            y_pred = model.predict(features)
            report = regression_report(y_true, y_pred)
            metrics_rows.append(
                {
                    "subset": args.subset,
                    "split": split,
                    "model": model_name,
                    "window_size": args.window_size,
                    "max_rul": args.max_rul,
                    **report,
                }
            )
            if split == "test":
                predictions_rows.append(
                    pd.DataFrame(
                        {
                            "subset": args.subset,
                            "model": model_name,
                            "unit": units,
                            "cycle": cycles,
                            "y_true": y_true,
                            "y_pred": y_pred,
                            "error": y_pred - y_true,
                        }
                    )
                )

    pd.DataFrame(metrics_rows).to_csv(out_dir / "metrics.csv", index=False)
    pd.concat(predictions_rows, ignore_index=True).to_csv(out_dir / "predictions.csv", index=False)
    pd.DataFrame({"feature": prepared.feature_columns}).to_csv(out_dir / "selected_features.csv", index=False)
    pd.DataFrame({"feature": train_features.columns}).to_csv(out_dir / "tabular_features.csv", index=False)
    pd.DataFrame({"dropped_feature": prepared.dropped_columns}).to_csv(
        out_dir / "dropped_features.csv", index=False
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Train traditional ML baselines for C-MAPSS RUL.")
    parser.add_argument("--data-dir", default="data/raw")
    parser.add_argument("--subset", default="FD001")
    parser.add_argument("--out-dir", default="reports/tables/fd001_ml")
    parser.add_argument("--max-rul", type=int, default=130)
    parser.add_argument("--window-size", type=int, default=30)
    parser.add_argument("--stride", type=int, default=1)
    parser.add_argument("--validation-fraction", type=float, default=0.2)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--n-jobs", type=int, default=1, help="Parallel workers for supported ML models.")
    return parser.parse_args()


def main() -> None:
    run(parse_args())


if __name__ == "__main__":
    main()
