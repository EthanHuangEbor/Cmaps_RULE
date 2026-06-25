# Small Paper Blueprint

## Working Title

Safety-Aware Evaluation and Improvement of Classical and Deep Sequence Models
for Turbofan Engine RUL Prediction on C-MAPSS

## Research Question

In C-MAPSS turbofan engine RUL prediction, do deep sequence models outperform
classical machine learning models under safety-oriented metrics such as
critical-zone error and overestimation risk?

## Contribution Target

This paper should not claim novelty from simply applying LSTM or GRU. The
contribution should be:

1. A reproducible comparison of classical and deep models under leakage-safe
   preprocessing.
2. A safety-oriented evaluation emphasizing critical-zone error and RUL
   overestimation.
3. A first-pass safety-aware GRU training variant.

## Planned Evidence

| Evidence | Required before paper draft |
|---|---|
| FD001 all models | Done for seed 42 |
| FD001 three seeds | Required |
| FD003 three seeds | Required |
| Window-size ablation | Required |
| Max-RUL ablation | Required |
| Safety-aware GRU | Required |
| Feature importance | Partially done |
| Failure-case analysis | Partially done |

## Paper Structure

1. Introduction: PHM, RUL, C-MAPSS, safety asymmetry.
2. Related Work: classical baselines, LSTM/GRU/CNN, C-MAPSS studies.
3. Method: preprocessing, model families, safety-aware losses.
4. Experiments: FD001/FD003, seeds, metrics, ablations.
5. Results: model comparison, critical-zone behavior, safety-aware loss.
6. Discussion: why tree baselines are strong, where recurrent models help,
   why CNN failed, limitations of simulated data.
7. Conclusion: evidence-backed claim and next steps.

## Minimum Figure Set

- Overall RMSE/MAE bar chart.
- NASA S-score comparison.
- Critical-zone RMSE comparison.
- Per-engine error plot.
- Prediction scatter plot.
- Feature importance or failure-case chart.

