# NASA C-MAPSS RUL Prediction / NASA C-MAPSS 剩余寿命预测研究

This repository is a reproducible research codebase for Remaining Useful Life
(RUL) prediction on the NASA C-MAPSS turbofan engine benchmark. It started as a
classical-versus-deep-learning comparison and is now moving toward a
safety-aware and policy-oriented evaluation of RUL models.

本仓库是一个面向 NASA C-MAPSS 涡扇发动机退化数据集的剩余寿命
（Remaining Useful Life, RUL）预测研究项目。项目最初比较传统机器学习和深度
序列模型，现在进一步关注临近失效阶段的安全风险、过度乐观预测、不确定性、
跨子集迁移、传感器扰动鲁棒性和维护决策成本。

## Research Question / 研究问题

English:

> Do RUL models remain useful when judged not only by aggregate RMSE, but also
> by late-life safety, optimistic overestimation risk, uncertainty calibration,
> cross-subset transfer, sensor robustness, and maintenance-trigger decisions?

中文：

> 当评价标准不再只是整体 RMSE，而是进一步包含临近失效安全性、过度乐观预测
> 风险、不确定性校准、跨子集迁移、传感器鲁棒性和维护触发决策时，RUL 模型
> 是否仍然具有实际研究价值？

The current manuscript positioning is modest: this project does not claim a new
state-of-the-art architecture. Its contribution is a reproducible, safety-aware
benchmarking workflow for C-MAPSS FD001/FD003, with extension hooks for FD002,
FD004, uncertainty, robustness, and decision simulation.

当前论文定位保持克制：本项目不宣称提出新的 SOTA 架构，而是提供一个可复现
的、安全感知的 C-MAPSS FD001/FD003 评估流程，并为 FD002/FD004、不确定性、
鲁棒性和维护决策模拟保留扩展接口。

## What Is Included / 仓库内容

- Classical baselines: Ridge, Random Forest, optional XGBoost, and a
  scikit-learn Gradient Boosting fallback.
- Deep sequence models: LSTM, GRU, and 1D-CNN implemented with PyTorch.
- Metrics: RMSE, MAE, NASA S-score, critical-zone RMSE, overestimation ratio,
  and overestimation magnitude.
- Safety-aware losses: critical-zone, asymmetric, and combined safety MSE
  variants.
- Experiment runners for multi-seed matrices, focused ablations, uncertainty,
  domain shift, sensor robustness, and maintenance decision simulation.
- Paper artifacts under `reports/paper/` and literature-review artifacts under
  `reports/review/`.

中文概览：

- 传统基线：Ridge、Random Forest、可选 XGBoost，以及 scikit-learn
  Gradient Boosting 备用模型。
- 深度模型：基于 PyTorch 的 LSTM、GRU 和 1D-CNN。
- 指标：RMSE、MAE、NASA S-score、critical-zone RMSE、overestimation ratio
  和 overestimation magnitude。
- 安全感知损失：critical-zone、asymmetric 以及 combined safety MSE。
- 实验脚本：多随机种子矩阵、集中消融、不确定性、domain shift、传感器扰动
  鲁棒性和维护决策模拟。
- 论文材料位于 `reports/paper/`，综述材料位于 `reports/review/`。

## Repository Layout / 目录结构

```text
configs/                  Experiment defaults and ablation plans
data/raw/                 Local C-MAPSS files; official txt data are ignored
docs/                     Research plans and gap analysis notes
notebooks/                Notebook guidance
reports/paper/            Manuscript source, generated paper figures, tables, reviews
reports/review/           Literature review manuscript, figures, bibliography, review notes
reports/tables/           Local generated experiment outputs; ignored by Git
reports/figures/          Local generated figures; ignored by Git
scripts/                  Data helpers, experiment runners, paper figure builders
src/rul_prediction/       Python package
tests/                    Lightweight unit tests
work/                     Scratch/smoke-test outputs; ignored by Git
```

`reports/tables/`, `reports/figures/`, `work/`, virtual environments, Python
caches, and official C-MAPSS raw text files are treated as local generated or
local-only assets.

`reports/tables/`、`reports/figures/`、`work/`、虚拟环境、Python 缓存以及官方
C-MAPSS 原始 txt 数据都被视为本地生成或本地自备内容。

## Data / 数据

Download the official Turbofan Engine Degradation Simulation Data Set from the
NASA Prognostics Center of Excellence data repository:

<https://www.nasa.gov/intelligent-systems-division/discovery-and-systems-health/pcoe/pcoe-data-set-repository/>

Place the files under `data/raw/`:

```text
data/raw/train_FD001.txt
data/raw/test_FD001.txt
data/raw/RUL_FD001.txt
data/raw/train_FD003.txt
data/raw/test_FD003.txt
data/raw/RUL_FD003.txt
```

FD002 and FD004 can also be placed in the same directory for multi-condition
experiments. The official C-MAPSS txt files are intentionally ignored by Git.

请从 NASA PCoE 官方页面下载 C-MAPSS 数据，并将文件放入 `data/raw/`。官方
txt 数据不会随仓库分发。项目提供 `scripts/make_demo_data.py` 用于生成合成
toy data，只适合 smoke test，不能作为论文实验依据。

## Setup / 环境安装

Python 3.10 or newer is required.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -U pip
python -m pip install -e .
```

For development tests:

```powershell
python -m pip install -e ".[dev]"
```

If `xgboost` is unavailable, the baseline workflow still runs with
scikit-learn Gradient Boosting.

中文说明：建议使用 Python 3.10+，通过 editable install 安装本项目。若本机
安装 XGBoost 不方便，传统基线脚本会自动使用 scikit-learn 的 Gradient
Boosting 作为备用方案。

## Quick Smoke Test / 快速烟雾测试

This verifies the pipeline shape with synthetic toy data. It is not a research
experiment.

```powershell
python scripts\make_demo_data.py --out-dir work\demo_raw --subset FD001
python -m rul_prediction.train_ml --data-dir work\demo_raw --subset FD001 --out-dir work\demo_results\ml --window-size 20
python -m rul_prediction.train_deep --data-dir work\demo_raw --subset FD001 --out-dir work\demo_results\deep --models lstm --epochs 2 --window-size 20
```

中文说明：上述命令只检查数据流、训练入口和输出格式是否能跑通。合成数据不能
用于论文结果。

## Core Experiments / 核心实验

### FD001 baseline / FD001 基线

```powershell
python -m rul_prediction.train_ml --data-dir data\raw --subset FD001 --out-dir reports\tables\fd001_ml
python -m rul_prediction.train_deep --data-dir data\raw --subset FD001 --out-dir reports\tables\fd001_deep --models lstm gru cnn
python -m rul_prediction.plots --metrics reports\tables\fd001_ml\metrics.csv reports\tables\fd001_deep\metrics.csv --predictions reports\tables\fd001_ml\predictions.csv reports\tables\fd001_deep\predictions.csv --out-dir reports\figures
```

### Multi-seed matrix / 多随机种子矩阵

```powershell
python scripts\run_research_matrix.py --subsets FD001 --seeds 42 43 44 --deep-epochs 60 --skip-safety --skip-existing
python scripts\run_research_matrix.py --subsets FD003 --seeds 42 43 44 --deep-epochs 60 --skip-safety --skip-existing
python scripts\run_research_matrix.py --subsets FD001 FD003 --seeds 42 43 44 --deep-epochs 60 --skip-ml --skip-deep --skip-existing
```

Use `--deep-models` to restrict the deep models in the matrix run:

```powershell
python scripts\run_research_matrix.py --subsets FD001 --seeds 42 --deep-models gru --deep-epochs 60 --skip-existing
```

### Focused deep ablations / 深度模型集中消融

```powershell
python scripts\run_deep_ablation_matrix.py --subsets FD001 FD003 --seeds 42 --models gru --skip-existing
```

Run selected jobs only:

```powershell
python scripts\run_deep_ablation_matrix.py --subsets FD001 --seeds 42 43 44 --models gru --jobs safety_w1p5_h64_l1_w30 --skip-existing
python scripts\run_deep_ablation_matrix.py --subsets FD003 --seeds 42 43 44 --models gru --jobs window50_h64_l1 capacity_h128_l1_w30 safety_w1p5_h64_l1_w30 --skip-existing
```

Recent experiment runners write `job_name` into metrics, predictions, and
training histories so that aggregate tables can distinguish focused ablation
settings.

新的实验脚本会在 metrics、predictions 和 training history 中写入 `job_name`，
便于聚合结果时区分不同消融任务。

## Safety and Policy-Oriented Extensions / 安全与维护决策扩展

Fast smoke commands:

```powershell
$env:PYTHONPATH="src"
python scripts\run_uncertainty.py --data-dir data\raw --subset FD001 --method mc_dropout --model gru --epochs 1 --patience 1 --mc-samples 3 --batch-size 512 --out-dir reports\tables\smoke_uncertainty
python scripts\run_decision_simulation.py --predictions reports\tables\smoke_uncertainty\predictions.csv --out-dir reports\tables\smoke_decision
python scripts\run_domain_shift.py --data-dir data\raw --source-subset FD001 --target-subset FD003 --model ridge --out-dir reports\tables\smoke_domain
python scripts\run_sensor_robustness.py --data-dir data\raw --subset FD001 --model ridge --noise-levels 0.05 --mask-fractions 0.1 --out-dir reports\tables\smoke_robustness
python scripts\make_upgrade_figures.py --metrics reports\tables\smoke_uncertainty\metrics.csv --interval-metrics reports\tables\smoke_uncertainty\interval_metrics.csv --decision-metrics reports\tables\smoke_decision\decision_metrics.csv --robustness-metrics reports\tables\smoke_robustness\robustness_metrics.csv --out-dir reports\figures\smoke_upgrade
```

Full experiments should replace smoke settings with longer training, multiple
seeds, and the intended FD subsets.

完整实验应使用更长训练轮数、多随机种子和目标 FD 子集替代 smoke 参数。

## Paper and Review Artifacts / 论文与综述材料

Paper draft:

- `reports/paper/main.tex`
- `reports/paper/references.bib`
- `reports/paper/figures/`
- `reports/paper/arxiv_metric_summary.csv`
- `reports/paper/safety_tradeoff_summary.csv`
- `reports/paper/paired_bootstrap_rmse.csv`

Literature review:

- `reports/review/aero_engine_dl_review.md`
- `reports/review/literature_matrix.csv`
- `reports/review/references.bib`
- `reports/review/figures/`
- `reports/review/ieee/aero_engine_rul_ieee_review.tex`
- `reports/review/ieee/aero_engine_rul_ieee_review.pdf`

论文草稿位于 `reports/paper/`。综述稿和 IEEE 风格排版材料位于
`reports/review/`。这些材料记录了项目当前研究推进状态，不代表已经过正式
同行评审。

## arXiv Figure and Source Workflow / arXiv 图表与源码包流程

```powershell
python -m rul_prediction.aggregate --root reports\tables\deep_ablations --out-dir reports\tables\deep_ablations\summary
python -m rul_prediction.error_analysis --root reports\tables\deep_ablations --out-dir reports\tables\deep_ablations\summary
python scripts\make_arxiv_figures.py
python scripts\package_arxiv_source.py
```

The figure builder reads local experiment outputs under `reports/tables/` and
writes manuscript figures and summary CSVs under `reports/paper/`.

图表生成脚本会读取本地 `reports/tables/` 中的实验输出，并将论文图表和摘要
CSV 写入 `reports/paper/`。

## Testing / 测试

```powershell
python -m pytest -q
```

The test suite currently focuses on lightweight unit coverage for metrics,
windowing, losses, uncertainty utilities, robustness perturbations, decision
simulation, and XAI helpers.

当前测试主要覆盖轻量单元逻辑：指标、窗口化、损失函数、不确定性工具、传感器
扰动、维护决策模拟和 XAI 辅助函数。

## Research Integrity / 研究完整性说明

- Fit scalers only on training engines, then transform validation/test data.
- Split train/validation by engine ID, not by individual windows.
- Never mix synthetic smoke data with official C-MAPSS experiment results.
- Report late-life and overestimation metrics alongside RMSE and MAE.
- Treat C-MAPSS as a simulation benchmark, not direct evidence for real fleet
  maintenance policy.
- Do not claim state-of-the-art performance without broader model selection,
  stronger baselines, and independent validation.

中文要点：

- 归一化器只能在训练发动机上拟合，再用于 validation/test。
- train/validation 应按 engine ID 切分，而不是按窗口随机切分。
- 合成 smoke data 不能混入正式 C-MAPSS 实验结果。
- 除 RMSE/MAE 外，应同时报告临近失效和过度乐观预测指标。
- C-MAPSS 是仿真基准，不等同于真实机队维护策略验证。
- 若没有更强基线、更全面调参和独立验证，不应宣称 SOTA。

## Current Direction / 当前推进方向

The next project phase is to consolidate FD001/FD003 evidence, add clearer
FD002/FD004 positioning, improve uncertainty and robustness experiments, and
keep the paper framed as a reproducible student research benchmark.

下一阶段重点是巩固 FD001/FD003 证据，明确 FD002/FD004 的实验定位，继续完善
不确定性与鲁棒性实验，并将论文表述保持在“可复现学生研究基准”的合理范围内。
