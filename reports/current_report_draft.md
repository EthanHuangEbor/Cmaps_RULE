# 面向安全指标的 C-MAPSS 涡扇发动机剩余寿命预测模型对比与改进：阶段性技术报告初稿

**版本**：v0.1  
**日期**：2026-06-25  
**项目**：NASA C-MAPSS RUL Prediction  
**定位**：本科科研项目阶段报告，不是正式投稿稿件

## Abstract

This project studies remaining useful life (RUL) prediction for turbofan engines on the NASA C-MAPSS benchmark. Instead of treating the task as a simple regression benchmark, the study evaluates both aggregate prediction accuracy and safety-relevant behavior near failure. Under leakage-controlled preprocessing, engine-level validation splitting, capped RUL labels, and sliding-window inputs, classical machine learning baselines are compared with LSTM, GRU, and 1D-CNN sequence models on FD001 and FD003. The current results show that gradient boosting and random forest remain strong baselines on aggregate RMSE, while GRU can become competitive on FD003 when longer temporal windows are used. A lightweight safety-aware GRU loss improves FD001 late-life prediction and reduces overestimation risk, but its effect is less stable on FD003. The main research value of the project is therefore not "using LSTM", but a safety-aware comparison framework for RUL prediction.

**Keywords**: Remaining Useful Life, C-MAPSS, turbofan engine, PHM, GRU, safety-aware loss

## 摘要

本项目研究 NASA C-MAPSS 涡扇发动机退化数据集上的 Remaining Useful Life, RUL 预测问题。与普通回归任务不同，发动机 RUL 预测具有明显的安全非对称性：高估剩余寿命可能导致维护延迟，因此不能只看整体 RMSE，还需要考察接近失效阶段和高估风险。当前项目已经实现从数据处理、无泄漏划分、传统机器学习 baseline、深度时序模型、safety-aware loss、指标评估到三 seed 稳定性实验的完整闭环。结果表明，传统树模型在 FD001 和默认 FD003 设置下仍然非常强；但在 FD003 上，使用更长时间窗口的 GRU 获得了当前最好的整体 RMSE。轻量 safety-aware loss 在 FD001 上改善了 GRU 的整体误差和 critical-zone 表现，在 FD003 上主要降低 overestimation risk，但稳定性仍需进一步验证。

## 1. 研究问题

本项目关注航空发动机健康管理中的 RUL 预测。核心问题不是“深度学习是否一定更好”，而是在统一实验协议下，比较不同模型在整体误差、安全相关指标和复杂故障场景中的表现。

当前研究问题如下：

1. 在 FD001 和 FD003 上，传统机器学习模型与深度时序模型的整体误差有何差异？
2. 在接近失效阶段，哪些模型具有更低的 critical-zone RMSE？
3. 面向安全的 loss 是否能降低 RUL 高估风险，并改善晚期退化预测？
4. 窗口长度和模型容量是否会改变 GRU 在复杂故障场景 FD003 上的表现？

## 2. 数据与预处理

数据来自 NASA PCoE Turbofan Engine Degradation Simulation Data Set。该数据由 C-MAPSS 仿真生成，包含多个 run-to-failure 的发动机单元、运行 cycle、工况变量和传感器通道。当前报告使用 FD001 和 FD003：

- FD001：单工况、单故障模式，适合作为入门 baseline。
- FD003：单工况、双故障模式，比 FD001 更复杂，更适合检验深度时序模型是否有优势。

预处理策略如下：

- RUL label 使用 piecewise capped RUL，`max_rul = 130`。
- train/validation 按 engine ID 划分，避免同一台发动机的窗口同时出现在训练和验证中。
- scaler 只在 training engines 上 fit，再 transform validation/test，避免 data leakage。
- 默认 sliding window 为 30 cycles，测试集按官方式评价只取每台发动机最后一个窗口。
- focused ablation 中额外验证 window size 50、hidden size 128 和 safety-aware loss。

## 3. 方法

传统模型包括 Ridge、Random Forest 和 Gradient Boosting。传统模型输入为窗口统计特征，包括 mean、std、last、delta 和 slope。深度模型包括 LSTM、GRU 和 1D-CNN，输入形状为 `[batch, window, sensors]`。

默认 GRU/LSTM 设置为 hidden size 64、1 层、dropout 0.2、Adam learning rate 1e-3、batch size 128、early stopping patience 8 或 10。focused ablation 中测试了：

- `window50_h64_l1`：窗口长度从 30 增加到 50。
- `capacity_h128_l1_w30`：hidden size 从 64 增加到 128。
- `safety_w1p5_h64_l1_w30`：使用 safety-aware MSE，对低 RUL 样本和高估误差加权，权重为 1.5。

评价指标包括：

- RMSE：整体误差，对大误差敏感。
- MAE：平均绝对误差，更直观。
- NASA S-score：对高估和低估使用非对称惩罚。
- Critical RMSE <= 50：只评价 RUL <= 50 的接近失效区域。
- Overestimation ratio：预测值大于真实 RUL 的比例，用于衡量模型是否倾向危险高估。

## 4. 实验结果

### 4.1 FD001 主结果

| Model / Setting | RMSE mean ± std | MAE | NASA S-score | Critical RMSE <=50 | Overestimation ratio |
|---|---:|---:|---:|---:|---:|
| Gradient Boosting | 12.81 ± 0.38 | 9.83 | 247.46 | 5.60 | 0.607 |
| Random Forest | 13.01 ± 0.57 | 9.62 | 258.65 | 6.21 | 0.617 |
| GRU + safety_w1p5 | 13.99 ± 0.26 | 10.01 | 312.82 | 4.94 | 0.563 |
| GRU | 15.27 ± 0.64 | 11.33 | 483.23 | 5.71 | 0.587 |
| LSTM | 15.60 ± 0.51 | 11.45 | 563.57 | 6.52 | 0.627 |
| Ridge | 16.92 ± 0.11 | 13.33 | 510.32 | 16.68 | 0.580 |
| CNN | 22.47 ± 1.17 | 16.49 | 3867.77 | 25.42 | 0.563 |

FD001 上，Gradient Boosting 和 Random Forest 仍然是最强整体 baseline。轻量 safety-aware GRU 没有超过树模型，但相比普通 GRU 明显改善：RMSE 从 15.27 降到 13.99，critical RMSE 从 5.71 降到 4.94，S-score 也下降。这个结果支持一个较稳健的阶段性结论：在简单故障场景 FD001 中，传统树模型整体最强，但 safety-aware GRU 对接近失效阶段更有帮助。

### 4.2 FD003 主结果

| Model / Setting | RMSE mean ± std | MAE | NASA S-score | Critical RMSE <=50 | Overestimation ratio |
|---|---:|---:|---:|---:|---:|
| GRU window50 | 12.96 ± 0.48 | 9.30 | 319.96 | 5.50 | 0.533 |
| Gradient Boosting | 13.21 ± 0.35 | 9.67 | 311.85 | 5.53 | 0.573 |
| Random Forest | 13.98 ± 0.25 | 10.14 | 343.90 | 4.76 | 0.583 |
| GRU + safety_w1p5 | 14.07 ± 1.24 | 9.96 | 413.74 | 5.25 | 0.437 |
| GRU hidden128 | 14.35 ± 1.48 | 10.48 | 407.65 | 5.98 | 0.577 |
| LSTM | 14.41 ± 1.57 | 10.22 | 550.26 | 5.09 | 0.507 |
| GRU | 15.24 ± 1.45 | 10.55 | 622.27 | 6.19 | 0.553 |
| Ridge | 18.02 ± 0.37 | 14.90 | 627.31 | 15.87 | 0.600 |
| CNN | 23.76 ± 0.42 | 17.25 | 3533.32 | 24.91 | 0.570 |

FD003 的结果更有科研价值。默认 GRU 不如传统树模型，但 window size 从 30 增加到 50 后，GRU 的 RMSE 达到 12.96，超过 Gradient Boosting 的 13.21 和 Random Forest 的 13.98。这说明在双故障模式场景中，GRU 可能确实需要更长的历史窗口来捕捉退化趋势。

不过，window50 并不是所有指标都最好。Random Forest 的 critical RMSE <=50 仍然最低，为 4.76；safety_w1p5 的 overestimation ratio 最低，为 0.437。这说明 FD003 上存在明显的指标 trade-off：window50 最适合整体误差，Random Forest 更适合 critical-zone，safety-aware GRU 更适合降低危险高估倾向。

### 4.3 Focused ablation 结论

| Subset | Focused setting | Seeds | RMSE mean ± std | Critical RMSE <=50 | Overestimation ratio |
|---|---|---:|---:|---:|---:|
| FD001 | safety_w1p5_h64_l1_w30 | 3 | 13.99 ± 0.26 | 4.94 | 0.563 |
| FD003 | window50_h64_l1 | 3 | 12.96 ± 0.48 | 5.50 | 0.533 |
| FD003 | safety_w1p5_h64_l1_w30 | 3 | 14.07 ± 1.24 | 5.25 | 0.437 |
| FD003 | capacity_h128_l1_w30 | 3 | 14.35 ± 1.48 | 5.98 | 0.577 |

focused ablation 支持三点判断：

1. FD001 上，轻量 safety loss 是有效改进，比普通 GRU 更稳。
2. FD003 上，window50 是目前最强的 GRU 改进方向，且三 seed 方差较小。
3. hidden size 128 的 seed 42 表现很好，但 seed 43/44 明显退化，说明单次漂亮结果不可靠。

## 5. 讨论

当前项目最重要的发现是：深度模型并不会因为“更高级”而自然超过传统模型。在 FD001 上，窗口统计特征加树模型已经很强，说明该子集中的退化模式可以被均值、斜率、delta 等手工特征较好捕捉。对于本科科研项目而言，这反而是一个很好的训练：必须尊重 strong baseline，不能只堆 LSTM/GRU。

FD003 的结果更接近小论文主线。默认 GRU 不强，但 window50 后明显提升，说明复杂故障模式下更长时间上下文可能更重要。这个发现可以发展成一个研究论点：深度序列模型的价值不在默认配置，而在于它能利用更长退化历史；但这种优势需要通过多 seed、critical-zone 和 overestimation risk 一起验证。

safety-aware loss 的结果也有价值。FD001 上，`safety_w1p5` 同时改善 RMSE、S-score 和 critical-zone error。FD003 上，它没有取得最佳 RMSE，但显著降低 overestimation ratio。这说明 safety-aware loss 不是单纯刷榜工具，而是改变模型错误偏好的方法。对于航空发动机维护场景，这比单一 RMSE 更贴近工程安全问题。

CNN 当前表现较差，尤其 S-score 和 critical-zone error 明显不理想。阶段性解释是：当前 1D-CNN 结构可能只捕捉局部模式，未能充分建模长时依赖；也可能需要更合适的归一化、残差结构或训练策略。当前报告不把 CNN 失败包装成理论结论，只把它作为当前配置下的实验现象。

## 6. 局限

当前工作仍有明显限制：

- C-MAPSS 是仿真数据，不等价于真实航空发动机全寿命运行数据。
- 目前只使用 FD001 和 FD003，尚未覆盖多工况 FD002/FD004。
- safety-aware loss 只测试了少数权重，尚未系统搜索。
- focused ablation 虽然完成三 seed，但还缺少 per-engine error 图、critical-zone boxplot 和 saliency/occlusion 分析。
- 参考文献部分还需要进一步核对 DOI、版本和引用格式，当前报告不应直接作为投稿稿。

## 7. 下一步计划

为了把项目升级成小论文雏形，建议下一阶段优先做五件事：

1. 固定 FD003 `window50_h64_l1` 作为深度模型主改进配置，补充预测散点图和 per-engine error 图。
2. 对比 FD003 `window50` 与 Random Forest 的 late-life error，判断二者在 critical-zone 的差异是否集中在少数 engine。
3. 测试一个小型组合实验：`window50 + safety_w1p5`，先跑 seed 42，如果有效再扩展三 seed。
4. 对 Random Forest / Gradient Boosting 做 feature importance，解释 mean、slope、delta 为什么有效。
5. 写 8-12 篇参考文献矩阵，重点读 C-MAPSS、LSTM RUL、CNN RUL、安全评价指标和 PHM benchmark。

小论文候选题目可以定为：

> Safety-Aware Evaluation of Classical and Deep Sequence Models for Turbofan Engine RUL Prediction on C-MAPSS

更准确的贡献表述是：

> 本研究不是提出全新 SOTA 模型，而是在严格避免 data leakage 的前提下，比较传统模型和深度时序模型在整体误差、接近失效阶段误差与高估风险上的差异，并初步验证 safety-aware loss 与长窗口 GRU 对安全相关 RUL 预测的影响。

## 8. 可复现实验命令

主实验矩阵：

```powershell
python scripts\run_research_matrix.py --subsets FD001 --seeds 42 43 44 --deep-epochs 60 --skip-safety --skip-existing
python scripts\run_research_matrix.py --subsets FD003 --seeds 42 43 44 --deep-epochs 60 --skip-safety --skip-existing
python scripts\run_research_matrix.py --subsets FD001 FD003 --seeds 42 43 44 --deep-epochs 60 --skip-ml --skip-deep --skip-existing
```

focused ablation：

```powershell
python scripts\run_deep_ablation_matrix.py --subsets FD001 --seeds 42 43 44 --models gru --jobs safety_w1p5_h64_l1_w30 --skip-existing
python scripts\run_deep_ablation_matrix.py --subsets FD003 --seeds 42 43 44 --models gru --jobs window50_h64_l1 capacity_h128_l1_w30 safety_w1p5_h64_l1_w30 --skip-existing
```

## 9. 数据、伦理与 AI 使用声明

本项目仅使用 NASA 公开仿真数据，不涉及人体受试者、隐私数据或真实发动机运行敏感数据。NASA 原始数据不随仓库重新分发，用户需要自行从官方页面下载。

本报告在 AI 辅助下撰写，所有实验命令、代码改动和数值结果均来自本地项目输出文件。最终用于导师申请、课程展示或投稿前，需要人工复核所有引用、图表和结论。

## References and Source Notes

- NASA PCoE Data Set Repository. Turbofan Engine Degradation Simulation Data Set. https://www.nasa.gov/intelligent-systems-division/discovery-and-systems-health/pcoe/pcoe-data-set-repository/
- Saxena, A., Goebel, K., Simon, D., & Eklund, N. Damage propagation modeling for aircraft engine run-to-failure simulation. Citation details to verify before formal submission.
- Zheng, S., Ristovski, K., Farahat, A., & Gupta, C. Long Short-Term Memory Network for Remaining Useful Life Estimation. Citation details and DOI to verify before formal submission.
- Babu, G. S., Zhao, P., & Li, X.-L. Deep Convolutional Neural Network Based Regression Approach for Estimation of Remaining Useful Life. https://doi.org/10.1007/978-3-319-32025-0_14
