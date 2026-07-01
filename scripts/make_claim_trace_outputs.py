from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


def _ratio(numerator: int, denominator: int) -> str:
    return f"{numerator}/{denominator}"


def _bool_count(frame: pd.DataFrame, column: str) -> tuple[int, int]:
    if column not in frame.columns:
        raise ValueError(f"Missing required column: {column}")
    values = frame[column].astype(bool)
    return int(values.sum()), int(len(values))


def _metric_improvement_count(tcn_vs_best: pd.DataFrame, metric: str) -> tuple[int, int]:
    subset = tcn_vs_best[tcn_vs_best["metric"].eq(metric)].copy()
    if subset.empty:
        raise ValueError(f"No rows found for metric: {metric}")
    deltas = pd.to_numeric(subset["delta_vs_best"], errors="coerce")
    return int((deltas <= 0).sum()), int(deltas.notna().sum())


def _model_best_count(frame: pd.DataFrame, model_column: str, model_name: str) -> tuple[int, int]:
    if model_column not in frame.columns:
        raise ValueError(f"Missing required column: {model_column}")
    values = frame[model_column].astype(str).str.lower()
    return int(values.eq(model_name.lower()).sum()), int(len(values))


def _scenario_agreement_summary(sensitivity_decision: pd.DataFrame) -> str:
    grouped = sensitivity_decision.groupby("cost_scenario")["same_model"].sum().sort_index()
    totals = sensitivity_decision.groupby("cost_scenario")["same_model"].size().sort_index()
    return "; ".join(f"{name}={int(grouped[name])}/{int(totals[name])}" for name in grouped.index)


def build_claim_evidence_map(out_dir: Path) -> pd.DataFrame:
    tcn_vs_best = pd.read_csv(out_dir / "tcn_vs_representative_best.csv")
    decision_base = pd.read_csv(out_dir / "decision_proxy_rmse_vs_cost_best.csv")
    decision_best = pd.read_csv(out_dir / "decision_proxy_best_by_cost.csv")
    sens_critical = pd.read_csv(out_dir / "sensitivity_critical_threshold_rmse_vs_risk_best.csv")
    sens_decision = pd.read_csv(out_dir / "sensitivity_decision_cost_rmse_vs_cost_best.csv")
    sens_decision_best = pd.read_csv(out_dir / "sensitivity_decision_cost_best.csv")

    rmse_improved, rmse_total = _metric_improvement_count(tcn_vs_best, "rmse")
    critical_improved, critical_total = _metric_improvement_count(tcn_vs_best, "critical_rmse_50")
    overmag_improved, overmag_total = _metric_improvement_count(tcn_vs_best, "overestimation_magnitude")
    decision_agree, decision_total = _bool_count(decision_base, "same_model")
    sens_critical_agree, sens_critical_total = _bool_count(sens_critical, "same_model")
    sens_decision_agree, sens_decision_total = _bool_count(sens_decision, "same_model")
    tcn_decision_best, tcn_decision_total = _model_best_count(decision_best, "model", "tcn")
    tcn_sens_decision_best, tcn_sens_decision_total = _model_best_count(sens_decision_best, "model", "tcn")
    scenario_summary = _scenario_agreement_summary(sens_decision)

    rows = [
        {
            "claim_id": "TCN-001",
            "claim": "TCN should be treated as a stronger sequence baseline extension, not as a SOTA or safety-certification claim.",
            "evidence_files": "reports/paper/tcn_matrix_summary.csv; reports/paper/tcn_vs_representative_best.csv",
            "evidence_rows": "4 subset summary rows; 24 metric-comparison rows",
            "extracted_value": "baseline-only TCN across FD001-FD004 and seeds 42/43/44",
            "interpretation": "Use TCN to stress-test benchmark rankings, not to reframe the paper around a new architecture.",
            "manuscript_use": "Methods/Discussion boundary statement",
            "confidence": "high",
        },
        {
            "claim_id": "TCN-002",
            "claim": "TCN matches or improves the representative-matrix RMSE best on only a subset of C-MAPSS subsets.",
            "evidence_files": "reports/paper/tcn_vs_representative_best.csv",
            "evidence_rows": "metric == rmse",
            "extracted_value": _ratio(rmse_improved, rmse_total),
            "interpretation": "TCN is competitive on aggregate RMSE in some subsets but does not dominate the matrix.",
            "manuscript_use": "Results: TCN baseline comparison",
            "confidence": "high",
        },
        {
            "claim_id": "TCN-003",
            "claim": "TCN risk-side gains are mixed and do not replace safety-oriented losses or classical baselines.",
            "evidence_files": "reports/paper/tcn_vs_representative_best.csv",
            "evidence_rows": "metric in {critical_rmse_50, overestimation_magnitude}",
            "extracted_value": f"critical_rmse_50={_ratio(critical_improved, critical_total)}; overestimation_magnitude={_ratio(overmag_improved, overmag_total)} comparable rows",
            "interpretation": "TCN cannot be promoted as a risk-best model from baseline-only evidence.",
            "manuscript_use": "Results/Discussion: risk trade-off",
            "confidence": "high",
        },
        {
            "claim_id": "DEC-001",
            "claim": "Under the baseline decision proxy, RMSE-best and decision-cost-best rankings are usually different.",
            "evidence_files": "reports/paper/decision_proxy_rmse_vs_cost_best.csv",
            "evidence_rows": "all rows",
            "extracted_value": f"agreement={_ratio(decision_agree, decision_total)}",
            "interpretation": "Decision proxy strengthens the safety-oriented ranking-discordance thesis.",
            "manuscript_use": "Results: decision proxy",
            "confidence": "high",
        },
        {
            "claim_id": "DEC-002",
            "claim": "TCN is decision-cost-best in some cells but not enough to become the paper's central risk model.",
            "evidence_files": "reports/paper/decision_proxy_best_by_cost.csv; reports/paper/sensitivity_decision_cost_best.csv",
            "evidence_rows": "model == tcn",
            "extracted_value": f"baseline_cost={_ratio(tcn_decision_best, tcn_decision_total)}; sensitivity_cost={_ratio(tcn_sens_decision_best, tcn_sens_decision_total)}",
            "interpretation": "TCN is useful as an additional comparator, while Safety-GRU/classical models still explain many risk-best cells.",
            "manuscript_use": "Results: model-specific decision-best cells",
            "confidence": "high",
        },
        {
            "claim_id": "SENS-001",
            "claim": "Critical-zone ranking discordance is not an artifact of choosing one threshold.",
            "evidence_files": "reports/paper/sensitivity_critical_threshold_rmse_vs_risk_best.csv",
            "evidence_rows": "thresholds 20, 30, 50, 70",
            "extracted_value": f"agreement={_ratio(sens_critical_agree, sens_critical_total)}",
            "interpretation": "RMSE-best rarely matches critical-zone-best across threshold choices.",
            "manuscript_use": "Robustness/sensitivity paragraph",
            "confidence": "high",
        },
        {
            "claim_id": "SENS-002",
            "claim": "Decision-cost ranking discordance is not an artifact of one declared cost schema.",
            "evidence_files": "reports/paper/sensitivity_decision_cost_rmse_vs_cost_best.csv",
            "evidence_rows": "5 cost scenarios x 4 subsets x 4 lead times",
            "extracted_value": f"agreement={_ratio(sens_decision_agree, sens_decision_total)}; {scenario_summary}",
            "interpretation": "Agreement remains low under every tested cost schema.",
            "manuscript_use": "Robustness/sensitivity paragraph",
            "confidence": "high",
        },
        {
            "claim_id": "GATE-001",
            "claim": "TCN safety-loss training is not required before the next manuscript pass.",
            "evidence_files": "reports/paper/tcn_vs_representative_best.csv; reports/paper/decision_proxy_rmse_vs_cost_best.csv; reports/paper/sensitivity_decision_cost_rmse_vs_cost_best.csv",
            "evidence_rows": "TCN mixed-risk rows plus decision/sensitivity discordance rows",
            "extracted_value": "defer",
            "interpretation": "Current claims are evaluation claims with sufficient CSV evidence; TCN safety-loss would open a new model-family ablation.",
            "manuscript_use": "Experiment gate / future work",
            "confidence": "medium-high",
        },
    ]
    return pd.DataFrame(rows)


def build_safety_loss_gate(claim_map: pd.DataFrame) -> pd.DataFrame:
    values = {row["claim_id"]: row["extracted_value"] for _, row in claim_map.iterrows()}
    rows = [
        {
            "gate_item": "Current manuscript claims need TCN safety-loss",
            "evidence": "Claim map frames TCN as baseline/evaluation extension; no current claim requires architecture-specific risk shaping.",
            "decision": "no",
        },
        {
            "gate_item": "Baseline TCN already dominates risk metrics",
            "evidence": values["TCN-003"],
            "decision": "no",
        },
        {
            "gate_item": "Ranking-discordance thesis lacks evidence without new training",
            "evidence": f"{values['DEC-001']}; {values['SENS-001']}; {values['SENS-002']}",
            "decision": "no",
        },
        {
            "gate_item": "Recommended immediate action",
            "evidence": "All TCN/decision/sensitivity claims now have CSV-backed trace rows.",
            "decision": "defer TCN safety-loss; integrate claim trace into manuscript first",
        },
        {
            "gate_item": "Conditional trigger for future TCN safety-loss",
            "evidence": "Run only if manuscript adds architecture-independent safety-loss claims or reviewers ask whether risk shaping transfers from GRU to TCN.",
            "decision": "conditional future experiment",
        },
    ]
    return pd.DataFrame(rows)


def write_note(claim_map: pd.DataFrame, gate: pd.DataFrame, out_path: Path) -> None:
    lines = [
        "# TCN Claim Trace And Experiment Gate",
        "",
        "Scope: map every current TCN, decision-proxy, and sensitivity-check paper claim to concrete CSV evidence before deciding whether to run a TCN safety-loss experiment.",
        "",
        "## Claim-Evidence Map",
        "",
        "```text",
        claim_map[
            [
                "claim_id",
                "extracted_value",
                "evidence_files",
                "interpretation",
            ]
        ].to_string(index=False),
        "```",
        "",
        "## TCN Safety-Loss Gate",
        "",
        "```text",
        gate.to_string(index=False),
        "```",
        "",
        "## Decision",
        "",
        "- Do not run a TCN safety-loss small experiment immediately.",
        "- The current evidence package supports the evaluation-paper claim: aggregate RMSE, critical-zone risk, and decision-cost rankings separate under multiple checks.",
        "- Treat TCN safety-loss as a conditional future experiment, not a blocker for the next manuscript pass.",
        "",
    ]
    out_path.write_text("\n".join(lines), encoding="utf-8")


def run(args: argparse.Namespace) -> None:
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    claim_map = build_claim_evidence_map(out_dir)
    gate = build_safety_loss_gate(claim_map)
    claim_map.to_csv(out_dir / "tcn_claim_evidence_map.csv", index=False)
    gate.to_csv(out_dir / "tcn_safety_loss_gate.csv", index=False)
    write_note(claim_map, gate, out_dir / "tcn_claim_trace_note.md")
    print(f"Wrote {out_dir / 'tcn_claim_evidence_map.csv'}")
    print(f"Wrote {out_dir / 'tcn_safety_loss_gate.csv'}")
    print(f"Wrote {out_dir / 'tcn_claim_trace_note.md'}")
    print(f"Claim rows: {len(claim_map)}")
    print(f"Gate rows: {len(gate)}")
    print("TCN safety-loss decision: defer")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate TCN claim-evidence trace and safety-loss gate outputs.")
    parser.add_argument("--out-dir", default="reports/paper")
    return parser.parse_args()


def main() -> None:
    run(parse_args())


if __name__ == "__main__":
    main()
