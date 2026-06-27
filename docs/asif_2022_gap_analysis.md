# Gap Analysis: Asif et al. 2022 vs. Current Project

Reference:

Owais Asif et al., "A Deep Learning Model for Remaining Useful Life Prediction
of Aircraft Turbofan Engine on C-MAPSS Dataset," IEEE Access, 2022. DOI:
`10.1109/ACCESS.2022.3203406`.

## What Asif et al. Contribute

- A C-MAPSS LSTM pipeline evaluated on FD001-FD004.
- Correlation-based sensor selection.
- Moving median filtering for noisy sensor sequences.
- Improved piecewise linear degradation labeling to estimate the degradation
  starting point.
- RMSE and NASA score reporting across all four subsets.

## Where Our Current Project Is Stronger

- Stronger classical baselines: Ridge, Random Forest, Gradient Boosting, and
  optional XGBoost.
- Leakage-aware protocol: engine-level validation split and train-only scaler
  fitting.
- Multi-seed reporting with mean and standard deviation.
- Safety-oriented metrics: critical-zone RMSE, overestimation ratio, and
  overestimation magnitude.
- Explicit negative results and cautious bootstrap-style interpretation.

## Where We Must Improve Before Submission

- FD002/FD004 representative evidence is now complete; clearly mark it as a representative GRU/Safety-GRU stress matrix rather than a full architecture search.
- Treat label construction and preprocessing as experimental variables, not
  fixed background choices.
- Add uncertainty calibration so the model can express when it is unreliable.
- Connect predictions to maintenance decision cost.
- Add sensor perturbation and cross-subset stress tests.

## Revised Paper Claim

Do not compete with Asif et al. on "best LSTM RMSE". The stronger claim is:

> Existing C-MAPSS studies often optimize point-prediction accuracy. We show
> that model ranking changes when RUL systems are evaluated by late-life safety,
> optimistic overestimation, uncertainty calibration, sensor robustness, and
> maintenance-trigger decision cost.

