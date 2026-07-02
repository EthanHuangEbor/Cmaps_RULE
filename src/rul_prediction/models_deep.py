from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import torch
from torch import nn
from torch.utils.data import DataLoader, Dataset


class SequenceDataset(Dataset):
    def __init__(self, x: np.ndarray, y: np.ndarray) -> None:
        self.x = torch.as_tensor(x, dtype=torch.float32)
        self.y = torch.as_tensor(y, dtype=torch.float32).reshape(-1, 1)

    def __len__(self) -> int:
        return int(self.x.shape[0])

    def __getitem__(self, index: int) -> tuple[torch.Tensor, torch.Tensor]:
        return self.x[index], self.y[index]


class Chomp1d(nn.Module):
    def __init__(self, chomp_size: int) -> None:
        super().__init__()
        self.chomp_size = chomp_size

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        if self.chomp_size == 0:
            return x
        return x[:, :, :-self.chomp_size].contiguous()


class TemporalBlock(nn.Module):
    def __init__(self, in_channels: int, out_channels: int, *, dilation: int, dropout: float) -> None:
        super().__init__()
        kernel_size = 3
        padding = (kernel_size - 1) * dilation
        self.net = nn.Sequential(
            nn.Conv1d(in_channels, out_channels, kernel_size, padding=padding, dilation=dilation),
            Chomp1d(padding),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Conv1d(out_channels, out_channels, kernel_size, padding=padding, dilation=dilation),
            Chomp1d(padding),
            nn.ReLU(),
            nn.Dropout(dropout),
        )
        self.downsample = nn.Conv1d(in_channels, out_channels, kernel_size=1) if in_channels != out_channels else None
        self.activation = nn.ReLU()

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        residual = x if self.downsample is None else self.downsample(x)
        return self.activation(self.net(x) + residual)

class RULSequenceModel(nn.Module):
    def __init__(
        self,
        model_type: str,
        input_size: int,
        hidden_size: int = 64,
        dropout: float = 0.2,
        num_layers: int = 1,
        window_size: int | None = None,
    ) -> None:
        super().__init__()
        self.model_type = model_type.lower()
        if self.model_type == "lstm":
            self.encoder = nn.LSTM(
                input_size=input_size,
                hidden_size=hidden_size,
                num_layers=num_layers,
                batch_first=True,
                dropout=dropout if num_layers > 1 else 0.0,
            )
            encoder_size = hidden_size
        elif self.model_type == "gru":
            self.encoder = nn.GRU(
                input_size=input_size,
                hidden_size=hidden_size,
                num_layers=num_layers,
                batch_first=True,
                dropout=dropout if num_layers > 1 else 0.0,
            )
            encoder_size = hidden_size
        elif self.model_type == "cnn":
            self.encoder = nn.Sequential(
                nn.Conv1d(input_size, 32, kernel_size=3, padding=1),
                nn.ReLU(),
                nn.Dropout(dropout),
                nn.Conv1d(32, 64, kernel_size=3, padding=1),
                nn.ReLU(),
                nn.AdaptiveAvgPool1d(1),
            )
            encoder_size = 64
        elif self.model_type == "tcn":
            layers: list[nn.Module] = []
            for layer_index in range(max(1, num_layers)):
                in_channels = input_size if layer_index == 0 else hidden_size
                layers.append(
                    TemporalBlock(
                        in_channels,
                        hidden_size,
                        dilation=2**layer_index,
                        dropout=dropout,
                    )
                )
            self.encoder = nn.Sequential(*layers)
            encoder_size = hidden_size
        elif self.model_type == "mlp":
            if window_size is None:
                raise ValueError("window_size is required for MLP models.")
            layers = [nn.Flatten()]
            in_features = window_size * input_size
            for _ in range(max(1, num_layers)):
                layers.extend(
                    [
                        nn.Linear(in_features, hidden_size),
                        nn.ReLU(),
                        nn.Dropout(dropout),
                    ]
                )
                in_features = hidden_size
            self.encoder = nn.Sequential(*layers)
            encoder_size = hidden_size
        else:
            raise ValueError(f"Unsupported model_type: {model_type}")

        self.head = nn.Sequential(
            nn.Linear(encoder_size, 32),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(32, 1),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        if self.model_type in {"lstm", "gru"}:
            _, hidden = self.encoder(x)
            if isinstance(hidden, tuple):
                hidden = hidden[0]
            encoded = hidden[-1]
        elif self.model_type == "tcn":
            encoded = self.encoder(x.transpose(1, 2))[:, :, -1]
        elif self.model_type == "mlp":
            encoded = self.encoder(x)
        else:
            encoded = self.encoder(x.transpose(1, 2)).squeeze(-1)
        return self.head(encoded)


@dataclass
class TrainResult:
    model: RULSequenceModel
    history: list[dict[str, float]]
    best_validation_loss: float


def set_torch_seed(seed: int) -> None:
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False


def predict(model: nn.Module, x: np.ndarray, device: torch.device, batch_size: int = 512) -> np.ndarray:
    dataset = SequenceDataset(x, np.zeros(len(x), dtype=np.float32))
    loader = DataLoader(dataset, batch_size=batch_size, shuffle=False)
    preds: list[np.ndarray] = []
    model.eval()
    with torch.no_grad():
        for batch_x, _ in loader:
            pred = model(batch_x.to(device)).detach().cpu().numpy().reshape(-1)
            preds.append(pred)
    return np.concatenate(preds)


def compute_rul_loss(
    y_pred: torch.Tensor,
    y_true: torch.Tensor,
    *,
    loss_type: str = "mse",
    critical_threshold: float = 50.0,
    critical_weight: float = 2.0,
    over_weight: float = 2.0,
) -> torch.Tensor:
    """Compute a RUL training loss.

    `mse` is the neutral baseline. The safety-aware variants are intentionally
    simple and transparent so they can be analyzed in a student research report.
    """
    squared_error = (y_pred - y_true) ** 2
    loss_type = loss_type.lower()
    weights = torch.ones_like(squared_error)
    if loss_type == "mse":
        pass
    elif loss_type == "critical_mse":
        critical_mask = (y_true <= critical_threshold).float()
        weights = weights + (critical_weight - 1.0) * critical_mask
    elif loss_type == "asymmetric_mse":
        over_mask = (y_pred > y_true).float()
        weights = weights + (over_weight - 1.0) * over_mask
    elif loss_type == "safety_mse":
        critical_mask = (y_true <= critical_threshold).float()
        over_mask = (y_pred > y_true).float()
        weights = weights + (critical_weight - 1.0) * critical_mask + (over_weight - 1.0) * over_mask
    else:
        raise ValueError(f"Unsupported loss_type: {loss_type}")
    return torch.mean(weights * squared_error)


def train_model(
    model_type: str,
    x_train: np.ndarray,
    y_train: np.ndarray,
    x_validation: np.ndarray,
    y_validation: np.ndarray,
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
    scheduler: str = "none",
    scheduler_factor: float = 0.5,
    scheduler_patience: int = 4,
    min_learning_rate: float = 1e-5,
) -> TrainResult:
    set_torch_seed(seed)
    torch_device = torch.device(device or ("cuda" if torch.cuda.is_available() else "cpu"))
    model = RULSequenceModel(
        model_type=model_type,
        input_size=x_train.shape[2],
        hidden_size=hidden_size,
        dropout=dropout,
        num_layers=num_layers,
        window_size=x_train.shape[1],
    ).to(torch_device)
    train_loader = DataLoader(SequenceDataset(x_train, y_train), batch_size=batch_size, shuffle=True)
    validation_loader = DataLoader(SequenceDataset(x_validation, y_validation), batch_size=batch_size)
    optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)
    lr_scheduler = None
    scheduler = scheduler.lower()
    if scheduler == "reduce_on_plateau":
        lr_scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(
            optimizer,
            mode="min",
            factor=scheduler_factor,
            patience=scheduler_patience,
            min_lr=min_learning_rate,
        )
    elif scheduler != "none":
        raise ValueError(f"Unsupported scheduler: {scheduler}")

    best_state = {key: value.detach().cpu().clone() for key, value in model.state_dict().items()}
    best_loss = float("inf")
    bad_epochs = 0
    history: list[dict[str, float]] = []

    for epoch in range(1, epochs + 1):
        model.train()
        train_losses: list[float] = []
        for batch_x, batch_y in train_loader:
            batch_x = batch_x.to(torch_device)
            batch_y = batch_y.to(torch_device)
            optimizer.zero_grad()
            loss = compute_rul_loss(
                model(batch_x),
                batch_y,
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
            for batch_x, batch_y in validation_loader:
                batch_x = batch_x.to(torch_device)
                batch_y = batch_y.to(torch_device)
                loss = compute_rul_loss(
                    model(batch_x),
                    batch_y,
                    loss_type=loss_type,
                    critical_threshold=critical_threshold,
                    critical_weight=critical_weight,
                    over_weight=over_weight,
                )
                validation_losses.append(float(loss.detach().cpu()))

        train_loss = float(np.mean(train_losses))
        validation_loss = float(np.mean(validation_losses))
        if lr_scheduler is not None:
            lr_scheduler.step(validation_loss)
        current_lr = float(optimizer.param_groups[0]["lr"])
        history.append(
            {
                "epoch": epoch,
                "train_loss": train_loss,
                "validation_loss": validation_loss,
                "learning_rate": current_lr,
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
    return TrainResult(model=model, history=history, best_validation_loss=best_loss)
