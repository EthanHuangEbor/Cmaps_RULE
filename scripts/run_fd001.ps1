$ErrorActionPreference = "Stop"

python -m rul_prediction.train_ml `
  --data-dir data/raw `
  --subset FD001 `
  --out-dir reports/tables/fd001_ml `
  --window-size 30 `
  --max-rul 130

python -m rul_prediction.train_deep `
  --data-dir data/raw `
  --subset FD001 `
  --out-dir reports/tables/fd001_deep `
  --models lstm gru cnn `
  --window-size 30 `
  --max-rul 130 `
  --epochs 100

python -m rul_prediction.plots `
  --metrics reports/tables/fd001_ml/metrics.csv reports/tables/fd001_deep/metrics.csv `
  --predictions reports/tables/fd001_ml/predictions.csv reports/tables/fd001_deep/predictions.csv `
  --out-dir reports/figures

