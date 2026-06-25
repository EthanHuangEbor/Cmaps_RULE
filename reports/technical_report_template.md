# Technical Report Template

## Title

基于 NASA C-MAPSS 数据集的涡扇发动机剩余寿命预测：传统机器学习与深度时序模型对比

## Abstract

本文研究 NASA C-MAPSS 涡扇发动机退化数据集上的 Remaining Useful Life (RUL) 预测问题。实验在统一数据预处理、engine-level validation split、相同评价指标和相同 RUL label 构造下，对比 Ridge、Random Forest、XGBoost/HistGradientBoosting、LSTM、GRU 和 1D-CNN。除 RMSE 与 MAE 外，本文重点报告 NASA S-score、critical-zone RMSE 和 overestimation ratio，以评估模型在接近失效阶段的安全相关表现。

## 1. Background

- 航空发动机健康管理与 predictive maintenance 的意义。
- RUL 预测在维修决策、风险控制和成本优化中的作用。
- C-MAPSS 作为公开 benchmark 的优点和局限。

## 2. Data

- Dataset: NASA C-MAPSS Turbofan Engine Degradation Simulation Data Set.
- Primary subset: FD001.
- Extension subset: FD003.
- Features: 3 operational settings and 21 sensor channels, after near-constant feature screening.
- Label: piecewise capped RUL with `max_rul = 130`.

## 3. Methods

### 3.1 Preprocessing

- Engine-level train/validation split.
- Standardization fitted only on training engines.
- Sliding windows with window size 30 and stride 1.

### 3.2 Traditional ML

- Ridge.
- Random Forest.
- XGBoost when available, otherwise scikit-learn GradientBoosting fallback.
- Summary window features: mean, std, last, delta, slope.

### 3.3 Deep Sequence Models

- LSTM.
- GRU.
- 1D-CNN.
- Training: Adam, learning rate 1e-3, early stopping.

## 4. Evaluation

- RMSE.
- MAE.
- NASA S-score.
- Critical-zone RMSE for RUL <= 30 and RUL <= 50.
- Overestimation ratio.

## 5. Results

Insert tables from `reports/tables/*/metrics.csv`.

## 6. Error Analysis

- Which engines are hardest?
- Do models fail more in the late-life region?
- Are models overestimating RUL?
- Which sensors/features appear important?

## 7. Limitations

- C-MAPSS is simulated, not real fleet data.
- Benchmark novelty is limited.
- Hyperparameter search is intentionally modest.
- Sensor interpretability is approximate.

## 8. Future Work

- Safety-weighted loss based on S-score.
- Attention-LSTM or temporal convolution improvements.
- FD001/FD003 cross-subset generalization.
- EDF thrust bench as future hardware extension.
