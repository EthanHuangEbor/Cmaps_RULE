# NASA C-MAPSS RUL Prediction

This project implements an 8-week starter research workflow for turbofan engine
Remaining Useful Life (RUL) prediction on the NASA C-MAPSS data set.

Core question:

> Under the same preprocessing, split, and metrics, do LSTM/GRU/1D-CNN models
> outperform traditional machine learning baselines for C-MAPSS RUL prediction,
> and where do those advantages or failures appear?

## Project Outputs

- Reproducible GitHub-style codebase for FD001 first, FD003 extension later.
- Traditional baselines: Ridge, Random Forest, XGBoost when available, otherwise
  scikit-learn `GradientBoostingRegressor`.
- Deep sequence models: LSTM, GRU, and 1D-CNN in PyTorch.
- Metrics: RMSE, MAE, NASA S-score, critical-zone RMSE, overestimation ratio.
- Report templates for a technical report, paper outline, and mentor outreach.

## Data

Download the official Turbofan Engine Degradation Simulation Data Set from the
NASA PCoE repository:

https://www.nasa.gov/intelligent-systems-division/discovery-and-systems-health/pcoe/pcoe-data-set-repository/

Place the files here:

```text
data/raw/train_FD001.txt
data/raw/test_FD001.txt
data/raw/RUL_FD001.txt
data/raw/train_FD003.txt
data/raw/test_FD003.txt
data/raw/RUL_FD003.txt
```

The code does not redistribute NASA data. A synthetic toy generator is included
only for smoke tests and must not be used as research evidence.

## Setup

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -U pip
python -m pip install -e .
```

If `xgboost` is difficult to install, the baseline script still runs with
scikit-learn gradient boosting.

## Quick Smoke Test

This creates toy data and verifies the pipeline shape. It is not a research run.

```powershell
python scripts\make_demo_data.py --out-dir work\demo_raw --subset FD001
python -m rul_prediction.train_ml --data-dir work\demo_raw --subset FD001 --out-dir work\demo_results\ml --window-size 20
python -m rul_prediction.train_deep --data-dir work\demo_raw --subset FD001 --out-dir work\demo_results\deep --models lstm --epochs 2 --window-size 20
```

## Real FD001 Baseline Run

```powershell
python -m rul_prediction.train_ml --data-dir data\raw --subset FD001 --out-dir reports\tables\fd001_ml
python -m rul_prediction.train_deep --data-dir data\raw --subset FD001 --out-dir reports\tables\fd001_deep --models lstm gru cnn
python -m rul_prediction.plots --metrics reports\tables\fd001_ml\metrics.csv reports\tables\fd001_deep\metrics.csv --predictions reports\tables\fd001_ml\predictions.csv reports\tables\fd001_deep\predictions.csv --out-dir reports\figures
```

## Research Upgrade Runs

The next phase focuses on reproducibility, FD003 transfer, ablations, and a
safety-aware GRU loss.

```powershell
python scripts\run_research_matrix.py --subsets FD001 --seeds 42 43 44 --deep-epochs 60 --skip-safety --skip-existing
python scripts\run_research_matrix.py --subsets FD003 --seeds 42 43 44 --deep-epochs 60 --skip-safety --skip-existing
python scripts\run_research_matrix.py --subsets FD001 FD003 --seeds 42 43 44 --deep-epochs 60 --skip-ml --skip-deep --skip-existing
python scripts\run_ablation.py --deep-epochs 40 --skip-existing
```

Aggregated outputs are written under `reports\tables\matrix\summary` and
`reports\tables\ablations\summary`.

## Suggested 8-Week Path

1. Research question, NASA data notes, and three reading cards.
2. Data parsing, RUL labels, no-leakage split, EDA figures.
3. Ridge, Random Forest, and gradient boosting baselines.
4. LSTM main model.
5. GRU and 1D-CNN extension.
6. Error analysis and interpretability.
7. Ablations: window size, max RUL cap, FD001 vs FD003.
8. Package GitHub repository, report, slides, one-pager, and mentor email.

## Repository Layout

```text
configs/                  Reproducible experiment defaults
data/raw/                 NASA data files, not tracked
notebooks/                Notebook instructions
reports/                  Report templates, tables, figures, mentor materials
scripts/                  Data helper scripts
src/rul_prediction/       Project package
tests/                    Lightweight tests
```

## Research Integrity Notes

- Fit scalers only on training engines, then transform validation/test.
- Split train/validation by engine ID, not by individual windows.
- Never mix synthetic smoke data with real NASA results.
- Report all metrics, including late-life critical-zone metrics.
- Treat publication as a second-phase goal after the benchmark is reproducible.
