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


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the planned C-MAPSS research experiment matrix.")
    parser.add_argument("--data-dir", default="data/raw")
    parser.add_argument("--out-root", default="reports/tables/matrix")
    parser.add_argument("--subsets", nargs="+", default=["FD001", "FD003"])
    parser.add_argument("--seeds", nargs="+", type=int, default=[42, 43, 44])
    parser.add_argument("--window-size", type=int, default=30)
    parser.add_argument("--max-rul", type=int, default=130)
    parser.add_argument("--deep-models", nargs="+", default=["lstm", "gru", "cnn"], choices=["lstm", "gru", "cnn", "tcn", "mlp"])
    parser.add_argument("--deep-epochs", type=int, default=60)
    parser.add_argument("--deep-hidden-size", type=int, default=64)
    parser.add_argument("--deep-num-layers", type=int, default=1)
    parser.add_argument("--deep-dropout", type=float, default=0.2)
    parser.add_argument("--device", default=None, help="Torch device for deep models, e.g. cuda or cpu.")
    parser.add_argument("--patience", type=int, default=8)
    parser.add_argument("--n-jobs", type=int, default=4)
    parser.add_argument("--skip-existing", action="store_true")
    parser.add_argument("--skip-ml", action="store_true")
    parser.add_argument("--skip-deep", action="store_true")
    parser.add_argument("--skip-safety", action="store_true")
    args = parser.parse_args()

    project_root = Path(__file__).resolve().parents[1]
    out_root = Path(args.out_root)
    if not out_root.is_absolute():
        out_root = project_root / out_root

    for subset in args.subsets:
        for seed in args.seeds:
            base_out = out_root / subset.lower() / f"seed_{seed}"
            if not args.skip_ml:
                ml_out = base_out / "ml"
                run_command(
                    [
                        sys.executable,
                        "-m",
                        "rul_prediction.train_ml",
                        "--data-dir",
                        args.data_dir,
                        "--subset",
                        subset,
                        "--out-dir",
                        str(ml_out),
                        "--seed",
                        str(seed),
                        "--window-size",
                        str(args.window_size),
                        "--max-rul",
                        str(args.max_rul),
                        "--n-jobs",
                        str(args.n_jobs),
                    ],
                    project_root,
                    ml_out / "metrics.csv" if args.skip_existing else None,
                )
            if not args.skip_deep:
                deep_out = base_out / "deep"
                run_command(
                    [
                        sys.executable,
                        "-m",
                        "rul_prediction.train_deep",
                        "--data-dir",
                        args.data_dir,
                        "--subset",
                        subset,
                        "--out-dir",
                        str(deep_out),
                        "--job-name",
                        f"deep_default_w{args.window_size}",
                        "--models",
                        *args.deep_models,
                        "--seed",
                        str(seed),
                        "--epochs",
                        str(args.deep_epochs),
                        "--patience",
                        str(args.patience),
                        "--window-size",
                        str(args.window_size),
                        "--max-rul",
                        str(args.max_rul),
                        "--hidden-size",
                        str(args.deep_hidden_size),
                        "--num-layers",
                        str(args.deep_num_layers),
                        "--dropout",
                        str(args.deep_dropout),
                        *(["--device", args.device] if args.device else []),
                    ],
                    project_root,
                    deep_out / "metrics.csv" if args.skip_existing else None,
                )
            if not args.skip_safety:
                safety_out = base_out / "deep_safety_gru"
                run_command(
                    [
                        sys.executable,
                        "-m",
                        "rul_prediction.train_deep",
                        "--data-dir",
                        args.data_dir,
                        "--subset",
                        subset,
                        "--out-dir",
                        str(safety_out),
                        "--job-name",
                        f"safety_w2_h64_l1_w{args.window_size}",
                        "--models",
                        "gru",
                        "--loss",
                        "safety_mse",
                        "--critical-threshold",
                        "50",
                        "--critical-weight",
                        "2",
                        "--over-weight",
                        "2",
                        "--seed",
                        str(seed),
                        "--epochs",
                        str(args.deep_epochs),
                        "--patience",
                        str(args.patience),
                        "--window-size",
                        str(args.window_size),
                        "--max-rul",
                        str(args.max_rul),
                    ],
                    project_root,
                    safety_out / "metrics.csv" if args.skip_existing else None,
                )

    run_command(
        [
            sys.executable,
            "-m",
            "rul_prediction.aggregate",
            "--root",
            args.out_root,
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
            args.out_root,
            "--out-dir",
            str(out_root / "summary"),
        ],
        project_root,
    )


if __name__ == "__main__":
    main()
