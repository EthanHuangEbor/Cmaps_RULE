# Repository Cleanup Audit - 2026-07-01

Working directory: `D:\Beihang\Cmaps_RULE`

This audit was performed as a read-only repository simplification pass. No files
were deleted, no notebooks were modified, and no git commit/push/reset/checkout
operations were run.

## 1. Executive Verdict

The repository is a coherent C-MAPSS RUL research project with a solid core:
`src/`, `scripts/`, `tests/`, `configs/`, `data/raw/README.md`, the root
`README.md`, and paper-facing outputs in `reports/paper/` and `reports/paper2/`
should be kept. The main cleanup opportunity is not source code deletion; it is
separating generated/heavy artifacts from the human-facing repo path.

Key verdicts:

- `KEEP`: source package, experiment runners, tests, configs, README,
  paper-facing manuscripts, final summary CSVs, value traces, claim/evidence
  maps, and data instructions.
- `KEEP_AS_SHOWCASE`: `notebooks/README.md` only. There are currently no
  `.ipynb` files. The notebook folder can become a strong ML-project showcase
  if three lightweight notebooks are added.
- `ARCHIVE`: historical roadmaps, mentor materials, old review/progress notes,
  and auto-research state/logs with trace value but low day-to-day value.
- `REGENERATE`: LaTeX build intermediates, arXiv/source-upload bundles, most
  generated figures, generated table matrices, model checkpoints, and package
  zips when corresponding scripts and final paper artifacts are retained.
- `REVIEW_DELETE`: empty cache/scratch/tool folders and generated cache files,
  after user confirmation only.
- `DO_NOT_DELETE`: `.venv`, `.git`, raw C-MAPSS data, raw-data documentation,
  and any important experiment results not yet externalized.

Space finding: `reports/tables/` is about 2.86 GB and contains 1065 files. The
largest files are 12 Random Forest `.joblib` models under
`reports/tables/matrix/.../ml/random_forest.joblib`, each roughly 121-349 MB.
These should not be deleted blindly, but they are strong candidates for artifact
storage, release packaging, or regeneration rather than normal tracked content.

## 2. Folder-by-Folder Decision Table

| Path | Evidence | Decision | Recommendation |
| --- | --- | --- | --- |
| `.git/` | Git metadata present. | DO_NOT_DELETE | Never delete as part of cleanup. |
| `.venv/` | Local virtual environment present. User explicitly forbade deletion. | DO_NOT_DELETE | Absolutely do not delete. |
| `.agents/` | Empty directory in top-level listing. | REVIEW_DELETE | Confirm whether used by local agent tooling; delete only after user approval. |
| `.matplotlib-cache/` | 1 file, about 0.149 MB. Ignored by `.gitignore`. | REVIEW_DELETE | Safe cleanup candidate after confirmation. |
| `.pytest_cache/` | Directory present; access issue during no-ignore rg. Ignored by `.gitignore`. | REVIEW_DELETE | Safe cleanup candidate after confirmation. |
| `configs/` | 3 YAML files: FD001 ML/deep defaults and ablation plan. | KEEP | Small, reproducible experiment configuration; retain. |
| `data/raw/` | 15 files, about 43.25 MB; NASA C-MAPSS train/test/RUL text files, raw README, original PDF/readme. | DO_NOT_DELETE | Retain locally. Keep ignored if data redistribution is not allowed. |
| `docs/` | 3 md files: research status, Dual-LSTM method spec, Asif 2022 gap analysis. | KEEP / ARCHIVE split | Keep method spec and current status; consider moving older gap/status notes to `docs/archive/` after README links are stable. |
| `notebooks/` | Only `README.md`; no `.ipynb` files found. | KEEP_AS_SHOWCASE | Keep README; add lightweight notebooks for EDA/results/ablation showcase. |
| `reports/` root files | `learning_checklist.md`, two progress roadmaps, `reading_cards.md`. | ARCHIVE | Move to `reports/archive/` or `docs/archive/` unless actively used. |
| `reports/paper/` | Paper 1 main `.tex`, PDF, figures, summary CSVs, reviewer responses, arXiv package/build outputs. | KEEP / REGENERATE split | Keep manuscript, final PDF, paper-facing CSVs, value traces, reviewer responses; regenerate build/upload intermediates. |
| `reports/paper2/` | Paper 2 main/supplement `.tex` and PDFs, Dual-LSTM outputs, figures, manifests, claim maps, audit docs. | KEEP / REGENERATE split | Keep manuscript, supplement, PDFs, final CSVs, claim/evidence/audit docs; regenerate TIFF/build/source bundles if needed. |
| `reports/tables/` | 1065 files, about 2.86 GB; 828 CSV, 199 `.pt`, 36 `.joblib`, 2 logs. | DO_NOT_DELETE / REGENERATE split | Important experiment evidence, but too heavy for main path. Preserve externally or mark as regenerable artifact before cleanup. |
| `reports/review/` | Literature review md/tex/pdf/bib and generated figures/build intermediates. | ARCHIVE / KEEP | Keep if literature review is a deliverable; otherwise archive. Build intermediates are regenerable. |
| `reports/autoresearch/` | State/log JSONL files for paper cleanup and TCN extension. | ARCHIVE | Preserve for traceability, but move out of main report path if not active. |
| `reports/mentor_materials/` | Three small md files: pitch, one-pager, email template. | ARCHIVE | Useful handoff material, but not core repo operation. |
| `reports/logs/` | 8 log files, near-zero size. | REVIEW_DELETE | Delete/clear after confirming no active run depends on them. |
| `scratch/` | Empty directory. Ignored by `.gitignore`. | REVIEW_DELETE | Candidate for deletion after confirmation; no content observed. |
| `scripts/` | 37 scripts, about 0.452 MB; experiment runners, paper builders, audit/package scripts. | KEEP | Core reproducibility and paper-generation surface. |
| `src/rul_prediction/` | 43 files, about 0.2 MB; data, metrics, models, train, robustness, XAI, decision, uncertainty. | KEEP | Core package. Do not trim casually. |
| `tests/` | 26 files, about 0.091 MB; unit tests for models, metrics, paper output scripts, decision, uncertainty, etc. | KEEP | Essential regression guard. |
| `tools/` | Empty directory. | REVIEW_DELETE | Confirm whether reserved; otherwise remove after approval. |
| `work/` | 14 files, about 0.145 MB; ignored smoke/scratch outputs. | REVIEW_DELETE / REGENERATE | Keep only if useful for local smoke comparison; otherwise regenerate from scripts. |

## 3. Notebook Showcase Potential

Current state:

- No `.ipynb` files were found under the repo, excluding `.venv` and `.git`.
- `notebooks/README.md` explicitly says notebooks are optional and that the
  reproducible path is the Python package plus scripts.
- The README proposes three future notebooks:
  `01_eda_fd001_fd004.ipynb`, `02_results_analysis.ipynb`, and
  `03_ablation_review.ipynb`.

Verdict: `notebooks/` is currently not a showcase, but it is worth keeping as
`KEEP_AS_SHOWCASE` because the project has enough real ML material to support a
good demo layer.

Recommended showcase notebooks:

1. `01_eda_fd001_fd004.ipynb`
   - Load C-MAPSS raw train/test/RUL files.
   - Show engine trajectories, RUL cap behavior, sensor variance/constant
     feature screening, and train/test split intuition.
   - Use small sample plots and avoid storing large outputs.
2. `02_results_analysis.ipynb`
   - Read paper-facing CSVs from `reports/paper/` and `reports/paper2/`.
   - Show RMSE vs critical-zone error, overestimation ratio/magnitude, and
     ranking discordance.
   - This is the best portfolio/demo notebook because it explains the project
     thesis without rerunning heavy training.
3. `03_ablation_review.ipynb`
   - Summarize safety-loss and Dual-LSTM trade-offs from generated summaries.
   - Compare baseline, cycle consistency, and safety-weighted variants.
   - Keep it analysis-only and link back to scripts for reproduction.

Do not commit heavy notebook outputs. Export final figures through scripts so
the reproducible path remains script-first.

## 4. Docs Markdown Retention

Observed files:

- `docs/research_status.md`: current research framing, completed evidence,
  paper-ready outputs, key findings, next analysis, and scope boundaries.
- `docs/dual_lstm_method_spec.md`: Paper 2 method definition, interfaces,
  prototype/small/full matrix results, and claim boundaries.
- `docs/asif_2022_gap_analysis.md`: literature gap note against Asif et al.
  2022.

Recommendations:

- Keep `docs/dual_lstm_method_spec.md` in the main docs path. It is a method
  specification and directly explains source/script outputs.
- Keep `docs/research_status.md` while the papers are active. Later, merge its
  stable parts into `README.md` or a shorter `docs/project_positioning.md`.
- Archive `docs/asif_2022_gap_analysis.md` once its useful points are absorbed
  into the manuscript/literature review. It has trace value but is likely not a
  main-path doc forever.
- Consider adding a `docs/README.md` that distinguishes active specs from
  archived research notes.

## 5. Reports: Paper, Paper2, Autoresearch, Tables

### `reports/paper/`

Keep:

- `main.tex`
- `references.bib`
- `paper1_main.pdf`
- paper-facing CSVs such as safety summaries, sensitivity outputs,
  decision-proxy outputs, claim/evidence maps, and value traces
- reviewer reports/responses if they record manuscript history
- final figure PDFs/PNGs that are used directly by the paper

Regenerate or package externally:

- `reports/paper/build/` LaTeX intermediates (`.aux`, `.log`, `.bbl`, `.blg`,
  `.fdb_latexmk`, `.fls`, `.out`)
- `reports/paper/arxiv_upload/`
- `reports/paper/arxiv_upload.zip`
- generated figure copies inside upload packages, if the source scripts remain
  usable

### `reports/paper2/`

Keep:

- `main.tex`
- `supplement.tex`
- `paper2_main.pdf`
- `paper2_supplement.pdf`
- `references.bib`
- `claim_evidence_map*.csv`
- `statistical_audit.md`
- `citation_audit.md`
- `submission_readiness_checklist.md`
- `figure_manifest.md`, `figure_table_manifest.md`
- final analysis CSVs and final figure source CSVs

Regenerate or package externally:

- build folders
- submission source bundles/zips
- oversized raster exports such as TIFFs
- duplicate generated figure formats when one canonical editable format and one
  publication format are enough

### `reports/tables/`

This is the biggest cleanup decision. It contains the raw matrix evidence:

- `deep_ablations/`
- `dual_lstm/`
- `dual_lstm_smoke/`
- `matrix/`
- `matrix_tcn/`
- `matrix_tcn_small/`

The contents are valuable, but not all should live in the main repository path.
CSV summaries are relatively small and useful for auditing. Model artifacts
(`.joblib`, `.pt`) and full per-run predictions/training histories are better
treated as local/generated artifacts unless needed for exact reproducibility.

Recommended policy:

- Keep small summary CSVs needed to reproduce manuscript values.
- Keep a manifest recording run commands, seeds, subset, code version, and
  expected outputs.
- Move heavy `.joblib`/`.pt` artifacts to external artifact storage or a release
  asset before deleting locally.
- Delete from the repo working tree only after user confirms that the final
  paper-facing CSV/PDF outputs are sufficient or that the heavy artifacts are
  backed up elsewhere.

### `reports/review/`

The review material is useful if the literature review paper is still active.
If not active, archive it under `reports/archive/review/`. Generated LaTeX
auxiliary files inside `reports/review/ieee/` are regenerable.

### `reports/autoresearch/`

Auto-research state/log files should be archived, not deleted immediately. They
are not part of the clean public path, but they may explain why TCN extension or
paper cleanup decisions were made.

### `reports/mentor_materials/`

Keep as archive or move to `docs/archive/mentor_materials/`. These are useful
for handoff but not needed by package users.

## 6. Scratch and Temporary Files

Observed temporary/cache paths:

- `.matplotlib-cache/`: generated cache, ignored.
- `.pytest_cache/`: generated pytest cache, ignored.
- `scratch/`: empty, ignored.
- `tools/`: empty.
- `work/`: small ignored smoke/scratch output directory.
- `reports/logs/`: 8 near-empty log files.

Recommendation: all are cleanup candidates, but only after user approval.
Because the user explicitly said not to delete anything in this task, no action
was taken.

## 7. Approval-Ready Cleanup Plan

No cleanup should be executed until the user confirms each group.

Phase 1 - safe local cache cleanup:

- Candidate: `.matplotlib-cache/`
- Candidate: `.pytest_cache/`
- Candidate: empty `scratch/`
- Candidate: empty `tools/`
- Candidate: `reports/logs/` if no active run depends on it

Phase 2 - archive historical docs:

- Candidate move: `reports/progress_roadmap_2026-06-27.md`
- Candidate move: `reports/progress_roadmap_2026-06-28.md`
- Candidate move: `reports/learning_checklist.md`
- Candidate move: `reports/reading_cards.md`
- Candidate move: `reports/mentor_materials/`
- Candidate move: `reports/autoresearch/`
- Candidate move: `docs/asif_2022_gap_analysis.md` after manuscript/docs
  references are checked

Phase 3 - generated report artifact cleanup:

- Candidate remove/regenerate: LaTeX build intermediates under
  `reports/paper/build/` and `reports/review/ieee/`
- Candidate remove/regenerate: `reports/paper/arxiv_upload/`
- Candidate remove/regenerate: `reports/paper/arxiv_upload.zip`
- Candidate remove/regenerate: Paper 2 build/submission-source bundles
- Candidate de-duplicate: repeated figure formats when not required for
  submission

Phase 4 - heavy experiment artifact policy:

- Candidate externalize: `reports/tables/**/*.joblib`
- Candidate externalize: `reports/tables/**/*.pt`
- Candidate review: full per-run `predictions.csv` and `training_history.csv`
  if already aggregated into paper-facing summaries

Hard exclusions:

- Do not delete `.venv`.
- Do not delete `.git`.
- Do not delete `data/raw/`.
- Do not delete `src/`, `scripts/`, `tests/`, `configs/`, or active manuscript
  files.

## 8. Evidence Commands

Commands completed or partially completed during the audit:

```powershell
Get-ChildItem -Force | Select-Object Mode,Length,LastWriteTime,Name
rg --files --hidden -g '!.git/**' -g '!.venv/**'
Get-ChildItem -Directory -Force | Select-Object Name,LastWriteTime
Get-ChildItem -Force | Where-Object { $_.PSIsContainer -and ($excluded -notcontains $_.Name) } | ...
Get-ChildItem -Recurse -File -Force | Where-Object { $_.FullName -notmatch '\\.git\\|\\.venv\\' } | Group-Object Extension
Get-ChildItem -Path reports -Directory -Force | Select-Object Name,LastWriteTime
Get-ChildItem -Path reports -Directory -Force | ForEach-Object { ... file count and size ... }
Get-ChildItem -Recurse -File -Force | Where-Object { $_.FullName -notmatch '\\.git\\|\\.venv\\' } | Sort-Object Length -Descending | Select-Object -First 50
Get-ChildItem -Path data -Recurse -Force | Select-Object Mode,Length,LastWriteTime,FullName
Get-ChildItem -Path reports\tables -Recurse -File -Force | Sort-Object Length -Descending | Select-Object -First 40
Get-ChildItem -Path reports\tables -Directory -Force
Get-ChildItem -Path reports\tables -Recurse -File -Force | Group-Object Extension
Get-ChildItem -Path notebooks -Recurse -Force
Get-Content -LiteralPath notebooks\README.md
Get-ChildItem -Path . -Recurse -File -Include *.ipynb -Force | Where-Object { $_.FullName -notmatch '\\.venv\\|\\.git\\' }
Get-ChildItem -Path docs -File -Force
Get-Content -LiteralPath docs\research_status.md
Get-Content -LiteralPath docs\dual_lstm_method_spec.md
Get-Content -LiteralPath docs\asif_2022_gap_analysis.md
Get-Content -LiteralPath README.md -Encoding UTF8 | Select-Object -First 40
Get-Content -LiteralPath '实施计划.md' -Encoding UTF8 | Select-Object -First 60
Get-ChildItem -Path scripts -File -Force
rg -n "argparse|def main|if __name__|click" scripts src tests
Get-ChildItem -Path src\rul_prediction -File -Force
Get-ChildItem -Path tests -File -Force
rg -n "^(class|def) " src\rul_prediction tests
Get-ChildItem -Path configs -File -Force
Get-Content -LiteralPath configs\fd001_ml.yaml
Get-Content -LiteralPath configs\fd001_deep.yaml
Get-Content -LiteralPath configs\ablation_plan.yaml
Get-ChildItem -Path reports -File -Force
```

Limitations:

- The user asked to stop exploration and close out. Therefore the reports root
  markdown files were inventoried but not all deeply read.
- No tests were run because this was a cleanup audit, not a code-change task.
- `rg --files --hidden --no-ignore` reported an access issue for
  `./.pytest_cache`; this reinforces treating it as generated cache and a
  review-delete candidate, not as project evidence.
