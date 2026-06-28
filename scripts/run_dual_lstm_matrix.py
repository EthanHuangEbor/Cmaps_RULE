from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


def run_command(command: list[str], cwd: Path, skip_existing: Path | None = None) -> None:
    if skip_existing is not None and skip_existing.exists():
        print(f"[skip] {skip_existing}")
        return
    print("[run]", " ".join(command))
    subprocess.run(command, cwd=cwd, check=True)


def predefined_jobs() -> list[dict[str, str | float | int]]:
    return [
        {
            "name": "lstm_baseline_h64_l1_w30",
            "kind": "baseline",
            "model_name": "lstm",
            "loss": "mse",
            "lambda_cycle": 0.0,
            "lambda_latent": 0.0,
            "lambda_mono": 0.0,
            "critical_weight": 2.0,
            "over_weight": 2.0,
        },
        {
            "name": "dual_no_cycle_h64_l1_w30",
            "kind": "dual",
            "model_name": "Dual-LSTM-no-cycle",
            "loss": "mse",
            "lambda_cycle": 0.0,
            "lambda_latent": 0.0,
            "lambda_mono": 0.0,
            "critical_weight": 2.0,
            "over_weight": 2.0,
        },
        {
            "name": "dual_cycle_h64_l1_w30",
            "kind": "dual",
            "model_name": "Dual-LSTM-cycle",
            "loss": "mse",
            "lambda_cycle": 1.0,
            "lambda_latent": 0.25,
            "lambda_mono": 0.1,
            "critical_weight": 2.0,
            "over_weight": 2.0,
        },
        {
            "name": "dual_cycle_safety_w2_h64_l1_w30",
            "kind": "dual",
            "model_name": "Dual-LSTM-cycle-safety-w2",
            "loss": "safety_mse",
            "lambda_cycle": 1.0,
            "lambda_latent": 0.25,
            "lambda_mono": 0.1,
            "critical_weight": 2.0,
            "over_weight": 2.0,
        },
    ]


def dual_command(args: argparse.Namespace, job: dict[str, str | float | int], out_dir: Path, subset: str, seed: int) -> list[str]:
    if job["kind"] == "baseline":
        return [
            sys.executable,
            "-m",
            "rul_prediction.train_deep",
            "--data-dir",
            args.data_dir,
            "--subset",
            subset,
            "--out-dir",
            str(out_dir),
            "--job-name",
            str(job["name"]),
            "--models",
            "lstm",
            "--seed",
            str(seed),
            "--epochs",
            str(args.epochs),
            "--patience",
            str(args.patience),
            "--window-size",
            str(args.window_size),
            "--learning-rate",
            str(args.learning_rate),
            "--hidden-size",
            str(args.hidden_size),
            "--num-layers",
            str(args.num_layers),
            "--dropout",
            str(args.dropout),
            "--loss",
            str(job["loss"]),
        ]
    return [
        sys.executable,
        "-m",
        "rul_prediction.train_dual_lstm",
        "--data-dir",
        args.data_dir,
        "--subset",
        subset,
        "--out-dir",
        str(out_dir),
        "--job-name",
        str(job["name"]),
        "--model-name",
        str(job["model_name"]),
        "--seed",
        str(seed),
        "--epochs",
        str(args.epochs),
        "--patience",
        str(args.patience),
        "--window-size",
        str(args.window_size),
        "--pair-horizon",
        str(args.pair_horizon),
        "--learning-rate",
        str(args.learning_rate),
        "--hidden-size",
        str(args.hidden_size),
        "--num-layers",
        str(args.num_layers),
        "--dropout",
        str(args.dropout),
        "--loss",
        str(job["loss"]),
        "--critical-weight",
        str(job["critical_weight"]),
        "--over-weight",
        str(job["over_weight"]),
        "--lambda-cycle",
        str(job["lambda_cycle"]),
        "--lambda-latent",
        str(job["lambda_latent"]),
        "--lambda-mono",
        str(job["lambda_mono"]),
    ]


def main() -> None:
    parser = argparse.ArgumentParser(description="Run Dual-LSTM prototype and validation jobs for C-MAPSS RUL.")
    parser.add_argument("--data-dir", default="data/raw")
    parser.add_argument("--out-root", default="reports/tables/dual_lstm")
    parser.add_argument("--subsets", nargs="+", default=["FD001"])
    parser.add_argument("--seeds", nargs="+", type=int, default=[42])
    parser.add_argument("--jobs", nargs="+", default=None)
    parser.add_argument("--epochs", type=int, default=30)
    parser.add_argument("--patience", type=int, default=5)
    parser.add_argument("--window-size", type=int, default=30)
    parser.add_argument("--pair-horizon", type=int, default=1)
    parser.add_argument("--learning-rate", type=float, default=1e-3)
    parser.add_argument("--hidden-size", type=int, default=64)
    parser.add_argument("--num-layers", type=int, default=1)
    parser.add_argument("--dropout", type=float, default=0.2)
    parser.add_argument("--skip-existing", action="store_true")
    args = parser.parse_args()

    project_root = Path(__file__).resolve().parents[1]
    out_root = Path(args.out_root)
    if not out_root.is_absolute():
        out_root = project_root / out_root

    jobs = predefined_jobs()
    if args.jobs is not None:
        requested = set(args.jobs)
        available = {str(job["name"]) for job in jobs}
        unknown = sorted(requested - available)
        if unknown:
            raise ValueError(f"Unknown job names: {', '.join(unknown)}")
        jobs = [job for job in jobs if str(job["name"]) in requested]

    for subset in args.subsets:
        for seed in args.seeds:
            for job in jobs:
                out_dir = out_root / subset.lower() / f"seed_{seed}" / str(job["name"])
                run_command(
                    dual_command(args, job, out_dir, subset, seed),
                    project_root,
                    out_dir / "metrics.csv" if args.skip_existing else None,
                )

    run_command(
        [
            sys.executable,
            "-m",
            "rul_prediction.aggregate",
            "--root",
            str(out_root),
            "--out-dir",
            str(out_root / "summary"),
        ],
        project_root,
    )
    run_command(
        [
            sys.executable,
            "-m",
            "rul_prediction.error_analysis",
            "--root",
            str(out_root),
            "--out-dir",
            str(out_root / "summary"),
        ],
        project_root,
    )


if __name__ == "__main__":
    main()
