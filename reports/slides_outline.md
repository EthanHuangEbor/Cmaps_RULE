# 8-10 Page Presentation Outline

## 1. Title

基于 NASA C-MAPSS 数据集的涡扇发动机剩余寿命预测

## 2. Motivation

RUL prediction matters for predictive maintenance and safety-aware decision making.

## 3. Dataset

NASA C-MAPSS, FD001 first, FD003 extension.

## 4. Method Pipeline

Data parsing -> RUL label -> engine-level split -> scaling -> windowing -> models -> metrics.

## 5. Models

Ridge, Random Forest, XGBoost/HistGradientBoosting, LSTM, GRU, 1D-CNN.

## 6. Metrics

RMSE, MAE, NASA S-score, critical-zone RMSE, overestimation ratio.

## 7. Main Results

Insert metrics table and prediction scatter.

## 8. Error Analysis

Per-engine error and critical-zone behavior.

## 9. Findings and Limitations

What is reproducible, what is uncertain, what still needs testing.

## 10. Next Step

Safety-weighted loss, cross-subset robustness, interpretability, possible hardware extension.

