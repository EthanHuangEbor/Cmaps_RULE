# AutoResearch Task Spec: Paper 1 Submission Audit And Repository Cleanup

Date: 2026-07-01

## Goal

Prepare Paper 1 for preprint/submission and audit the repository structure so future experiments can extend the project without carrying stale artifacts.

## Scope

- Read through the current Paper 1 PDF/manuscript for language flow, figure/table references, pagination, abstract length, and overstatement risk.
- Audit BibTeX metadata, author/affiliation fields, arXiv category/license readiness, and refreshed source package contents.
- Audit repository folders, including notebooks, docs, reports, paper artifacts, and scratch-like outputs.
- Classify files as keep, archive, regenerate, review, or delete-candidate.

## Constraints

- Do not delete files without explicit human approval.
- Do not delete `.venv`, raw data, experiment scripts, or reusable configuration.
- Preserve future extension paths for additional experiments.
- Keep Paper 1 and Paper 2 artifacts separated.

## Deliverables

- `reports/paper/preprint_readthrough_2026-07-01.md`
- `reports/paper/bibtex_author_package_audit_2026-07-01.md`
- `reports/repo_cleanup_audit_2026-07-01.md`
- refreshed `reports/paper/build/main.pdf`
- refreshed `reports/paper/arxiv_upload.zip`
- updated checklist/state files as needed

## Success Criteria

- PDF build and source package rerun successfully.
- Numeric claim trace remains fully matched.
- Manuscript audit identifies actionable issues without inventing claims.
- BibTeX/package audit lists remaining human-only metadata tasks.
- Repo cleanup audit provides an approval-ready deletion/archive candidate list, but performs no deletions.