# Response to Reviewer Round 1

Date: 2026-06-25

Dear Reviewer,

Thank you for the detailed arXiv-readiness review. We agree that the paper should be presented as a reproducible, safety-aware benchmark study rather than as a state-of-the-art model paper. The revision focuses on traceability, claim discipline, and package-level reproducibility.

## Response to P0: Code availability and archival state

We agree that code availability must be backed by an actual pushed commit and tag. The manuscript, figures, arXiv source package, checklist, and reviewer-response files have been prepared for commit. The final step of this revision round is to push the repository and tag the exact arXiv candidate as `arxiv-draft-2026-06-25`.

Status: addressed in the local package; to be closed after GitHub push and tag verification.

## Response to P1: FD003 GRU window50 claim

We softened the claim throughout the manuscript. The revised text now states that the FD003 GRU window50 configuration obtains the numerically lowest RMSE among evaluated complete three-seed settings, but that the paired bootstrap comparison against Gradient Boosting is not statistically resolved.

Specific change: the Results section now reports the paired bootstrap difference as -0.25 cycles with 95% CI [-1.45, 1.00], and the Discussion avoids "beats" or "outperforms" wording.

## Response to P1: Table and figure consistency

We regenerated the arXiv-oriented figure set and summary CSV files. Table 3 now uses selected complete three-seed settings aligned with the main model-comparison figure. Focused ablation labels are explicitly distinguished from the default main rows.

Specific change: the figure-generation script now de-duplicates rows, prioritizes complete three-seed main settings, and records the data lineage in `reports/paper/figure_trace.csv`.

## Response to P1: Methods detail

We expanded the Methods and Experimental Setup sections. The revised manuscript specifies engine-level validation splitting, train-only scaler fitting, low-variance column removal, capped RUL construction for train/validation/test, sliding-window sequence construction, official-style last-window test evaluation, optimizer settings, early stopping, seeds, and baseline hyperparameters.

Specific change: the paper now distinguishes classical feature-engineered window summaries from raw-sequence deep inputs, so the comparison is framed as an engineering pipeline comparison.

## Response to P1: Future-work contradiction

We revised the limitations language. The manuscript no longer says that paired testing has not been done. Instead, it states that broader paired statistical comparisons across more models, subsets, and seeds remain future work.

## Response to P2: Source package and layout polish

We regenerated the eight arXiv-oriented figures, removed obsolete duplicate figures, generated a clean `arxiv_upload` source directory and `arxiv_upload.zip`, and independently compiled the upload source package. The manifest now records that no referenced figures are missing.

## Remaining Limitations

The paper is now suitable as a preprint-style student research manuscript if the GitHub commit/tag and final package compile are verified. Remaining scientific limitations are stated in the manuscript: only FD001/FD003 are studied, three seeds provide limited statistical power, FD002/FD004 and real engine data remain outside scope, and the safety-aware loss is a focused proof-of-concept rather than a deployed maintenance policy.
