import torch

from rul_prediction.models_deep import compute_rul_loss


def test_safety_loss_penalizes_overestimation_more_than_mse():
    y_true = torch.tensor([[20.0], [100.0]])
    y_pred = torch.tensor([[30.0], [90.0]])
    mse = compute_rul_loss(y_pred, y_true, loss_type="mse")
    safety = compute_rul_loss(y_pred, y_true, loss_type="safety_mse")
    assert safety > mse


def test_critical_loss_penalizes_low_rul_samples():
    y_true = torch.tensor([[20.0], [100.0]])
    y_pred = torch.tensor([[25.0], [105.0]])
    mse = compute_rul_loss(y_pred, y_true, loss_type="mse")
    critical = compute_rul_loss(y_pred, y_true, loss_type="critical_mse")
    assert critical > mse


def test_critical_weight_is_multiplier_for_low_rul_sample():
    y_true = torch.tensor([[20.0], [100.0]])
    y_pred = torch.tensor([[30.0], [110.0]])
    critical = compute_rul_loss(
        y_pred,
        y_true,
        loss_type="critical_mse",
        critical_threshold=50,
        critical_weight=2,
    )
    assert torch.isclose(critical, torch.tensor(150.0))
