from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import torch
from torch import nn
from torch.utils.data import DataLoader, Dataset

from rul_prediction.data import PairedSequenceWindows
from rul_prediction.models_deep import compute_rul_loss, set_torch_seed


class PairedSequenceDataset(Dataset):
    def __init__(self, pairs: PairedSequenceWindows) -> None:
        self.x_current = torch.as_tensor(pairs.x_current, dtype=torch.float32)
        self.y_current = torch.as_tensor(pairs.y_current, dtype=torch.float32).reshape(-1, 1)
        self.x_future = torch.as_tensor(pairs.x_future, dtype=torch.float32)
        self.y_future = torch.as_tensor(pairs.y_future, dtype=torch.float32).reshape(-1, 1)
        self.horizon = torch.as_tensor(pairs.horizon, dtype=torch.float32).reshape(-1, 1)

    def __len__(self) -> int:
        return int(self.x_current.shape[0])

    def __getitem__(self, index: int) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor]:
        return (
            self.x_current[index],
            self.y_current[index],
            self.x_future[index],
            self.y_future[index],
            self.horizon[index],
        )


class CycleConsistentDualLSTM(nn.Module):
    """Forward RUL LSTM plus target-conditioned latent transition LSTM."""

    def __init__(
        self,
        input_size: int,
        hidden_size: int = 64,
        dropout: float = 0.2,
        num_layers: int = 1,
        horizon_scale: float = 30.0,
    ) -> None:
        super().__init__()
        self.hidden_size = hidden_size
        self.horizon_scale = float(horizon_scale)
        self.encoder = nn.LSTM(
            input_size=input_size,
            hidden_size=hidden_size,
            num_layers=num_layers,
            batch_first=True,
            dropout=dropout if num_layers > 1 else 0.0,
        )
        self.head = nn.Sequential(
            nn.Linear(hidden_size, 32),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(32, 1),
        )
        self.transition = nn.LSTM(
            input_size=hidden_size + 1,
            hidden_size=hidden_size,
            num_layers=num_layers,
            batch_first=True,
            dropout=dropout if num_layers > 1 else 0.0,
        )

    def encode(self, x: torch.Tensor) -> torch.Tensor:
        _, hidden = self.encoder(x)
        if isinstance(hidden, tuple):
            hidden = hidden[0]
        return hidden[-1]

    def predict_current(self, x: torch.Tensor) -> torch.Tensor:
        return self.head(self.encode(x))

    def forward(self, x_current: torch.Tensor, horizon: torch.Tensor) -> dict[str, torch.Tensor]:
        current_latent = self.encode(x_current)
        current_pred = self.head(current_latent)
        horizon = horizon.reshape(-1, 1).to(dtype=x_current.dtype, device=x_current.device) / self.horizon_scale
        transition_input = torch.cat([current_latent, horizon], dim=1).unsqueeze(1)
        _, transition_hidden = self.transition(transition_input)
        if isinstance(transition_hidden, tuple):
            transition_hidden = transition_hidden[0]
        future_latent = transition_hidden[-1]
        future_pred = self.head(future_latent)
        return {
            "current_latent": current_latent,
            "current_pred": current_pred,
            "future_latent": future_latent,
            "future_pred": future_pred,
        }


@dataclass
class DualTrainResult:
    model: CycleConsistentDualLSTM
    history: list[dict[str, float]]
    best_validation_loss: float


def compute_dual_lstm_loss(
    outputs: dict[str, torch.Tensor],
    y_current: torch.Tensor,
    y_future: torch.Tensor,
    *,
    future_latent_target: torch.Tensor | None = None,
    lambda_cycle: float = 1.0,
    lambda_latent: float = 0.25,
    lambda_mono: float = 0.1,
    loss_type: str = "mse",
    critical_threshold: float = 50.0,
    critical_weight: float = 2.0,
    over_weight: float = 2.0,
) -> torch.Tensor:
    current_loss = compute_rul_loss(
        outputs["current_pred"],
        y_current,
        loss_type=loss_type,
        critical_threshold=critical_threshold,
        critical_weight=critical_weight,
        over_weight=over_weight,
    )
    cycle_loss = compute_rul_loss(
        outputs["future_pred"],
        y_future,
        loss_type=loss_type,
        critical_threshold=critical_threshold,
        critical_weight=critical_weight,
        over_weight=over_weight,
    )
    loss = current_loss + lambda_cycle * cycle_loss
    if future_latent_target is not None and lambda_latent > 0:
        loss = loss + lambda_latent * torch.mean((outputs["future_latent"] - future_latent_target.detach()) ** 2)
    if lambda_mono > 0:
        monotonic_violation = torch.relu(outputs["future_pred"] - outputs["current_pred"])
        loss = loss + lambda_mono * torch.mean(monotonic_violation**2)
    return loss


def predict_current(
    model: CycleConsistentDualLSTM,
    x: np.ndarray,
    device: torch.device,
    batch_size: int = 512,
) -> np.ndarray:
    tensor = torch.as_tensor(x, dtype=torch.float32)
    loader = DataLoader(tensor, batch_size=batch_size, shuffle=False)
    preds: list[np.ndarray] = []
    model.eval()
    with torch.no_grad():
        for batch_x in loader:
            pred = model.predict_current(batch_x.to(device)).detach().cpu().numpy().reshape(-1)
            preds.append(pred)
    return np.concatenate(preds)


def train_dual_lstm_model(
    train_pairs: PairedSequenceWindows,
    validation_pairs: PairedSequenceWindows,
    *,
    hidden_size: int = 64,
    dropout: float = 0.2,
    batch_size: int = 128,
    epochs: int = 100,
    learning_rate: float = 1e-3,
    patience: int = 10,
    seed: int = 42,
    device: str | None = None,
    num_layers: int = 1,
    loss_type: str = "mse",
    critical_threshold: float = 50.0,
    critical_weight: float = 2.0,
    over_weight: float = 2.0,
    lambda_cycle: float = 1.0,
    lambda_latent: float = 0.25,
    lambda_mono: float = 0.1,
) -> DualTrainResult:
    set_torch_seed(seed)
    torch_device = torch.device(device or ("cuda" if torch.cuda.is_available() else "cpu"))
    model = CycleConsistentDualLSTM(
        input_size=train_pairs.x_current.shape[2],
        hidden_size=hidden_size,
        dropout=dropout,
        num_layers=num_layers,
    ).to(torch_device)
    train_loader = DataLoader(PairedSequenceDataset(train_pairs), batch_size=batch_size, shuffle=True)
    validation_loader = DataLoader(PairedSequenceDataset(validation_pairs), batch_size=batch_size, shuffle=False)
    optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)

    best_state = {key: value.detach().cpu().clone() for key, value in model.state_dict().items()}
    best_loss = float("inf")
    bad_epochs = 0
    history: list[dict[str, float]] = []

    for epoch in range(1, epochs + 1):
        model.train()
        train_losses: list[float] = []
        for batch_x, batch_y, future_x, future_y, horizon in train_loader:
            batch_x = batch_x.to(torch_device)
            batch_y = batch_y.to(torch_device)
            future_x = future_x.to(torch_device)
            future_y = future_y.to(torch_device)
            horizon = horizon.to(torch_device)
            optimizer.zero_grad()
            outputs = model(batch_x, horizon)
            future_latent = model.encode(future_x)
            loss = compute_dual_lstm_loss(
                outputs,
                batch_y,
                future_y,
                future_latent_target=future_latent,
                lambda_cycle=lambda_cycle,
                lambda_latent=lambda_latent,
                lambda_mono=lambda_mono,
                loss_type=loss_type,
                critical_threshold=critical_threshold,
                critical_weight=critical_weight,
                over_weight=over_weight,
            )
            loss.backward()
            optimizer.step()
            train_losses.append(float(loss.detach().cpu()))

        model.eval()
        validation_losses: list[float] = []
        with torch.no_grad():
            for batch_x, batch_y, future_x, future_y, horizon in validation_loader:
                batch_x = batch_x.to(torch_device)
                batch_y = batch_y.to(torch_device)
                future_x = future_x.to(torch_device)
                future_y = future_y.to(torch_device)
                horizon = horizon.to(torch_device)
                outputs = model(batch_x, horizon)
                future_latent = model.encode(future_x)
                loss = compute_dual_lstm_loss(
                    outputs,
                    batch_y,
                    future_y,
                    future_latent_target=future_latent,
                    lambda_cycle=lambda_cycle,
                    lambda_latent=lambda_latent,
                    lambda_mono=lambda_mono,
                    loss_type=loss_type,
                    critical_threshold=critical_threshold,
                    critical_weight=critical_weight,
                    over_weight=over_weight,
                )
                validation_losses.append(float(loss.detach().cpu()))

        train_loss = float(np.mean(train_losses))
        validation_loss = float(np.mean(validation_losses))
        history.append(
            {
                "epoch": epoch,
                "train_loss": train_loss,
                "validation_loss": validation_loss,
                "learning_rate": float(optimizer.param_groups[0]["lr"]),
            }
        )
        if validation_loss < best_loss:
            best_loss = validation_loss
            best_state = {key: value.detach().cpu().clone() for key, value in model.state_dict().items()}
            bad_epochs = 0
        else:
            bad_epochs += 1
            if bad_epochs >= patience:
                break

    model.load_state_dict(best_state)
    return DualTrainResult(model=model, history=history, best_validation_loss=best_loss)
