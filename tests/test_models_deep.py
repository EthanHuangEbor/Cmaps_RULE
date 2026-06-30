import numpy as np
import torch

from rul_prediction.models_deep import RULSequenceModel, train_model


def test_tcn_forward_returns_one_rul_per_window() -> None:
    model = RULSequenceModel("tcn", input_size=14, hidden_size=16, num_layers=2, dropout=0.0)
    x = torch.randn(4, 30, 14)

    y = model(x)

    assert y.shape == (4, 1)
    assert torch.isfinite(y).all()


def test_tcn_can_train_for_one_epoch_on_small_batch() -> None:
    rng = np.random.default_rng(7)
    x_train = rng.normal(size=(8, 30, 5)).astype(np.float32)
    y_train = rng.uniform(0, 130, size=8).astype(np.float32)
    x_validation = rng.normal(size=(4, 30, 5)).astype(np.float32)
    y_validation = rng.uniform(0, 130, size=4).astype(np.float32)

    result = train_model(
        "tcn",
        x_train,
        y_train,
        x_validation,
        y_validation,
        hidden_size=8,
        num_layers=2,
        dropout=0.0,
        batch_size=4,
        epochs=1,
        patience=1,
        seed=7,
        device="cpu",
    )

    assert len(result.history) == 1
    assert np.isfinite(result.best_validation_loss)
