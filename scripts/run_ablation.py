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
    parser = argparse.ArgumentParser(description="Run planned FD001/FD003 ablations.")
    parser.add_argument("--data-dir", default="data/raw")
    parser.add_argument("--out-root", default="reports/tables/ablations")
    parser.add_argument("--deep-epochs", type=int, default=40)
    parser.add_argument("--deep-models", nargs="+", default=["lstm", "gru", "cnn"], choices=["lstm", "gru", "cnn"])
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--skip-existing", action="store_true")
    parser.add_argument("--skip-deep", action="store_true")
    args = parser.parse_args()

    project_root = Path(__file__).resolve().parents[1]
    out_root = Path(args.out_root)
    if not out_root.is_absolute():
        out_root = project_root / out_root

    jobs = []
    for window_size in [20, 30, 50]:
        jobs.append({"subset": "FD001", "max_rul": 130, "window_size": window_size, "name": f"window_{window_size}"})
    for max_rul in [100, 130]:
        jobs.append({"subset": "FD001", "max_rul": max_rul, "window_size": 30, "name": f"maxrul_{max_rul}"})
    for subset in ["FD001", "FD003"]:
        jobs.append({"subset": subset, "max_rul": 130, "window_size": 30, "name": f"subset_{subset}"})

    for job in jobs:
        ml_out = out_root / job["name"] / "ml"
        run_command(
            [
                sys.executable,
                "-m",
                "rul_prediction.train_ml",
                "--data-dir",
                args.data_dir,
                "--subset",
                job["subset"],
                "--out-dir",
                str(ml_out),
                "--max-rul",
                str(job["max_rul"]),
                "--window-size",
                str(job["window_size"]),
                "--seed",
                str(args.seed),
            ],
            project_root,
            ml_out / "metrics.csv" if args.skip_existing else None,
        )
        if not args.skip_deep:
            deep_out = out_root / job["name"] / "deep"
            run_command(
                [
                    sys.executable,
                    "-m",
                    "rul_prediction.train_deep",
                    "--data-dir",
                    args.data_dir,
                    "--subset",
                    job["subset"],
                    "--out-dir",
                    str(deep_out),
                    "--models",
                    *args.deep_models,
                    "--epochs",
                    str(args.deep_epochs),
                    "--max-rul",
                    str(job["max_rul"]),
                    "--window-size",
                    str(job["window_size"]),
                    "--seed",
                    str(args.seed),
                ],
                project_root,
                deep_out / "metrics.csv" if args.skip_existing else None,
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
