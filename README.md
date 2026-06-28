# NASA C-MAPSS RUL Prediction / NASA C-MAPSS 剩余寿命预测

This repository contains a reproducible research workflow for Remaining Useful Life (RUL) prediction on the NASA C-MAPSS turbofan benchmark. The project has evolved from a model-comparison scaffold into two connected research tracks.

本仓库是一个面向 NASA C-MAPSS 涡扇发动机退化数据集的剩余寿命（Remaining Useful Life, RUL）预测研究项目。当前项目已经从基础模型比较推进到两条相互衔接的研究主线。

1. **Paper 1: Safety-oriented C-MAPSS evaluation.** A benchmark-style paper showing that aggregate RMSE is not enough for model selection across FD001-FD004.
2. **Paper 2: Cycle-consistent safety-oriented Dual-LSTM.** A method-response paper testing whether a Dual-LSTM training branch can shape late-life and overestimation-risk behavior under the Paper 1 protocol.

## Current Status / 当前进度

Latest synced main-branch state: `6e0c7d3 Complete Paper 2 Dual-LSTM full matrix`.

当前 `main` 分支已经同步到 `6e0c7d3 Complete Paper 2 Dual-LSTM full matrix`。

## Paper 1: Safety-Oriented Evaluation / 第一篇：安全导向评估

Working title:

> Safety-Oriented Evaluation of Classical and Deep Sequence Models for Aero-Engine RUL Prediction on C-MAPSS

Core question:

> On FD001-FD004, is the aggregate RMSE-best model also the best model for late-life error and optimistic overestimation risk?

Current answer: **no**. RMSE-best, critical-zone-best, overestimation-risk-best, and SARBI-best rankings often differ.

当前结论：**不是**。在 FD001-FD004 上，整体 RMSE 最优模型、临近失效误差最优模型、过度乐观预测风险最优模型，以及 SARBI 综合指标最优模型经常并不一致。

Completed evidence:

- Representative FD001-FD004 matrix for Ridge, Random Forest, Gradient Boosting, GRU, and Safety-GRU.
- Full GRU safety-loss ablation: 4 subsets x 3 seeds x 8 jobs = 96 jobs.
- Leakage-aware protocol: engine-level validation split, train-only scaling, capped RUL labels, 30-cycle windows, last-window test evaluation, seeds 42/43/44.
- Metrics: RMSE, MAE, NASA S-score, Critical RMSE30/50, overestimation ratio, and overestimation magnitude.
- SARBI reporting layer: a transparent relative composite score combining aggregate accuracy, late-life error, and optimistic-risk behavior.
- Bootstrap checks for RMSE-best versus SARBI-best comparisons.

Key files:

- `docs/research_status.md`
- `reports/progress_roadmap_2026-06-28.md`
- `reports/paper/main.tex`
- `reports/paper/figure_table_manifest.md`
- `reports/paper/paper_value_trace.csv`
- `scripts/make_safety_benchmark_outputs.py`
- `scripts/audit_paper_submission.py`

## Paper 2: Dual-LSTM Method Response / 第二篇：Dual-LSTM 方法回应

Working title:

> Cycle-Consistent Safety-Oriented Dual-LSTM for Aero-Engine RUL Prediction

Paper 2 is separate from Paper 1. It is a method-response project that uses Paper 1's safety-oriented protocol to evaluate a cycle-consistent Dual-LSTM.

第二篇与第一篇分开定位。它不是 Paper 1 的一部分，而是基于 Paper 1 的安全导向评估协议，测试 cycle-consistent Dual-LSTM 是否能改善临近失效和过度乐观预测风险。

Implemented method:

- Current-window RUL branch: `X_t -> z_t -> y_hat_t`.
- Target-conditioned transition branch: `(z_t, horizon k) -> z_hat_{t+k}`.
- Cycle consistency between predicted future state and actual future-window supervision during training.
- Latent consistency and monotonic regularization.
- Test-time inference uses only the current last window; future windows are training-only regularization signals.

Completed evidence:

- Full matrix: FD001-FD004 x 3 seeds x 4 jobs = 48 jobs.
- Jobs: LSTM baseline, Dual-LSTM no-cycle, Dual-LSTM cycle, and Dual-LSTM cycle safety-w2.
- Output schema remains compatible with existing aggregation: `metrics.csv`, `predictions.csv`, `training_history.csv`, `selected_features.csv`.
- Claim gates in `reports/paper2/claim_evidence_map.csv` are marked pass.
- Paper-facing figures and tables are generated under `reports/paper2/`.

Key files:

- `docs/dual_lstm_method_spec.md`
- `src/rul_prediction/models_dual_lstm.py`
- `src/rul_prediction/train_dual_lstm.py`
- `scripts/run_dual_lstm_matrix.py`
- `scripts/make_dual_lstm_paper2_outputs.py`
- `scripts/make_paper2_analysis_outputs.py`
- `scripts/make_paper2_submission_package.py`
- `reports/paper2/main.tex`
- `reports/paper2/submission_readiness_checklist.md`

## Repository Layout / 目录结构

```text
configs/                  Experiment defaults and ablation plans
data/raw/                 Local NASA C-MAPSS files; official txt/PDF data ignored
docs/                     Research status, method specs, and gap analysis
notebooks/                Notebook guidance
reports/paper/            Paper 1 manuscript, figures, tables, value traces
reports/paper2/           Paper 2 Dual-LSTM manuscript, figures, tables, audits
reports/review/           Literature review manuscript and supporting figures
reports/tables/           Local generated experiment outputs; ignored by Git
reports/figures/          Local generated figures; ignored by Git
scripts/                  Data helpers, experiment runners, paper-output builders
src/rul_prediction/       Python package
tests/                    Lightweight unit tests
work/                     Scratch and smoke-test outputs; ignored by Git
```

## Data / 数据

Download the official Turbofan Engine Degradation Simulation Data Set from the NASA Prognostics Center of Excellence data repository:

<https://www.nasa.gov/intelligent-systems-division/discovery-and-systems-health/pcoe/pcoe-data-set-repository/>

Place the files under `data/raw/`:

```text
data/raw/train_FD001.txt
data/raw/test_FD001.txt
data/raw/RUL_FD001.txt
data/raw/train_FD002.txt
data/raw/test_FD002.txt
data/raw/RUL_FD002.txt
data/raw/train_FD003.txt
data/raw/test_FD003.txt
data/raw/RUL_FD003.txt
data/raw/train_FD004.txt
data/raw/test_FD004.txt
data/raw/RUL_FD004.txt
```

Official NASA data files are not redistributed by this repository. Synthetic toy data generated by `scripts/make_demo_data.py` are only for smoke tests and must not be used as research evidence.

本仓库不分发 NASA 官方原始数据。`scripts/make_demo_data.py` 生成的合成 toy data 只用于 smoke test，不能作为正式论文实验依据。

## Setup / 环境安装

Python 3.10 or newer is required.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -U pip
python -m pip install -e ".[dev]"
```

If `xgboost` is unavailable, the classical baseline workflow still runs with scikit-learn Gradient Boosting.

如果本机暂时无法安装 XGBoost，传统基线仍可使用 scikit-learn Gradient Boosting 继续运行。

## Quick Smoke Test / 快速烟雾测试

This verifies the pipeline shape with synthetic data. It is not a research run.

```powershell
python scripts\make_demo_data.py --out-dir work\demo_raw --subset FD001
python -m rul_prediction.train_ml --data-dir work\demo_raw --subset FD001 --out-dir work\demo_results\ml --window-size 20
python -m rul_prediction.train_deep --data-dir work\demo_raw --subset FD001 --out-dir work\demo_results\deep --models lstm --epochs 2 --window-size 20
```

## Paper 1 Commands / 第一篇相关命令

Representative matrix:

```powershell
python scripts\run_research_matrix.py --subsets FD001 FD002 FD003 FD004 --seeds 42 43 44 --deep-models gru --deep-epochs 60 --skip-existing
```

Focused GRU safety-loss ablation:

```powershell
python scripts\run_deep_ablation_matrix.py --subsets FD001 FD002 FD003 FD004 --seeds 42 43 44 --models gru --skip-existing
```

Regenerate Paper 1 tables and figures from local experiment outputs:

```powershell
python scripts\make_safety_benchmark_outputs.py
python scripts\audit_paper_submission.py
python scripts\package_arxiv_source.py
```

Paper 1 generated experiment outputs under `reports/tables/` are local-only and ignored by Git. Paper-facing summaries are kept under `reports/paper/`.

`reports/tables/` 中的完整实验输出是本地生成内容，不进入 Git；论文使用的摘要表和图表位于 `reports/paper/`。

## Paper 2 Commands / 第二篇相关命令

Full Dual-LSTM matrix:

```powershell
python scripts\run_dual_lstm_matrix.py --subsets FD001 FD002 FD003 FD004 --seeds 42 43 44 --jobs lstm_baseline_h64_l1_w30 dual_no_cycle_h64_l1_w30 dual_cycle_h64_l1_w30 dual_cycle_safety_w2_h64_l1_w30 --epochs 30 --patience 5 --skip-existing
```

Regenerate Paper 2 paper-facing outputs:

```powershell
python scripts\make_dual_lstm_paper2_outputs.py --root reports\tables\dual_lstm --out-dir reports\paper2
python scripts\make_paper2_analysis_outputs.py --paper2-dir reports\paper2 --dual-root reports\tables\dual_lstm --paper1-dir reports\paper --out-dir reports\paper2
python scripts\make_paper2_submission_package.py
```

After a local LaTeX installation is available:

```powershell
.\reports\paper2\build_paper2.ps1
.\reports\paper2\package_paper2_source.ps1
```

## Testing / 测试

```powershell
python -m pytest -q
```

The test suite covers metrics, data windowing, safety losses, uncertainty utilities, robustness perturbations, decision simulation, XAI helpers, Dual-LSTM data/model behavior, and arXiv source packaging.

当前测试覆盖指标、窗口化、安全损失、不确定性工具、鲁棒性扰动、维护决策模拟、XAI 辅助函数、Dual-LSTM 数据/模型行为，以及 arXiv source packaging。

## Research Integrity / 研究边界

- Fit scalers only on training engines, then transform validation/test data.
- Split train/validation by engine ID, not by individual windows.
- Use last-window test evaluation for C-MAPSS test engines.
- Never mix synthetic smoke data with official C-MAPSS experiment results.
- Report late-life and overestimation metrics alongside RMSE and MAE.
- Treat SARBI as a transparent reporting index, not as a physical safety formula or certification criterion.
- Treat C-MAPSS as a simulated benchmark, not real fleet telemetry.
- Do not claim aviation safety certification or new architecture SOTA from these results alone.

研究边界：

- 归一化器只能在训练发动机上拟合，再用于 validation/test。
- train/validation 按 engine ID 切分，不按窗口随机切分。
- C-MAPSS test engine 使用 last-window evaluation。
- 合成 smoke data 不能混入正式 C-MAPSS 实验结果。
- 除 RMSE/MAE 外，需要同时报告临近失效和过度乐观预测风险指标。
- SARBI 是透明报告指标，不是物理安全公式或认证标准。
- C-MAPSS 是仿真 benchmark，不是真实机队遥测数据。
- 仅凭当前结果不宣称航空安全认证，也不宣称新架构 SOTA。

## Next Work / 下一步

Paper 1:

- Audit manuscript numeric values against `reports/paper/paper_value_trace.csv`.
- Rebuild and inspect `reports/paper/main.tex` after a TeX engine is available.
- Keep uncertainty, maintenance decision simulation, domain shift, robustness, and XAI as future-work scaffolds until Paper 1 stabilizes.

Paper 2:

- Read `reports/paper2/main.tex` for voice, target-journal fit, and claim tone.
- Compile `reports/paper2/main.tex` and `reports/paper2/supplement.tex`.
- Check figures visually and decide final submission packaging details.
- Keep novelty claims narrow: cycle-consistent Dual-LSTM is a safety-oriented method response under this protocol, not a universal replacement for Paper 1 baselines.
