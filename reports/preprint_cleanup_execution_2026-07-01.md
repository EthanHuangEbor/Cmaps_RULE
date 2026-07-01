# Paper 1 Preprint And Repository Cleanup Execution Record

Date: 2026-07-01
Scope: Paper 1 preprint readiness, CSV-backed claim audit, repository usefulness audit, and cleanup planning before future experiments.

## Executed Work

- Ran a PDF-level preprint readthrough and recorded the findings in `reports/paper/preprint_readthrough_2026-07-01.md`.
- Ran a BibTeX, author-info, and source-package audit and recorded the findings in `reports/paper/bibtex_author_package_audit_2026-07-01.md`.
- Ran a repository file usefulness audit and inventory and recorded the findings in `reports/repo_cleanup_audit_2026-07-01.md` and `reports/repo_file_inventory_2026-07-01.csv`.
- Rebuilt `reports/paper/build/main.pdf` with `reports/paper/build_paper.ps1`.
- Repacked `reports/paper/arxiv_upload.zip` with `scripts/package_arxiv_source.py`.
- Refreshed `reports/paper/arxiv_readiness_checklist.md` with final artifact hashes.

## Manuscript Fixes Applied

- Softened the wording from "pre-registered reference portfolio" to "predefined reference portfolio".
- Added an explicit in-text reference to the ablation trade-off figure.
- Reworked wide tables with `tabularx` where needed.
- Inserted a page break before Discussion so the TCN claim-trace table and sensitivity figure appear before Discussion/References.
- Rebuilt the PDF and verified that no `undefined`, `Fatal`, `Error`, or `Overfull` log issues remain.

## Current Paper 1 Stage

Paper 1 is now in preprint-package readiness, not experiment-building. The remaining blockers are human submission metadata choices rather than computational evidence:

- Verify BibTeX metadata manually.
- Confirm author affiliation and author order.
- Choose arXiv category and license.
- Fill web-submission metadata.
- Perform one final human visual skim of the regenerated PDF.

## Repository Cleanup Decision

No deletion was performed. The repository is ready for a staged cleanup after approval:

1. Keep core code, configs, tests, raw-data README, paper scripts, and reproducible summary CSVs.
2. Keep `.venv` because it is required for local continuation.
3. Keep `notebooks/` and turn it into an experiment showcase area rather than deleting it.
4. Keep `docs/` for now, but merge or retire old handoff/status notes only after confirming they are superseded by `docs/research_status.md` and current paper reports.
5. Review `reports/tables/` before future pushes because it is large and contains experiment artifacts/checkpoints that should not become manuscript evidence unless summarized.
6. Treat `scratch/`, logs, build intermediates, and cache-like folders as deletion candidates only after an explicit approval pass.

## Notebook Showcase Plan

Recommended notebooks for machine-learning project demonstration:

- `notebooks/01_cmapps_protocol_overview.ipynb`: dataset protocol, RUL capping, engine split, scaling, and last-window test logic.
- `notebooks/02_paper1_safety_benchmark_results.ipynb`: RMSE versus safety-risk ranking, SARBI, bootstrap intervals, and main figures.
- `notebooks/03_paper2_dual_lstm_results.ipynb`: Dual-LSTM ablation, late-life risk, overestimation metrics, and Paper 1 comparison.

The notebooks should read from existing CSV artifacts and should not retrain models by default.

## Next Local Actions

- Commit and push this preprint-readiness and cleanup audit bundle.
- Update the pull-request description with the new PDF/package audit evidence.
- After the user approves cleanup scope, perform a separate cleanup branch that removes only agreed generated intermediates or archives bulky experiment outputs.
