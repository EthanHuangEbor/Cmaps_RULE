# Learning Checklist

## Problem Layer

- [ ] Define Remaining Useful Life (RUL).
- [ ] Explain why RUL prediction belongs to PHM.
- [ ] Explain why overestimating RUL is safety-critical.
- [ ] Explain why C-MAPSS is simulated benchmark data.
- [ ] Explain the difference between FD001 and FD003.

## Data Layer

- [ ] Explain engine-level splitting.
- [ ] Explain why random window splitting causes leakage.
- [ ] Explain train-only scaler fitting.
- [ ] Explain capped RUL and `max_rul=130`.
- [ ] Explain sliding windows and final-window test evaluation.

## Model Layer

- [ ] Explain Ridge as a linear baseline.
- [ ] Explain why Random Forest / Gradient Boosting are strong baselines.
- [ ] Explain LSTM and GRU sequence inputs.
- [ ] Explain why 1D-CNN might fail on this setup.
- [ ] Explain why baseline comparison is required before claiming deep learning value.

## Metric Layer

- [ ] Explain RMSE and MAE.
- [ ] Explain NASA S-score.
- [ ] Explain critical-zone RMSE.
- [ ] Explain overestimation ratio.
- [ ] Explain why the best RMSE model may not be the safest model.

## Research Communication

- [ ] Present the current FD001 result table.
- [ ] Interpret one failure case.
- [ ] Explain one feature importance result.
- [ ] State the next experiment and why it matters.
- [ ] State what evidence is still missing for a small paper.

