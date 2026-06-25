# arXiv Readiness Checklist

Date: 2026-06-25

## Manuscript

- [x] Main manuscript source exists: `reports/paper/main.tex`.
- [x] Bibliography exists: `reports/paper/references.bib`.
- [x] Compiled PDF exists: `reports/paper/build/main.pdf`.
- [x] The manuscript compiles with TeX Live 2026 and XeLaTeX.
- [x] Severe overfull table warnings were fixed by using `tabularx`.
- [x] No unresolved citations or undefined references were reported in the final compile output.
- [x] Visual spot checks were performed on rendered PDF pages 1, 2, 5, and 8.

## Figures and Tables

- [x] Eight arXiv-oriented figures were generated from project data and model outputs.
- [x] Figure trace file exists: `reports/paper/figure_trace.csv`.
- [x] Main summary table exists: `reports/paper/arxiv_metric_summary.csv`.
- [x] Safety trade-off summary exists: `reports/paper/safety_tradeoff_summary.csv`.
- [x] Paired bootstrap summary exists: `reports/paper/paired_bootstrap_rmse.csv`.
- [x] Main safety trade-off figure uses complete three-seed configurations.
- [x] Exploratory or duplicate ablation rows are not used for main model-comparison claims.

## arXiv Source Package

- [x] Clean source directory exists: `reports/paper/arxiv_upload`.
- [x] Upload zip exists: `reports/paper/arxiv_upload.zip`.
- [x] Source package includes `main.tex`, `references.bib`, `main.bbl`, `source_manifest.txt`, and referenced figure PDFs.
- [x] Source package excludes raw NASA data, model checkpoints, joblib files, local build intermediates, reviewer reports, and large experiment tables.
- [x] Source package independently compiles from `reports/paper/arxiv_upload/main.tex`.

## Reproducibility and Scope

- [x] README includes the arXiv figure-generation workflow.
- [x] Raw C-MAPSS data are referenced but not redistributed.
- [x] Code availability points to the public GitHub repository.
- [x] Manuscript claims are scoped to FD001/FD003 and do not claim state-of-the-art performance.
- [x] AI assistance disclosure is included.

## Remaining Human Submission Tasks

- [ ] Choose arXiv category, likely `cs.LG`, `cs.AI`, or `eess.SY` depending on positioning.
- [ ] Choose arXiv license.
- [ ] Verify all BibTeX metadata manually before public submission.
- [ ] Confirm author affiliation and author order.
- [ ] Fill arXiv web metadata, abstract, comments, and code URL.
