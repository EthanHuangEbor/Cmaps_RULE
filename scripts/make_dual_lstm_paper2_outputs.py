from __future__ import annotations

import argparse
from itertools import product
from pathlib import Path

import pandas as pd

METRICS = [
    "rmse",
    "mae",
    "nasa_s_score",
    "critical_rmse_30",
    "critical_rmse_50",
    "overestimation_ratio",
    "overestimation_magnitude",
]

JOB_ORDER = [
    "lstm_baseline_h64_l1_w30",
    "dual_no_cycle_h64_l1_w30",
    "dual_cycle_h64_l1_w30",
    "dual_cycle_safety_w2_h64_l1_w30",
]

JOB_LABELS = {
    "lstm_baseline_h64_l1_w30": "LSTM baseline",
    "dual_no_cycle_h64_l1_w30": "Dual-LSTM no-cycle",
    "dual_cycle_h64_l1_w30": "Dual-LSTM cycle",
    "dual_cycle_safety_w2_h64_l1_w30": "Dual-LSTM cycle safety-w2",
}

EXPECTED_SUBSETS = ["FD001", "FD002", "FD003", "FD004"]
EXPECTED_SEEDS = [42, 43, 44]
EXPECTED_SPLITS = ["validation", "test"]
REQUIRED_JOB_OUTPUTS = ["metrics.csv", "predictions.csv", "training_history.csv", "selected_features.csv"]


def expected_job_dirs(root: Path) -> dict[tuple[str, int, str], Path]:
    return {
        (subset, seed, job): root / subset.lower() / f"seed_{seed}" / job
        for subset, seed, job in product(EXPECTED_SUBSETS, EXPECTED_SEEDS, JOB_ORDER)
    }


def validate_job_artifacts(root: Path) -> list[Path]:
    expected_dirs = expected_job_dirs(root)
    missing_outputs: list[str] = []
    for (subset, seed, job), job_dir in expected_dirs.items():
        for output_name in REQUIRED_JOB_OUTPUTS:
            output_path = job_dir / output_name
            if not output_path.exists():
                missing_outputs.append(f"{subset}/seed_{seed}/{job}/{output_name}")
    if missing_outputs:
        preview = "; ".join(missing_outputs[:12])
        suffix = "" if len(missing_outputs) <= 12 else f"; ... {len(missing_outputs) - 12} more"
        raise FileNotFoundError(f"Incomplete Dual-LSTM job outputs: {preview}{suffix}")

    expected_metric_paths = {job_dir / "metrics.csv" for job_dir in expected_dirs.values()}
    actual_metric_paths = set(root.glob("*/*/*/metrics.csv"))
    extra_metric_paths = sorted(actual_metric_paths - expected_metric_paths)
    missing_metric_paths = sorted(expected_metric_paths - actual_metric_paths)
    if extra_metric_paths or missing_metric_paths:
        details: list[str] = []
        if missing_metric_paths:
            details.append("missing=" + ", ".join(str(path) for path in missing_metric_paths[:8]))
        if extra_metric_paths:
            details.append("extra=" + ", ".join(str(path) for path in extra_metric_paths[:8]))
        raise ValueError("Dual-LSTM metrics path set does not match the expected 48-job matrix: " + "; ".join(details))
    return sorted(expected_metric_paths)


def read_metrics(root: Path) -> pd.DataFrame:
    paths = validate_job_artifacts(root)
    frames = [pd.read_csv(path).assign(source_file=str(path)) for path in paths]
    metrics = pd.concat(frames, ignore_index=True)
    missing = [column for column in ["subset", "seed", "job_name", "split", *METRICS] if column not in metrics.columns]
    if missing:
        raise ValueError(f"Missing required metric columns: {', '.join(missing)}")
    metrics["job_label"] = metrics["job_name"].map(JOB_LABELS).fillna(metrics["job_name"])
    metrics["job_order"] = metrics["job_name"].map({name: index for index, name in enumerate(JOB_ORDER)}).fillna(999)
    return metrics


def validate_full_matrix(metrics: pd.DataFrame) -> pd.DataFrame:
    expected_keys = set(product(EXPECTED_SUBSETS, EXPECTED_SEEDS, JOB_ORDER, EXPECTED_SPLITS))
    observed_keys = set(
        metrics[["subset", "seed", "job_name", "split"]]
        .itertuples(index=False, name=None)
    )
    if observed_keys != expected_keys:
        missing = sorted(expected_keys - observed_keys)
        extra = sorted(observed_keys - expected_keys)
        details: list[str] = []
        if missing:
            details.append(f"missing={missing[:8]}")
        if extra:
            details.append(f"extra={extra[:8]}")
        raise ValueError("Dual-LSTM metric key set does not match FD001-FD004 x 3 seeds x 4 jobs x 2 splits: " + "; ".join(details))
    duplicates = metrics.duplicated(["subset", "seed", "job_name", "split"], keep=False)
    if duplicates.any():
        duplicate_rows = metrics.loc[duplicates, ["subset", "seed", "job_name", "split", "source_file"]]
        raise ValueError("Duplicate metric rows found:\n" + duplicate_rows.head(12).to_string(index=False))
    if len(metrics) != len(expected_keys):
        raise ValueError(f"Expected {len(expected_keys)} metric rows, found {len(metrics)}")
    test_metrics = metrics[metrics["split"].eq("test")].copy()
    if len(test_metrics) != len(EXPECTED_SUBSETS) * len(EXPECTED_SEEDS) * len(JOB_ORDER):
        raise ValueError(f"Expected 48 test rows, found {len(test_metrics)}")
    return test_metrics


def write_seed_metrics(test_metrics: pd.DataFrame, out_dir: Path) -> pd.DataFrame:
    columns = ["subset", "seed", "job_order", "job_name", "job_label", "model", *METRICS]
    seed_metrics = test_metrics[[column for column in columns if column in test_metrics.columns]].copy()
    seed_metrics = seed_metrics.sort_values(["subset", "seed", "job_order", "job_name"]).drop(columns=["job_order"], errors="ignore")
    seed_metrics.to_csv(out_dir / "dual_lstm_seed_metrics.csv", index=False)
    return seed_metrics


def write_summary(test_metrics: pd.DataFrame, out_dir: Path) -> pd.DataFrame:
    grouped = test_metrics.groupby(["subset", "job_name", "job_label", "model", "job_order"], dropna=False)[METRICS]
    summary = grouped.agg(["mean", "std"]).reset_index()
    summary.columns = ["_".join(str(part) for part in col if part != "") if isinstance(col, tuple) else str(col) for col in summary.columns]
    summary = summary.sort_values(["subset", "job_order", "job_name"]).drop(columns=["job_order"])
    summary.to_csv(out_dir / "dual_lstm_full_summary.csv", index=False)
    return summary


def write_rmse_vs_risk(test_metrics: pd.DataFrame, out_dir: Path) -> pd.DataFrame:
    means = test_metrics.groupby(["subset", "job_name"], dropna=False)[METRICS].mean().reset_index()
    rows: list[dict[str, object]] = []
    for subset, subset_frame in means.groupby("subset"):
        rmse_best = subset_frame.loc[subset_frame["rmse"].idxmin()]
        for metric in METRICS:
            metric_best = subset_frame.loc[subset_frame[metric].idxmin()]
            rows.append(
                {
                    "subset": subset,
                    "metric": metric,
                    "rmse_best_job": rmse_best["job_name"],
                    "metric_best_job": metric_best["job_name"],
                    "same_as_rmse_best": bool(metric_best["job_name"] == rmse_best["job_name"]),
                    "rmse_best_metric_value": float(rmse_best[metric]),
                    "metric_best_value": float(metric_best[metric]),
                    "rmse_at_rmse_best": float(rmse_best["rmse"]),
                    "rmse_at_metric_best": float(metric_best["rmse"]),
                    "rmse_change_pct": float((metric_best["rmse"] - rmse_best["rmse"]) / rmse_best["rmse"] * 100.0),
                }
            )
    result = pd.DataFrame(rows)
    result.to_csv(out_dir / "dual_lstm_rmse_vs_risk_best.csv", index=False)
    return result


def gate_status(test_metrics: pd.DataFrame) -> dict[str, object]:
    means = test_metrics.groupby(["subset", "job_name"], dropna=False)[METRICS].mean()
    safety_risk_wins = 0
    cycle_rmse_wins = 0
    for subset in EXPECTED_SUBSETS:
        baseline = means.loc[(subset, "lstm_baseline_h64_l1_w30")]
        cycle = means.loc[(subset, "dual_cycle_h64_l1_w30")]
        safety = means.loc[(subset, "dual_cycle_safety_w2_h64_l1_w30")]
        if cycle["rmse"] <= baseline["rmse"]:
            cycle_rmse_wins += 1
        if safety["critical_rmse_50"] < cycle["critical_rmse_50"] or safety["overestimation_magnitude"] < cycle["overestimation_magnitude"]:
            safety_risk_wins += 1
    return {
        "observed_subsets": EXPECTED_SUBSETS,
        "observed_jobs": JOB_ORDER,
        "min_seed_coverage": len(EXPECTED_SEEDS),
        "full_matrix_complete": True,
        "evaluable_subsets": len(EXPECTED_SUBSETS),
        "cycle_rmse_wins": cycle_rmse_wins,
        "safety_risk_wins": safety_risk_wins,
    }


def write_claim_map(out_dir: Path, status: dict[str, object]) -> pd.DataFrame:
    cycle_status = "pass" if status["cycle_rmse_wins"] >= 2 else "needs_review"
    safety_status = "pass" if status["safety_risk_wins"] >= 3 else "needs_review"
    rows = [
        {
            "claim_id": "P2-C1",
            "claim": "Dual-LSTM full matrix covers FD001-FD004 with 3 seeds and 4 jobs.",
            "evidence_file": "reports/paper2/dual_lstm_seed_metrics.csv",
            "gate": "Exactly 48 test rows, 96 metric rows, expected seeds 42/43/44, and complete metrics/predictions/history/feature files.",
            "status": "pass",
        },
        {
            "claim_id": "P2-C2",
            "claim": "Cycle consistency is the RMSE-oriented representation control.",
            "evidence_file": "reports/paper2/dual_lstm_full_summary.csv",
            "gate": "Dual-LSTM cycle RMSE should improve over LSTM baseline on at least 2 of 4 subsets.",
            "status": cycle_status,
        },
        {
            "claim_id": "P2-C3",
            "claim": "Cycle safety-w2 shifts the risk profile toward lower late-life or optimistic overestimation risk.",
            "evidence_file": "reports/paper2/dual_lstm_rmse_vs_risk_best.csv",
            "gate": "Risk improvement on at least 3 of 4 subsets before manuscript claim.",
            "status": safety_status,
        },
        {
            "claim_id": "P2-C4",
            "claim": "All conclusions are benchmark-limited and do not claim aviation certification or first-ever Dual-LSTM RUL.",
            "evidence_file": "reports/paper2/positioning_memo.md",
            "gate": "Boundary statement present before writing manuscript.",
            "status": "pass",
        },
    ]
    claim_map = pd.DataFrame(rows)
    claim_map.to_csv(out_dir / "claim_evidence_map.csv", index=False)
    return claim_map


def write_memos(out_dir: Path, status: dict[str, object], rmse_vs_risk: pd.DataFrame) -> None:
    subsets = ", ".join(status["observed_subsets"])
    jobs = ", ".join(status["observed_jobs"])
    risk_metrics = ["nasa_s_score", "critical_rmse_30", "critical_rmse_50", "overestimation_ratio", "overestimation_magnitude"]
    high_cost = rmse_vs_risk[
        rmse_vs_risk["metric"].isin(risk_metrics)
        & ~rmse_vs_risk["same_as_rmse_best"].astype(bool)
        & (rmse_vs_risk["rmse_change_pct"] > 5.0)
    ].copy()
    if high_cost.empty:
        tradeoff_warning = "- No risk-best comparison exceeds the 5% RMSE-cost warning threshold."
    else:
        warning_lines = []
        for _, row in high_cost.sort_values(["subset", "metric"]).iterrows():
            warning_lines.append(
                f"- {row['subset']} {row['metric']}: {row['metric_best_job']} is risk-best "
                f"with +{row['rmse_change_pct']:.1f}% RMSE versus {row['rmse_best_job']}; write as a trade-off."
            )
        tradeoff_warning = "\n".join(warning_lines)
    positioning = f"""# Paper 2 Positioning Memo

Working title: Cycle-Consistent Safety-Oriented Dual-LSTM for Aero-Engine RUL Prediction.

Paper 2 is a method-response paper built on Paper 1's safety-oriented C-MAPSS evaluation protocol. It tests whether a Dual-LSTM with target-conditioned degradation transition and cycle consistency can shift late-life and optimistic-overestimation risk while keeping aggregate RMSE interpretable.

Current matrix state: complete.
Observed subsets: {subsets}.
Observed jobs: {jobs}.
Minimum seed coverage per subset/job: {status['min_seed_coverage']}.

Protocol cautions:

- The LSTM baseline trains on all sequence windows, while Dual-LSTM jobs train on paired windows that require a same-engine future window. Interpret model differences as branch/loss/protocol evidence, not as pure parameter-count effects.
- Inference still uses only the current last window; future windows and future RUL are training-only regularization signals.

Trade-off warnings:

{tradeoff_warning}

Claim boundaries:

- Do not claim first-ever Dual-LSTM RUL.
- Do not claim new architecture SOTA.
- Do not claim aviation safety certification or real fleet validation.
- Treat negative FD002/FD003 results as subset-dependent trade-offs, not failures to hide.
"""
    experiment = """# Paper 2 Experiment Plan

Primary command:

```powershell
.\\.venv\\Scripts\\python.exe scripts\\run_dual_lstm_matrix.py --subsets FD001 FD002 FD003 FD004 --seeds 42 43 44 --jobs lstm_baseline_h64_l1_w30 dual_no_cycle_h64_l1_w30 dual_cycle_h64_l1_w30 dual_cycle_safety_w2_h64_l1_w30 --epochs 30 --patience 5 --skip-existing
```

Paper-facing output command:

```powershell
.\\.venv\\Scripts\\python.exe scripts\\make_dual_lstm_paper2_outputs.py --root reports\\tables\\dual_lstm --out-dir reports\\paper2
```

Acceptance gates:

- 48 jobs with metrics, predictions, training history, and selected feature files.
- `combined_metrics.csv` has 96 rows.
- Every subset/job/split has exactly seeds 42, 43, and 44 with no duplicate rows.
- `dual_cycle_h64_l1_w30` is the RMSE-oriented representation control.
- `dual_cycle_safety_w2_h64_l1_w30` reduces critical RMSE50 or overestimation magnitude on at least 3 of 4 subsets before making a positive risk-shift claim.
"""
    (out_dir / "positioning_memo.md").write_text(positioning, encoding="ascii")
    (out_dir / "experiment_plan.md").write_text(experiment, encoding="ascii")


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate Paper 2 Dual-LSTM tables and planning docs.")
    parser.add_argument("--root", default="reports/tables/dual_lstm")
    parser.add_argument("--out-dir", default="reports/paper2")
    args = parser.parse_args()

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    metrics = read_metrics(Path(args.root))
    test_metrics = validate_full_matrix(metrics)
    write_seed_metrics(test_metrics, out_dir)
    write_summary(test_metrics, out_dir)
    rmse_vs_risk = write_rmse_vs_risk(test_metrics, out_dir)
    status = gate_status(test_metrics)
    write_claim_map(out_dir, status)
    write_memos(out_dir, status, rmse_vs_risk)
    print(f"Wrote Paper 2 Dual-LSTM outputs to {out_dir}")


if __name__ == "__main__":
    main()
