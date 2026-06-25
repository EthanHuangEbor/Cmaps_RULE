# Simulated Reviewer Report

## Decision

Major Revision.

The manuscript has a clear and suitable undergraduate research direction: it does not claim a new state-of-the-art architecture, but compares classical baselines and deep sequence models while emphasizing safety-asymmetric RUL errors. This positioning is valuable for a C-MAPSS student research project. However, the current version needs stronger experimental-protocol detail, clearer definition of the safety-aware loss, more careful scope limitation, and more complete reporting of robustness before it can be treated as a submission-ready short paper.

## Major Issues

1. The methodology needs enough detail for reproducibility: feature selection, low-variance column removal, train/validation split by engine ID, scaler fitting, RUL cap, sliding-window construction, last-window test rule, model settings, optimizer, early stopping, and random seeds.

2. Three seeds are useful as a minimum robustness check, but they are not enough to support strong statistical claims. The paper should report mean and standard deviation, and phrase stability claims cautiously.

3. The safety-aware loss must be mathematically defined. The manuscript should specify the critical threshold, overestimation condition, whether weights are additive, and the exact weight values.

4. Safety claims need consistent metrics for all models, not only selected GRU variants. NASA S-score, critical-zone RMSE, and overestimation ratio should be reported together.

5. FD001 and FD003 are both single-operating-condition subsets. The claims should be scoped to FD001/FD003 and should not be generalized to all C-MAPSS subsets or real engine fleets.

6. The window50 result should be described as an empirical finding among tested configurations, not as a general proof that longer windows help recurrent models.

7. The comparison mixes feature-engineered classical models and raw-sequence neural models. This is acceptable as an engineering pipeline comparison, but not as a pure architecture comparison.

8. Citations and dataset/scoring details should be verified before formal submission.

## Minor Issues

- Use “among evaluated configurations” when describing best results.
- Avoid implying real aviation safety validation from benchmark-level safety metrics.
- Define the critical-zone threshold explicitly.
- Interpret CNN failure narrowly as failure of the tested configuration.
- Mention that full all-metric standard deviations are available in CSV outputs if not printed in the main table.

## Required Revision Priorities

1. Add dataset-scope and protocol tables.
2. Add the explicit NASA S-score and safety-loss equations.
3. Narrow claims to FD001/FD003 and evaluated configurations.
4. Add a threats-to-validity section.
5. Clarify practical pipeline comparison.
6. Verify references before any external submission.
