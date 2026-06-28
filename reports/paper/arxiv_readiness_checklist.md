# arXiv / Preprint Readiness Checklist

Date: 2026-06-28

## Manuscript

- [x] Main manuscript source exists and has been rewritten for the FD001-FD004 safety-oriented benchmark: `reports/paper/main.tex`.
- [x] Bibliography exists: `reports/paper/references.bib`.
- [x] Manuscript scope is FD001-FD004 and explicitly avoids SOTA, aircraft certification, and SARBI-as-physical-formula claims.
- [x] Results are organized around RMSE-best versus risk-best rank discordance.
- [x] Numeric claims are traced in `reports/paper/paper_value_trace.csv`.
- [ ] Current PDF has not been rebuilt from the 2026-06-28 manuscript in this Codex environment because no TeX engine was available (`pdflatex`, `latexmk`, `xelatex`, `tectonic`, and `bibtex` were not found).
- [ ] Independent LaTeX compilation of the upload source package remains a human/environment task before public submission.

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
- [ ] `main.bbl` is not included because no fresh LaTeX/BibTeX build exists for the 2026-06-28 manuscript. Regenerate it during final TeX build if arXiv requires a bbl.
- [ ] Source package independent compilation is not verified in this environment.

## Reproducibility and Scope

- [x] Raw C-MAPSS data are referenced but not redistributed.
- [x] Code availability points to the public GitHub repository.
- [x] Main paper artifacts are reproducible with `scripts/make_safety_benchmark_outputs.py`, `scripts/audit_paper_submission.py`, and `scripts/package_arxiv_source.py`.
- [x] Paper 1 claims are scoped to simulated benchmark evidence and do not claim certified maintenance decisions.
- [x] AI assistance disclosure is included in `main.tex`.

## Artifact Hashes

- [x] `reports/paper/arxiv_upload.zip` SHA256: `13E5DD6989D7EE64A950BD7A34D0A5147C1F701336CC1426F60F94C41DDDA7A0`.
- [x] `reports/paper/main.tex` SHA256: `1B9C95735F9F06A7D52B8BD130458388A2A75788CFC85853F577A4204E21F430`.
- [x] `reports/paper/paper_value_trace.csv` SHA256: `0CE33D3AF13158542AF6CF0A45B8561310C2CBB647CB1DA9858C5C884A2375FF`.
- [ ] `reports/paper/build/main.pdf` SHA256 is intentionally not listed as current because the PDF is still the older 2026-06-26 build artifact.

## Remaining Human Submission Tasks

- [ ] Install/configure a TeX distribution or use Overleaf/GitHub Actions to compile `reports/paper/main.tex`.
- [ ] Verify all BibTeX metadata manually before public submission.
- [ ] Confirm author affiliation and author order.
- [ ] Choose arXiv category, likely `cs.LG`, `cs.AI`, or `eess.SY` depending on positioning.
- [ ] Choose arXiv license.
- [ ] Fill arXiv web metadata, abstract, comments, and code URL.
- [ ] Do one final human visual skim of the regenerated PDF before uploading.
