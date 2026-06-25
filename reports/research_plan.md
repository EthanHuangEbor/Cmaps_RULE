# 8-Week Research Plan

## Title

基于 NASA C-MAPSS 数据集的涡扇发动机剩余寿命预测：传统机器学习与深度时序模型对比

## Research Question

在统一预处理、相同 train/validation/test 规则和相同指标下，LSTM/GRU/1D-CNN 相比 Random Forest/XGBoost 等传统模型，是否能在 C-MAPSS RUL 预测中获得稳定优势？优势主要出现在哪些寿命区间和故障场景？

## Week-by-Week Deliverables

| Week | Focus | Deliverable |
|---|---|---|
| 1 | Research question and reading | 1-page RQ brief + 3 reading cards |
| 2 | Data and EDA | Data parser, RUL labels, sensor screening |
| 3 | Traditional baselines | Ridge/RF/XGBoost or sklearn gradient boosting metrics table |
| 4 | LSTM | Training curve and LSTM comparison table |
| 5 | GRU and 1D-CNN | Full model comparison table |
| 6 | Error analysis | 4-6 core figures and interpretation notes |
| 7 | Ablations | Window/max RUL/FD001-FD003 robustness table |
| 8 | Packaging | GitHub project, report, PPT outline, mentor materials |

## Integrity Rules

- Split validation by engine ID.
- Fit scaler only on training engines.
- Keep synthetic smoke-test data separate from NASA results.
- Report both ordinary metrics and safety-relevant overestimation behavior.
- Do not claim publication readiness unless the ablation/error analysis gives a clear contribution.
