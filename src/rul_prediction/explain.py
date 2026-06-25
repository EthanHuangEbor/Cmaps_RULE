from __future__ import annotations

import argparse
from pathlib import Path

import joblib
import pandas as pd


def export_feature_importance(model_path: str | Path, feature_path: str | Path, out_path: str | Path) -> None:
    model = joblib.load(model_path)
    feature_names = pd.read_csv(feature_path)
    if "feature" not in feature_names.columns:
        raise ValueError("feature_path must contain a 'feature' column.")
    if not hasattr(model, "feature_importances_"):
        raise ValueError(f"Model does not expose feature_importances_: {model_path}")
    values = getattr(model, "feature_importances_")
    if len(values) != len(feature_names):
        raise ValueError(
            "Feature importance length does not match feature file length. "
            "Use train_ml.py's tabular_features.csv for tree models."
        )
    output = pd.DataFrame({"feature": feature_names["feature"], "importance": values})
    output.sort_values("importance", ascending=False).to_csv(out_path, index=False)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Export feature importance for tree-based models.")
    parser.add_argument("--model", required=True)
    parser.add_argument("--features", required=True)
    parser.add_argument("--out", required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    export_feature_importance(args.model, args.features, args.out)


if __name__ == "__main__":
    main()
