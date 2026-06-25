# Reviewer Round 1: arXiv Readiness Review

Date: 2026-06-25

## Decision

Major Revision.

The manuscript has a defensible student-research contribution: it compares classical feature-engineered baselines with deep sequence models on C-MAPSS FD001/FD003, and it correctly shifts the contribution away from "we used LSTM" toward safety-aware RUL evaluation. However, the first arXiv-style draft was not yet ready because several claims and package-level guarantees were stronger than the available evidence.

## Priority Findings

### P0. Code availability and archival state were claimed before being fixed

The manuscript and checklist referred to a public GitHub code package, but the revised paper sources, generated figures, arXiv package, and exact draft tag had not yet been committed, tagged, and pushed. This is a blocking reproducibility issue for an arXiv upload.

Required action: commit all manuscript/figure/source-package changes, push them to GitHub, and create a stable tag for the arXiv draft.

### P1. FD003 GRU window50 claim was too strong

The FD003 GRU window50 configuration had the numerically lowest RMSE among the complete three-seed settings, but the paired bootstrap comparison against Gradient Boosting was not statistically resolved. The RMSE difference was -0.25 cycles with a 95% CI of [-1.45, 1.00], so the manuscript must not claim that GRU statistically beats Gradient Boosting.

Required action: replace "best" or "outperforms" language with "numerically lowest among evaluated configurations" and explicitly report the uncertainty.

### P1. Results table and figure consistency needed tightening

The manuscript table, Figure 2, and the CSV summary did not yet consistently distinguish complete three-seed main configurations from focused ablation or safety-loss variants. A reader could misread exploratory rows as main comparisons.

Required action: define which rows are main complete three-seed settings, align Table 3 with Figure 2, and keep exploratory ablations out of main claims.

### P1. Methods details were under-specified

The paper needed clearer descriptions of train/validation splitting by engine ID, train-only scaling, low-variance column removal, RUL capping for train/validation/test labels, last-window test evaluation, optimizer/early-stopping settings, and classical model hyperparameters.

Required action: expand Methods and Experimental Setup so the workflow can be reproduced from the repository.

### P1. Future-work contradiction

The manuscript had already added paired bootstrap confidence intervals, but the limitations/future-work section still implied that paired tests remained future work.

Required action: revise the limitation to call for broader paired statistical comparisons, not the first paired test itself.

### P2. Source package and layout polish

The source package and figure manifest needed a clean "no missing figures" statement. Old duplicate figures should be removed. Some PDF pages needed visual spot checks after the layout changes.

Required action: regenerate the arXiv source package, compile it independently, remove obsolete figures, and keep a source manifest.

## Editorial Assessment

The paper can become arXiv-uploadable after these revisions, but only if the final package is tested from the upload directory and the public repository/tag match the manuscript's code-availability statement. The scientific contribution should remain modest and careful: a reproducible, safety-aware benchmark study rather than a claim of new state-of-the-art performance.
