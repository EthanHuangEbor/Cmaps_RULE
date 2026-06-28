# Cycle-Consistent Safety-Oriented Dual-LSTM for Aero-Engine RUL Prediction

## One-Sentence Argument

In C-MAPSS aero-engine RUL prediction, we show that a cycle-consistent Dual-LSTM can act as a safety-oriented method response to RMSE/risk discordance, supported by FD001-FD004 three-seed experiments and paired seed-engine bootstrap checks, with claims bounded to simulated benchmark evidence.

## Terminology Ledger

| Canonical term | Definition | Decision |
| --- | --- | --- |
| C-MAPSS | NASA Commercial Modular Aero-Propulsion System Simulation benchmark | Spell out once. |
| RUL | remaining useful life | Spell out once. |
| Dual-LSTM | cycle-consistent dual long short-term memory model | Use consistently. |
| Cycle consistency | training regularization aligning predicted future state with encoded future state | Do not call it inverse control. |
| Safety weighting | loss weighting emphasizing critical-zone or optimistic-overestimation errors | Do not call it aviation certification. |
| Critical RMSE50 | RMSE restricted to true RUL <= 50 cycles | Use exact name. |
| Overestimation magnitude | mean max(predicted RUL - true RUL, 0) | Use exact name. |

## Title Candidates

1. Cycle-Consistent Safety-Oriented Dual-LSTM for Aero-Engine Remaining Useful Life Prediction
2. Risk-Profile Shaping with Cycle-Consistent Dual-LSTM for C-MAPSS RUL Prediction
3. Cycle-Consistent Degradation Transition for Safety-Oriented RUL Prediction on C-MAPSS

## Abstract Skeleton

C-MAPSS RUL models are commonly selected by aggregate accuracy, yet Paper 1 shows that RMSE-optimal and risk-optimal rankings can diverge. This paper introduces a cycle-consistent Dual-LSTM that augments a current-window RUL branch with a target-conditioned degradation-transition branch during training. The model is evaluated on FD001-FD004 using the same engine-level split, train-only scaling, RUL cap, window size, seeds, and safety-oriented metrics as Paper 1. Across the full matrix, cycle consistency changed RMSE relative to the LSTM baseline by -4.6% to +0.4%, while adding safety weighting reduced Critical RMSE50 by -21.3% to -7.5% and overestimation magnitude by -42.6% to -29.1% relative to cycle-only Dual-LSTM. These results support Dual-LSTM as a candidate risk-profile shaping method, not as a universal SOTA model or aviation safety certification method.

## Introduction

1. Field stake: RUL prediction supports maintenance planning, but late-life overestimation is more hazardous than conservative underestimation.
2. Gap: Paper 1 showed that aggregate RMSE and safety-risk rankings can separate on C-MAPSS.
3. Prior routes: LSTM/GRU models capture temporal degradation, but one-branch supervision gives weak pressure for transition consistency between nearby engine states.
4. Present study: we test a cycle-consistent Dual-LSTM under Paper 1's safety-oriented protocol.

## Methods

1. Data and protocol: FD001-FD004, engine-level validation split, train-only scaling, max RUL 130, window size 30, last-window test, seeds 42/43/44.
2. Paired windows: same-engine pairs (X_t, y_t, X_t+k, y_t+k, k), k=1.
3. Model: current encoder/head plus target-conditioned transition LSTM and future head.
4. Losses: current RUL loss, future-cycle loss, latent consistency, monotonic penalty, optional safety_mse weighting.
5. Evaluation: RMSE, MAE, NASA S-score, Critical RMSE30/50, overestimation ratio/magnitude, paired seed-engine bootstrap, and Paper 1 bridge comparison.
6. Boundary: inference uses only the current last window; future windows and future RUL are training-only regularization signals.

## Results

1. Full matrix integrity: 48 jobs are complete across FD001-FD004, three seeds, and four LSTM/Dual-LSTM variants.
2. Cycle consistency: Dual-LSTM cycle changed RMSE relative to LSTM baseline by -4.6% to +0.4%; this is a modest representation signal.
3. Safety weighting: cycle+safety-w2 lowered Critical RMSE50 by -21.3% to -7.5% and overestimation magnitude by -42.6% to -29.1% relative to cycle-only.
4. Ranking discordance: RMSE-best and risk-best jobs separate in several subsets; FD003 is the favorable case where cycle+safety-w2 is also RMSE-best.
5. Paper 1 bridge: Paper2 best improves over Paper1 representative-matrix best in 4/20 subset-metric cells; do not claim full-portfolio superiority.

## Discussion

Cycle consistency may regularize degradation-state transitions, while safety weighting shifts the error distribution toward lower late-life and optimistic-overestimation risk. FD002 is the key caution because risk reduction carries visible RMSE cost. The LSTM baseline and Dual-LSTM jobs also differ in training support, so claims should be phrased as branch/loss/protocol evidence rather than pure parameter-count superiority.

## Conclusion

Cycle-consistent Dual-LSTM is a viable Paper 2 candidate under the safety-oriented C-MAPSS protocol. Its strongest evidence is systematic reduction of Critical RMSE50 and overestimation magnitude when safety weighting is added to the cycle branch, with subset-dependent RMSE trade-offs.

## Figure Plan

- Figure 1: Dual-LSTM architecture and inference boundary.
- Figure 2: metric-rank heatmap across FD001-FD004.
- Figure 3: RMSE versus Critical RMSE50.
- Figure 4: RMSE versus overestimation magnitude.
- Figure 5: Paper 1 to Paper 2 bridge comparison.

## Missing Before Full Submission

- Add verified literature citations.
- Decide target journal and format.
- Convert skeleton into LaTeX and run a value-trace audit.
- Add final figure legends and source-data captions.
