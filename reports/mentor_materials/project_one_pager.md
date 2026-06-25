# Project One-Pager

## Project

基于 NASA C-MAPSS 数据集的涡扇发动机剩余寿命预测：传统机器学习与深度时序模型对比

## Motivation

我希望从航空发动机健康管理问题入手，建立一个完整的机器学习科研闭环：公开数据、可复现预处理、baseline、深度时序模型、指标对比和误差分析。这个项目连接了我对 AI/机器学习、机器人/控制和航空发动机的兴趣。

## What I Built

- NASA C-MAPSS 数据解析与 RUL 标签构造。
- Engine-level validation split，避免窗口级 data leakage。
- Ridge、Random Forest、XGBoost/sklearn GradientBoosting baseline。
- LSTM、GRU、1D-CNN 深度时序模型。
- RMSE、MAE、NASA S-score、critical-zone RMSE 和 overestimation ratio 评价。

## Current / Expected Findings

待填入真实实验结果。重点关注深度模型是否只在普通 RMSE 上更好，还是在接近失效阶段也更可靠。

## Why It Matters

航空发动机 RUL 预测不只是普通回归任务。过高估计剩余寿命可能带来更严重的安全风险，因此项目会单独分析 overestimation 和 critical-zone performance。

## Next Step

希望在老师指导下进一步扩展到安全代价函数、跨工况泛化或可解释性分析。
