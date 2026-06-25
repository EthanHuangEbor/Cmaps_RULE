# Small-Paper IMRaD Outline

## Working Title

Safety-Oriented Benchmarking of Classical and Deep Sequence Models for Turbofan Engine RUL Prediction on C-MAPSS

## Introduction

- Predictive maintenance problem.
- Why RUL overestimation is more safety-critical than underestimation.
- Gap: many comparisons focus on aggregate RMSE and less on critical-zone behavior.

## Methods

- Dataset: NASA C-MAPSS FD001, extension FD003.
- Label construction: capped RUL.
- Split: engine-level validation.
- Models: Ridge, Random Forest, XGBoost/sklearn GradientBoosting, LSTM, GRU, 1D-CNN.
- Metrics: RMSE, MAE, NASA S-score, critical-zone RMSE, overestimation ratio.

## Results

- Main comparison table.
- Critical-zone analysis.
- Per-engine error analysis.
- Ablation on window size and RUL cap.

## Discussion

- Whether deep models improve aggregate accuracy.
- Whether they reduce safety-relevant overestimation.
- When traditional models remain competitive.
- Limits of simulated benchmark evidence.

## Conclusion

- State the strongest reproducible finding.
- State what should be tested next before claiming engineering usefulness.
