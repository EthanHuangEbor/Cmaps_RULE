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


def predefined_jobs() -> list[dict[str, str | int]]:
    base = {
        "learning_rate": "0.001",
        "hidden_size": "64",
        "num_layers": "1",
        "dropout": "0.2",
        "scheduler": "none",
        "critical_weight": "2",
        "over_weight": "2",
    }
    return [
        {**base, "name": "baseline_lr1e-3_h64_l1_w30", "window_size": 30, "loss": "mse"},
        {**base, "name": "lr5e-4_h64_l1_w30", "window_size": 30, "learning_rate": "0.0005", "loss": "mse"},
        {**base, "name": "plateau_lr1e-3_h64_l1_w30", "window_size": 30, "scheduler": "reduce_on_plateau", "loss": "mse"},
        {**base, "name": "capacity_h128_l1_w30", "window_size": 30, "hidden_size": "128", "loss": "mse"},
        {**base, "name": "capacity_h64_l2_d03_w30", "window_size": 30, "num_layers": "2", "dropout": "0.3", "loss": "mse"},
        {**base, "name": "window20_h64_l1", "window_size": 20, "loss": "mse"},
        {**base, "name": "window50_h64_l1", "window_size": 50, "loss": "mse"},
        {**base, "name": "critical_w2_h64_l1_w30", "window_size": 30, "loss": "critical_mse", "critical_weight": "2"},
        {**base, "name": "critical_w3_h64_l1_w30", "window_size": 30, "loss": "critical_mse", "critical_weight": "3"},
        {**base, "name": "asymmetric_w2_h64_l1_w30", "window_size": 30, "loss": "asymmetric_mse", "over_weight": "2"},
        {**base, "name": "asymmetric_w3_h64_l1_w30", "window_size": 30, "loss": "asymmetric_mse", "over_weight": "3"},
        {**base, "name": "safety_w1p5_h64_l1_w30", "window_size": 30, "loss": "safety_mse", "critical_weight": "1.5", "over_weight": "1.5"},
        {**base, "name": "safety_w2_h64_l1_w30", "window_size": 30, "loss": "safety_mse", "critical_weight": "2", "over_weight": "2"},
        {**base, "name": "safety_w3_h64_l1_w30", "window_size": 30, "loss": "safety_mse", "critical_weight": "3", "over_weight": "3"},
        {**base, "name": "safety_plateau_w2_h64_l1_w30", "window_size": 30, "scheduler": "reduce_on_plateau", "loss": "safety_mse"},
    ]


def main() -> None:
    parser = argparse.ArgumentParser(description="Run focused deep-model ablations for C-MAPSS RUL.")
    parser.add_argument("--data-dir", default="data/raw")
    parser.add_argument("--out-root", default="reports/tables/deep_ablations")
    parser.add_argument("--subsets", nargs="+", default=["FD001", "FD003"])
    parser.add_argument("--seeds", nargs="+", type=int, default=[42])
    parser.add_argument("--epochs", type=int, default=60)
    parser.add_argument("--patience", type=int, default=8)
    parser.add_argument("--models", nargs="+", default=["gru"], choices=["lstm", "gru", "cnn"])
    parser.add_argument(
        "--jobs",
        nargs="+",
        default=None,
        help="Optional subset of ablation job names to run. By default all predefined jobs are run.",
    )
    parser.add_argument("--skip-existing", action="store_true")
    args = parser.parse_args()

    project_root = Path(__file__).resolve().parents[1]
    out_root = Path(args.out_root)
    if not out_root.is_absolute():
        out_root = project_root / out_root

    jobs = predefined_jobs()
    if args.jobs is not None:
        requested_jobs = set(args.jobs)
        available_jobs = {str(job["name"]) for job in jobs}
        unknown_jobs = sorted(requested_jobs - available_jobs)
        if unknown_jobs:
            raise ValueError(f"Unknown job names: {', '.join(unknown_jobs)}")
        jobs = [job for job in jobs if job["name"] in requested_jobs]

    for subset in args.subsets:
        for seed in args.seeds:
            for job in jobs:
                out_dir = out_root / subset.lower() / f"seed_{seed}" / str(job["name"])
                command = [
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
                    *args.models,
                    "--seed",
                    str(seed),
                    "--epochs",
                    str(args.epochs),
                    "--patience",
                    str(args.patience),
                    "--window-size",
                    str(job["window_size"]),
                    "--learning-rate",
                    str(job["learning_rate"]),
                    "--hidden-size",
                    str(job["hidden_size"]),
                    "--num-layers",
                    str(job["num_layers"]),
                    "--dropout",
                    str(job["dropout"]),
                    "--scheduler",
                    str(job["scheduler"]),
                    "--loss",
                    str(job["loss"]),
                    "--critical-weight",
                    str(job["critical_weight"]),
                    "--over-weight",
                    str(job["over_weight"]),
                ]
                run_command(command, project_root, out_dir / "metrics.csv" if args.skip_existing else None)

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
