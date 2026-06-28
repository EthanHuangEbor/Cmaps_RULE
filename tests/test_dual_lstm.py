from __future__ import annotations

import numpy as np
import pandas as pd
import torch

from rul_prediction.data import make_paired_sequence_windows
from rul_prediction.models_dual_lstm import CycleConsistentDualLSTM, compute_dual_lstm_loss


def test_paired_sequence_windows_stay_within_engine_and_horizon() -> None:
    df = pd.DataFrame(
        {
            "unit": [1, 1, 1, 1, 1, 2, 2, 2, 2, 2],
            "cycle": [1, 2, 3, 4, 5, 1, 2, 3, 4, 5],
            "sensor_1": np.arange(10),
            "sensor_2": np.arange(10) * 2,
            "rul": [4, 3, 2, 1, 0, 4, 3, 2, 1, 0],
        }
    )

    pairs = make_paired_sequence_windows(df, ["sensor_1", "sensor_2"], window_size=3, pair_horizon=1)

    assert pairs.x_current.shape == (4, 3, 2)
    assert pairs.x_future.shape == (4, 3, 2)
    assert pairs.y_current.tolist() == [2, 1, 2, 1]
    assert pairs.y_future.tolist() == [1, 0, 1, 0]
    assert pairs.horizon.tolist() == [1, 1, 1, 1]
    assert pairs.units_current.tolist() == pairs.units_future.tolist()
    assert pairs.cycles_future.tolist() == [4, 5, 4, 5]


def test_cycle_consistent_dual_lstm_outputs_and_loss_are_finite() -> None:
    torch.manual_seed(7)
    model = CycleConsistentDualLSTM(input_size=2, hidden_size=8, num_layers=1, dropout=0.0)
    x_current = torch.randn(5, 4, 2)
    x_future = torch.randn(5, 4, 2)
    y_current = torch.tensor([[8.0], [7.0], [6.0], [5.0], [4.0]])
    y_future = torch.tensor([[7.0], [6.0], [5.0], [4.0], [3.0]])
    horizon = torch.ones(5, 1)

    outputs = model(x_current, horizon)
    future_latent = model.encode(x_future).detach()
    loss = compute_dual_lstm_loss(
        outputs,
        y_current,
        y_future,
        future_latent_target=future_latent,
        lambda_cycle=0.5,
        lambda_latent=0.25,
        lambda_mono=0.1,
        loss_type="safety_mse",
    )

    assert outputs["current_pred"].shape == (5, 1)
    assert outputs["future_pred"].shape == (5, 1)
    assert outputs["future_latent"].shape == (5, 8)
    assert torch.isfinite(loss)
