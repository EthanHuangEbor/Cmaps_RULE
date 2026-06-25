# Next Experiment Runbook

## Quick Validation

```powershell
python -m compileall src scripts tests
python -c "from rul_prediction.models_deep import compute_rul_loss; print('loss-ok')"
```

## Aggregate Existing Results

```powershell
python -m rul_prediction.aggregate --root reports\tables --out-dir reports\tables\summary
python -m rul_prediction.error_analysis --root reports\tables --out-dir reports\tables\summary
```

## FD001 Three Seeds

```powershell
python scripts\run_research_matrix.py --subsets FD001 --seeds 42 43 44 --deep-epochs 60 --skip-safety --skip-existing
```

## FD003 Three Seeds

```powershell
python scripts\run_research_matrix.py --subsets FD003 --seeds 42 43 44 --deep-epochs 60 --skip-safety --skip-existing
```

## Safety-Aware GRU

```powershell
python scripts\run_research_matrix.py --subsets FD001 FD003 --seeds 42 43 44 --deep-epochs 60 --skip-ml --skip-deep --skip-existing
```

## Ablations

```powershell
python scripts\run_ablation.py --deep-epochs 40 --skip-existing
```

## Full Matrix

This is CPU-heavy. Run it overnight if no GPU is available.

```powershell
python scripts\run_research_matrix.py --subsets FD001 FD003 --seeds 42 43 44 --deep-epochs 60 --skip-existing
```

## Interpretive Questions

After each run, answer:

1. Which model has the best aggregate RMSE?
2. Which model has the best critical-zone RMSE?
3. Which model has the lowest NASA S-score?
4. Which model overestimates RUL most often?
5. Did safety-aware GRU improve safety metrics enough to justify worse RMSE?
