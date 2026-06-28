# Paper 2 Statistical Audit

Audit method: paired bootstrap over seed-engine rows, pairing jobs by subset, seed, and engine. Lower metric values are better.

## Cycle Consistency
- Cycle versus LSTM baseline improves RMSE in 3/4 subsets by point estimate.
- The 95% bootstrap interval excludes zero in 1/4 subset-level RMSE contrasts.

## Safety Weighting
- Cycle+safety-w2 lowers Critical RMSE50 in 4/4 subsets by point estimate.
- Critical RMSE50 intervals exclude zero in 2/4 subsets.
- Cycle+safety-w2 lowers overestimation magnitude in 4/4 subsets by point estimate.
- Overestimation-magnitude intervals exclude zero in 4/4 subsets.

## Paper 1 Bridge
- Paper2 best is lower than the Paper1 representative-matrix best in 4/20 subset-metric cells.
- The bridge supports a bounded method-response claim, not full-portfolio SOTA superiority.

## Boundary
- This is simulated C-MAPSS benchmark evidence, not real-fleet aviation safety certification.
- Three seeds remain modest; use bootstrap and seed-consistency as robustness checks, not as decisive proof.
