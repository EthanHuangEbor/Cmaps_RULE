# Paper 1 preprint readthrough audit

Date: 2026-07-01

Scope: manual readthrough-style audit of `reports/paper/main.tex`, `reports/paper/build/main.pdf`, `reports/paper/build/main.log`, `reports/paper/figure_table_manifest.md`, and `reports/paper/paper_value_trace.csv`.

## 1. Executive verdict

Conditional pass for entering the final human preprint readthrough.

The manuscript is coherent, appropriately scoped, and numerically traceable. The central claim is consistently framed as a benchmark-level evaluation and ranking-discordance contribution, not as a new state-of-the-art architecture or certified aviation safety method.

However, I would not treat the current PDF as preprint-ready without one layout pass. The main blocking issue is float placement/read order: Figure 5 appears after the end-matter has begun, and Table 5 is stranded on a mostly blank final page. There is also one LaTeX overfull hbox around Table 4. These are not content-validity failures, but they are visible enough to fix before posting.

## 2. Language flow

### Abstract

The abstract is strong but long. Source-based count: about 258 words. That may be acceptable for some preprint venues, but it reads dense because it includes protocol, metrics, SARBI definition, representative results, ablation, TCN, decision proxy, sensitivity checks, and contribution boundary in one block.

Suggested tightening: reduce one or two evidence-list sentences, especially the long sentence beginning "A post hoc temporal convolutional network..." if the target venue prefers concise abstracts. The current abstract is not misleading; it is just near the upper comfort range for readability.

### Introduction / Related Work

Flow is good. The paper establishes the safety asymmetry clearly, then narrows the question from architecture superiority to ranking mismatch. Related Work is appropriately positioned: it credits architecture-driven, uncertainty-aware, and decision-aware studies while explaining why this paper is diagnostic rather than SOTA-seeking.

Minor language issue: "Strong classical baselines remain competitive" and similar phrasing appears in Introduction, Results, and Discussion. It is substantively useful, but could be slightly consolidated in a final polish pass.

### Methods

Methods are clear and reproducible at manuscript level: engine-level validation, train-only scaling, capped labels, final-window test metrics, seeds, model classes, SARBI, and decision proxy are all described. The safety-loss equations are understandable.

Potential clarity issue: "pre-registered reference portfolio" is a strong procedural phrase. If there is not an externally timestamped pre-registration, consider "fixed reference portfolio" or "predefined reference portfolio" to avoid over-implying formal pre-registration.

### Results

Results are generally readable and well ordered from representative matrix to winner split, trade-offs, ablation, bootstrap, SARBI sensitivity, and TCN/decision checks. The narrative repeatedly returns to the main question, which helps.

The Results section is the longest section by far. This is acceptable for an empirical benchmark paper, but the TCN/decision/sensitivity subsection feels compressed because several checks are introduced in one paragraph sequence. It is still understandable.

### Discussion / Conclusion

Discussion is appropriately restrained. It explicitly rejects the strongest possible overclaims: no new SOTA architecture, no physical safety formula, no validated maintenance policy, no aviation certification. Threats to Validity further supports this restraint.

Conclusion is concise and aligned with the evidence. No obvious overclaim in the current conclusion.

## 3. Figure/table/reference audit

### Citation and label status

No obvious unresolved references were found.

- `main.log` search found no undefined citation/reference warnings.
- Extracted PDF text search found no `??` unresolved-reference markers.
- LaTeX label scan found no duplicate labels.
- Referenced figures/tables in text have corresponding labels.

One label is defined but not referenced in text: `fig:ablation-tradeoff`. This is not fatal because Figure 4 appears and is captioned, but the narrative around the ablation would read more cleanly if it explicitly referred to Figure 4.

Table 1 (`tab:positioning`) is also not explicitly referenced via `Table~\ref{tab:positioning}`. Because it appears in Related Work as a positioning table, this is acceptable but still worth considering.

### Figure/table order and float placement

Logical source order is sensible:

- Table 1 positioning.
- Table 2 representative matrix.
- Table 3 winner split.
- Figures 1-3 representative rank/trade-off plots.
- Table 4 ablation summary.
- Figure 4 ablation trade-off.
- Figure 5 SARBI sensitivity.
- Table 5 TCN/decision/sensitivity trace.

PDF float placement is the main issue:

- Figure 4 appears on page 8 after the Conclusion/end-matter has already started on page 7.
- Figure 5 appears on page 9 among the References.
- Table 5 appears alone on page 10 with large unused whitespace.

This does not indicate missing content, but it harms reading order and should be fixed before preprint release.

### Table pagination / overflow risk

No table was visually observed to be clipped or split across pages in the rendered PDF pages I inspected.

Confirmed layout risks:

- `main.log` reports `Overfull \hbox (40.19868pt too wide) in paragraph at lines 232--242`, corresponding to Table 4 (`tab:ablation-summary`). The rendered page did not appear visibly truncated in the inspected PNG, but the log warning is large enough to fix.
- `main.log` reports underfull boxes around line 286, corresponding to Table 5 narrow-cell wrapping. The table is readable, but line breaks are unattractive.
- Page 10 contains only Table 5 and substantial whitespace. This is a float placement/page economy issue rather than an overflow issue.

### Manifest and value trace

`figure_table_manifest.md` confirms the expected figure files and source CSVs exist for Figures 9-13 and identifies the table/numeric claim sources.

`paper_value_trace.csv` contains 152 records, all with status `matched`. It covers Table 2, Table 3, Table 4, the bootstrap paragraph, methods counts, and Table 5 claim trace.

## 4. Claim strength audit

Overall claim strength is appropriate.

Well-limited claims:

- The abstract says the contribution is a reproducible benchmark-level protocol and risk-trade-off evidence, not a certified aviation safety method.
- Methods call the safety loss "a benchmark intervention, not a certified safety mechanism."
- Decision proxy is explicitly not a fleet scheduler.
- SARBI is explicitly a reporting index, not a physical safety formula.
- Discussion says TCN is a stress test and does not convert the paper into an architecture claim.
- Threats to Validity identifies missing real fleet logistics, certified costs, distribution shift, and limited seed/hyperparameter coverage.

Potential overstatement or phrase to soften:

- "pre-registered reference portfolio" may imply a formal registry or time-stamped pre-registration. Use "predefined" unless such a registration exists.
- "systematic rank discordance" is probably justified by the matrix and sensitivity checks, but if aiming for maximum conservatism, "consistent rank discordance under the tested protocol" would be tighter.
- "FD002 and FD004 select Safety-GRU throughout the tested grid" is supported as a tested-grid claim. Keep "tested grid"; do not generalize beyond it.

No major Discussion overclaim found.

## 5. Required fixes before preprint

### Must fix

1. Resolve float placement so Figures 4-5 and Table 5 appear before end-matter/references or are moved into a cleaner appendix/supplement structure.
2. Fix the Table 4 overfull hbox warning at `main.tex` lines 232-242.

### Should fix

1. Shorten the abstract if the target preprint venue or journal style expects around 150-200 words.
2. Explicitly reference Figure 4 (`fig:ablation-tradeoff`) in the ablation narrative.
3. Consider explicitly referencing Table 1 in Related Work/Positioning.
4. Improve Table 5 column widths or wording to reduce underfull line breaks.
5. Consider changing "pre-registered reference portfolio" to "predefined reference portfolio" unless formal pre-registration exists.

### Can retain

1. The current contribution boundary language.
2. The decision proxy, SARBI, and TCN claims as currently qualified.
3. The Results-first empirical structure.
4. The Threats to Validity section, which is concise but adequate for the present draft.

## 6. Evidence

Commands/checks run:

- Listed required files and timestamps with `Get-ChildItem`.
- Read `reports/paper/main.tex` with line numbers.
- Read `reports/paper/figure_table_manifest.md`.
- Read full `reports/paper/paper_value_trace.csv`.
- Summarized value trace status: 152 `matched` records.
- Inspected `reports/paper/build/main.log` for `Warning`, `Overfull`, `Underfull`, `undefined`, `Citation`, `Reference`, `Rerun`, `Error`, and `Float`.
- Confirmed no undefined citation/reference warnings in `main.log`.
- Ran `pdftotext -layout reports/paper/build/main.pdf -` for PDF text review.
- Searched extracted PDF text for unresolved `??` markers.
- Ran `pdfinfo` via TeX Live Poppler: PDF has 10 A4 pages, generated 2026-07-01 15:59:45 CST.
- Rendered the PDF with `pdftoppm -png -r 150` to `C:\tmp\paper1_pdf_render_20260701`.
- Visually inspected rendered PNG pages through Node image emission: pages 1-10 were viewed in two batches.
- Scanned LaTeX labels/references and confirmed no duplicate labels.
- Counted approximate abstract length from source: 258 words.
- Counted approximate section lengths from source: Introduction 333 words, Related Work 348, Methods 690, Results 1561, Discussion 427, Threats to Validity 128, Conclusion 108.

Limitations:

- Visual inspection was performed from rendered PNGs, not by opening the PDF in a full PDF viewer. This is sufficient for clipping, gross placement, and page-flow issues, but final preprint proofing should still include a human PDF-viewer pass.
- I did not modify LaTeX source, figures, bibliography, or generated PDF.

## 7. Post-audit layout fix addendum

Applied after this audit:

- Changed the ablation summary table to `tabularx`, removing the previous 40pt overfull hbox.
- Added an explicit reference to `Figure~\ref{fig:ablation-tradeoff}` in the ablation narrative.
- Changed "pre-registered reference portfolio" to "predefined reference portfolio" to avoid implying formal pre-registration.
- Added `\clearpage` before Discussion so result floats complete before end-matter.
- Rebuilt with `reports/paper/build_paper.ps1` and refreshed `scripts/package_arxiv_source.py` output.

Post-fix log status: no `Overfull` warnings; remaining warnings are underfull box/page-fill warnings only. The rebuilt PDF has 11 pages.
