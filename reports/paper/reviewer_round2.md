# Reviewer Round 2: arXiv Readiness Re-Review

Date: 2026-06-25

## Decision

Accept for arXiv-readiness re-review.

No P0 or P1 blockers remain. The candidate `arxiv-draft-2026-06-25` at commit `aa1ddfcfddec2e9a7a15b419f774fbd1fc7e2057` is technically ready for arXiv upload, subject only to human-only submission choices.

## P0 Findings

None.

The remote tag exists and points to the candidate commit:

```text
aa1ddfcfddec2e9a7a15b419f774fbd1fc7e2057 refs/tags/arxiv-draft-2026-06-25
```

The repository status was clean before and after review.

## P1 Findings

None.

The arXiv source package is clean and independently compilable. The upload zip contains only:

```text
main.tex
references.bib
main.bbl
source_manifest.txt
figures/figure_01...figure_08.pdf
```

The source manifest reports:

```text
Missing referenced figures:
None
```

An independent compile of the extracted source package with TeX Live/XeLaTeX succeeded and produced an 11-page PDF.

## P2 Findings

Minor polish only.

Some comparative language remains, such as "difficult to beat" and "outperform basic deep models," but these statements are either background/contextual or directly supported by the reported FD001 table. They are not blockers.

The compile log contains underfull box warnings from narrow two-column tables. No fatal error, missing figure, unresolved citation, or overfull blocker was observed.

## Consistency Check

Table 3, Figure 2, `arxiv_metric_summary.csv`, and `paired_bootstrap_rmse.csv` are mutually consistent for the main claims.

Key checked values:

```text
FD003 GRU window50: RMSE 12.96 +/- 0.48
FD003 Gradient Boosting: RMSE 13.21 +/- 0.35
Bootstrap diff GRU window50 - GB: -0.249, 95% CI [-1.453, 1.003]
```

This supports the manuscript wording: GRU window50 is numerically lower on FD003, but the confidence interval crosses zero.

Safety claims also match the CSV:

```text
FD001 best critical RMSE50: GRU safety-w2, 4.86
FD003 lowest overestimation ratio: GRU safety-w2, 0.430
FD003 best critical RMSE50: Random Forest, 4.76
```

## Verification Evidence

Commands/files inspected:

```text
git rev-parse HEAD
git show-ref --tags arxiv-draft-2026-06-25
git ls-remote --tags origin arxiv-draft-2026-06-25
git status --short
tar -tf reports/paper/arxiv_upload.zip
reports/paper/arxiv_upload/source_manifest.txt
reports/paper/main.tex
reports/paper/arxiv_metric_summary.csv
reports/paper/paired_bootstrap_rmse.csv
reports/paper/figure_trace.csv
scripts/make_arxiv_figures.py
```

## Final Recommendation

Proceed to arXiv upload.

Remaining human-only tasks: choose arXiv category, license, author metadata, abstract text, comments field, and confirm that the work should be posted as a student reproducible benchmark rather than as a peer-reviewed contribution.
