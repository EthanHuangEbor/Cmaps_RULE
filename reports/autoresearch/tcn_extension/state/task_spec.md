# AutoResearch Task Spec: TCN Extension And Next Benchmark Step

Date: 2026-06-30

## Goal

Stabilize the TCN baseline extension as a clean GitHub PR and use it to decide
the next safety-oriented C-MAPSS benchmark step.

## Scope

- Publish the existing TCN baseline implementation and paper-facing summary.
- Keep the first TCN extension as a baseline-only result, not a SOTA claim.
- Preserve Paper 1 and Paper 2 boundaries:
  - Paper 1: safety-oriented model-selection benchmark.
  - Paper 2: Dual-LSTM risk-profile shaping extension.
- Plan the next research iteration around decision proxy, sensitivity, or TCN
  safety-loss follow-up.

## Deliverables

- Clean remote branch and pull request for `codex/tcn-baseline`.
- `reports/paper/tcn_matrix_summary.csv`
- `reports/paper/tcn_vs_representative_best.csv`
- `reports/paper/tcn_matrix_extension_note.md`
- AutoResearch state files under `reports/autoresearch/tcn_extension/state/`.
- `reports/paper/sensitivity_checks_note.md` and companion sensitivity CSVs.
- `reports/paper/tcn_claim_evidence_map.csv`, `reports/paper/tcn_safety_loss_gate.csv`, and `reports/paper/tcn_claim_trace_note.md`.

## Success Criteria

- PR branch is based on remote `main`, not the stale local Paper 2 branch
  history.
- The PR contains only main-synced paper artifacts plus TCN implementation,
  tests, and small paper-facing TCN summaries.
- Tests reported in the PR:
  - `python -m pytest -q -p no:cacheprovider`
  - TCN smoke training
  - FD001-FD004 TCN minimal full matrix completeness check.
- The next research step is explicitly staged and claim-bounded.

## Constraints

- Do not claim TCN is SOTA.
- Do not claim safety certification or real-fleet validation.
- Do not commit full ignored matrix outputs from `reports/tables/**`.
- If `git push` fails, use GitHub API fallback without printing tokens.
