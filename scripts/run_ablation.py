from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


def run_command(command: list[str], cwd: Path) -> None:
    print(" ".join(command))
    subprocess.run(command, cwd=cwd, check=True)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run planned FD001/FD003 ablations.")
    parser.add_argument("--data-dir", default="data/raw")
    parser.add_argument("--out-root", default="reports/tables/ablations")
    parser.add_argument("--deep-epochs", type=int, default=40)
    parser.add_argument("--skip-deep", action="store_true")
    args = parser.parse_args()

    project_root = Path(__file__).resolve().parents[1]
    out_root = Path(args.out_root)

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
            ],
            project_root,
        )
        if not args.skip_deep:
            deep_out = out_root / job["name"] / "deep_lstm"
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
                    "lstm",
                    "--epochs",
                    str(args.deep_epochs),
                    "--max-rul",
                    str(job["max_rul"]),
                    "--window-size",
                    str(job["window_size"]),
                ],
                project_root,
            )


if __name__ == "__main__":
    main()

