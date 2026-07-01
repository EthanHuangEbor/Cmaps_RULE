# arXiv / Preprint Readiness Checklist

Date: 2026-07-01

## Manuscript

- [x] Main manuscript source exists and has been rewritten for the FD001-FD004 safety-oriented benchmark: `reports/paper/main.tex`.
- [x] Bibliography exists: `reports/paper/references.bib`.
- [x] Manuscript scope is FD001-FD004 and explicitly avoids SOTA, aircraft certification, and SARBI-as-physical-formula claims.
- [x] Results are organized around RMSE-best versus risk-best rank discordance.
- [x] Numeric claims are traced in `reports/paper/paper_value_trace.csv`.
- [x] Current PDF has been rebuilt from the 2026-06-30 manuscript and re-verified with `latexmk`.
- [x] `latexmk` wrapper issue is root-caused to the Codex shell process missing `WINDIR`; `reports/paper/build_paper.ps1` applies the process-local workaround `$env:WINDIR = $env:SystemRoot` before running `latexmk`.

## Figures, Tables, and Data Trace

- [x] FD001-FD004 representative matrix summary exists: `reports/paper/matrix_safety_benchmark_summary.csv`.
- [x] FD001-FD004 deep safety-loss ablation summary exists: `reports/paper/deep_ablation_sarbi_summary.csv`.
- [x] RMSE-best versus risk-best tables exist for both representative matrix and deep ablation.
- [x] Bootstrap comparison file exists: `reports/paper/matrix_bootstrap_rmse_vs_sarbi.csv`.
- [x] SARBI weight-sensitivity file exists: `reports/paper/matrix_sarbi_weight_sensitivity.csv`.
- [x] Figure/table manifest exists: `reports/paper/figure_table_manifest.md`.
- [x] Current source package includes the FD001-FD004 figures referenced by `main.tex`: `figure_09` through `figure_13`.
- [x] Legacy FD001/FD003 figure files `figure_01` through `figure_08` remain in `reports/paper/figures/` for historical context but are excluded from the clean upload package.

## arXiv Source Package

- [x] Clean source directory exists: `reports/paper/arxiv_upload`.
- [x] Upload zip exists: `reports/paper/arxiv_upload.zip`.
- [x] Source package includes `main.tex`, `references.bib`, `source_manifest.txt`, and referenced figure PDFs.
- [x] Source package excludes raw NASA data, model checkpoints, joblib files, local build intermediates, reviewer reports, response drafts, and large experiment tables.
- [x] Zip contents match the clean upload directory and contain only the current FD001-FD004 figure set.
- [x] `main.bbl` is included from the fresh 2026-07-01 BibTeX build.
- [x] Source package contents have been refreshed from the current manuscript and figures.

## Reproducibility and Scope

- [x] Raw C-MAPSS data are referenced but not redistributed.
- [x] Code availability points to the public GitHub repository.
- [x] Main paper artifacts are reproducible with `scripts/make_safety_benchmark_outputs.py`, `scripts/audit_paper_submission.py`, `scripts/package_arxiv_source.py`, and `reports/paper/build_paper.ps1`.
- [x] Paper 1 claims are scoped to simulated benchmark evidence and do not claim certified maintenance decisions.
- [x] AI assistance disclosure is included in `main.tex`.

## Artifact Hashes

- [x] `reports/paper/arxiv_upload.zip` SHA256: `2FD8018BA7FBE932D0AB34DFD10D8FA5F103248F65CD1B8FE244DBE95FDA094F`.
- [x] `reports/paper/main.tex` SHA256: `99FEE3D3CE8B167359F6A63386E4C56DE3E9A8474CFDDA6FEFD31CC63E4C0FE8`.
- [x] `reports/paper/paper_value_trace.csv` SHA256: `E65026670B0BDA9696D3364689060DCA904A8C101FDFBDA1F2747FDE13A318B8`.
- [x] `reports/paper/build/main.pdf` SHA256: `0864B0A71D56F6C50DD28067DEBBE2F1D751029E36BDE077DCDADB836A36FEB5`.

## Remaining Human Submission Tasks

- [x] Resolve or bypass the local `latexmk` wrapper issue if the final workflow requires `latexmk`: set process-local `WINDIR` from `SystemRoot` before invoking `latexmk`.
- [ ] Verify all BibTeX metadata manually before public submission.
- [ ] Confirm author affiliation and author order.
- [ ] Choose arXiv category, likely `cs.LG`, `cs.AI`, or `eess.SY` depending on positioning.
- [ ] Choose arXiv license.
- [ ] Fill arXiv web metadata, abstract, comments, and code URL.
- [ ] Do one final human visual skim of the regenerated PDF before uploading.
