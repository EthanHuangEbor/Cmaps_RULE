# C-MAPSS RUL Safety-Oriented Benchmark

NASA C-MAPSS turbofan Remaining Useful Life (RUL) prediction research repo.

This repository is a reproducible safety-oriented RUL benchmark for NASA C-MAPSS. It is designed to support a student research paper while remaining useful as a multi-model reproduction codebase. The fixed direction is not single-model SOTA chasing, but model-selection behavior under different evaluation preferences.

## Fixed Research Position

Working title:

> Safety-Oriented Model Selection for Aero-Engine RUL Prediction: Ranking Discordance and Risk-Profile Shaping on C-MAPSS

Core question:

> On C-MAPSS FD001-FD004, does the aggregate RMSE-best model remain the best choice when late-life error, optimistic overestimation risk, uncertainty, and maintenance-decision proxies are considered?

Current answer: often no. The existing results show that RMSE-best, critical-zone-best, overestimation-risk-best, and SARBI-best rankings can diverge.


## Contributions

- Leakage-aware FD001-FD004 C-MAPSS protocol: engine-level validation split, train-only scaling, capped RUL labels, sliding windows, and last-window test evaluation.
- Multi-model comparison across classical ML, deep sequence models, safety-weighted losses, and Dual-LSTM risk-shaping variants.
- Safety-oriented metrics beyond RMSE: NASA S-score, critical-zone RMSE, overestimation ratio, and overestimation magnitude.
- SARBI as a transparent reporting index for aggregate accuracy, late-life behavior, and optimistic-risk behavior.
- Reproducible scripts for paper-facing tables, figures, review materials, and LaTeX manuscripts.

## Current Evidence Snapshot

Paper 1:

- Representative FD001-FD004 matrix for Ridge, Random Forest, Gradient Boosting, GRU, and Safety-GRU.
- 96-job GRU safety-loss ablation across 4 subsets, 3 seeds, and 8 loss/job settings.
- Bootstrap checks and SARBI sensitivity tables for RMSE-best versus risk-best comparisons.
- Baseline extensions now include FD001-FD004 x 3-seed TCN and MLP matrices. These are benchmark-strengthening comparators, not new Paper 1 headline claims unless the manuscript is intentionally expanded.
- MLP full-matrix summary: `reports/mlp_full_matrix_summary_2026-07-02.csv`
- MLP versus existing test-rank summary: `reports/mlp_full_matrix_vs_existing_test_ranks_2026-07-02.csv`
- Main manuscript: `reports/paper/main.tex`
- Compiled reading PDF: `reports/paper/paper1_main.pdf`

Paper 2:

- Full Dual-LSTM matrix: 4 subsets x 3 seeds x 4 jobs = 48 jobs.
- Jobs include LSTM baseline, Dual-LSTM without cycle branch, Dual-LSTM with cycle consistency, and cycle+safety-w2.
- The strongest supported claim is risk-profile shaping, especially reduced overestimation magnitude; cycle consistency should be described as a modest representation signal.
- Main manuscript: `reports/paper2/main.tex`
- Supplement: `reports/paper2/supplement.tex`
- Compiled PDFs: `reports/paper2/paper2_main.pdf`, `reports/paper2/paper2_supplement.pdf`

## Model Roadmap

Implemented:

| Layer | Models / modules | Status |
| --- | --- | --- |
| Classical ML | Ridge, Random Forest, Gradient Boosting, optional XGBoost | implemented |
| Deep sequence | MLP, LSTM, GRU, 1D CNN, TCN | implemented |
| Safety losses | MSE, critical MSE, asymmetric MSE, safety MSE | implemented |
| Risk shaping | Cycle-consistent Dual-LSTM | implemented |
| Evaluation | RMSE, MAE, NASA S-score, critical RMSE30/50, overestimation metrics, SARBI tables | implemented |
| Supporting analyses | uncertainty, robustness, domain shift, XAI, decision simulation scaffolds | partially implemented |

Planned expansion:

| Layer | Planned additions | Purpose |
| --- | --- | --- |
| Attention / Transformer | attention pooling, Transformer encoder, lightweight temporal Transformer | test whether ranking discordance survives stronger deep models |
| Safety-loss transfer | optional TCN/MLP safety-loss checks only if a claim or reviewer question requires them | avoid opening new ablations without a claim-backed reason |
| Uncertainty / calibration | MC dropout, deep ensembles, conformal or quantile intervals | connect RUL point estimates to risk-aware decision support |
| Decision proxy | preventive/late/missed-critical cost simulation | make the evaluation preference explicit rather than only metric-driven |
| Robustness / transfer | sensor noise, masking, FD-to-FD domain shift | support the repo-as-benchmark fallback route |


## Repository Layout

```text
configs/                  Experiment defaults and ablation plans
data/raw/                 Local NASA C-MAPSS files; official txt/PDF data ignored by Git
docs/                     Research status, method specs, and gap analysis
notebooks/                Notebook guidance
reports/paper/            Paper 1 manuscript, figures, tables, value traces, PDF
reports/paper2/           Paper 2 manuscript, supplement, figures, audits, PDFs
reports/review/           Literature review manuscript and supporting review materials
scripts/                  Data helpers, experiment runners, paper-output builders
src/rul_prediction/       Python package
tests/                    Lightweight unit tests
work/                     Scratch and smoke-test outputs; ignored by Git
```

## Data

Download the official Turbofan Engine Degradation Simulation Data Set from the NASA Prognostics Center of Excellence:

<https://www.nasa.gov/intelligent-systems-division/discovery-and-systems-health/pcoe/pcoe-data-set-repository/>

Place files under `data/raw/`:

```text
data/raw/train_FD001.txt
data/raw/test_FD001.txt
data/raw/RUL_FD001.txt
...
data/raw/train_FD004.txt
data/raw/test_FD004.txt
data/raw/RUL_FD004.txt
```

Official NASA data files are not redistributed by this repository. Synthetic data generated by `scripts/make_demo_data.py` are only for smoke tests and must not be used as research evidence.

## Setup

Python 3.10 or newer is recommended.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -U pip
python -m pip install -e ".[dev]"
```

Optional XGBoost support:

```powershell
python -m pip install -e ".[xgboost,dev]"
```

## Smoke Test

This verifies the pipeline with synthetic C-MAPSS-shaped data. It is not a research run.

```powershell
python scripts\make_demo_data.py --out-dir work\demo_raw --subset FD001
python -m rul_prediction.train_ml --data-dir work\demo_raw --subset FD001 --out-dir work\demo_results\ml --window-size 20
python -m rul_prediction.train_deep --data-dir work\demo_raw --subset FD001 --out-dir work\demo_results\deep --models lstm mlp --epochs 2 --window-size 20
python -m pytest -q
```

## Main Experiment Commands

Representative FD001-FD004 matrix:

```powershell
python scripts\run_research_matrix.py --subsets FD001 FD002 FD003 FD004 --seeds 42 43 44 --deep-models lstm gru cnn --deep-epochs 60 --skip-existing
```

Focused GRU safety-loss ablation:

```powershell
python scripts\run_deep_ablation_matrix.py --subsets FD001 FD002 FD003 FD004 --seeds 42 43 44 --models gru --skip-existing
```


### MLP Neural Baseline

A multilayer perceptron is available as a formal fixed-window neural baseline:

```powershell
python -m rul_prediction.train_deep --data-dir data\raw --subset FD001 --out-dir reports\tables\mlp_baseline\fd001\seed_42\deep --models mlp --epochs 20 --patience 4 --window-size 30 --device cuda
```

Implementation scope:

- MLP uses the same engine-level split, train-only scaling, capped RUL labels, sliding windows, last-window test evaluation, metrics, and CSV schema as LSTM/GRU/CNN/TCN.
- The model flattens each `(window_size, n_features)` tensor and feeds it through dense hidden blocks; `num_layers` controls the number of hidden dense blocks.
- MLP is now a completed formal neural baseline matrix, while Paper 1's main narrative still remains centered on the original representative models unless the manuscript is intentionally expanded.
- A CUDA smoke matrix has been run on FD001 and FD004 with seed 42; the small summary is stored in `reports/mlp_baseline_cuda_summary_2026-07-02.csv`, with notes in `reports/mlp_baseline_note_2026-07-02.md`.
- A full FD001-FD004 x 3-seed MLP matrix has been run with CUDA; compact summaries are stored in `reports/mlp_full_matrix_summary_2026-07-02.csv` and `reports/mlp_full_matrix_vs_existing_test_ranks_2026-07-02.csv`.
- Current interpretation: MLP is not RMSE-best overall, but it is a useful non-recurrent neural comparator and is competitive on selected optimistic-risk metrics, especially overestimation magnitude on FD001 and FD003.

Full CUDA matrix command:

```powershell
python scripts\run_research_matrix.py --out-root reports\tables\mlp_full_matrix --subsets FD001 FD002 FD003 FD004 --seeds 42 43 44 --deep-models mlp --deep-epochs 60 --patience 8 --skip-ml --skip-safety --device cuda
```

Dual-LSTM matrix:

```powershell
python scripts\run_dual_lstm_matrix.py --subsets FD001 FD002 FD003 FD004 --seeds 42 43 44 --jobs lstm_baseline_h64_l1_w30 dual_no_cycle_h64_l1_w30 dual_cycle_h64_l1_w30 dual_cycle_safety_w2_h64_l1_w30 --epochs 30 --patience 5 --skip-existing
```

Regenerate paper-facing outputs:

```powershell
python scripts\make_safety_benchmark_outputs.py
python scripts\audit_paper_submission.py
python scripts\package_arxiv_source.py
python scripts\make_dual_lstm_paper2_outputs.py --root reports\tables\dual_lstm --out-dir reports\paper2
python scripts\make_paper2_analysis_outputs.py --paper2-dir reports\paper2 --dual-root reports\tables\dual_lstm --paper1-dir reports\paper --out-dir reports\paper2
python scripts\make_paper2_submission_package.py
```

Generated full experiment outputs under `reports/tables/` are local-only and ignored by Git. Paper-facing summaries are kept under `reports/paper/` and `reports/paper2/`.

## Research Boundaries

- C-MAPSS is a simulated benchmark, not real fleet telemetry.
- SARBI is a transparent reporting index, not a physical safety formula or certification criterion.
- Safety-GRU means loss weighting around an existing GRU, not a new certified safety architecture.
- Dual-LSTM evidence should be framed as risk-profile shaping under the Paper 1 protocol, not universal model superiority.
- Synthetic smoke data must not be mixed with official C-MAPSS results.
- No aviation safety certification, real-fleet deployment, or SOTA claim should be made from the current evidence alone.

## Project Summary

The project is fixed around safety-oriented C-MAPSS RUL evaluation and reproduction. The central question is whether model rankings on FD001-FD004 change when evaluation expands from aggregate RMSE to late-life error, optimistic overestimation risk, and decision-proxy costs. Current evidence says they often do.

Current evidence includes classical ML, GRU/Safety-GRU, TCN, MLP, Dual-LSTM, and safety-loss ablations. MLP has completed the FD001-FD004 x 3-seed CUDA full matrix as a fixed-window neural baseline, but it is not yet a core Paper 1 novelty claim. The repository keeps the experiment runners, metrics, paper tables/figures, and LaTeX artifacts together so the work can serve both as a student-paper package and as a continuing NASA C-MAPSS benchmark baseline.
