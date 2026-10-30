"""Forecaster contract (ADR 0002: forecasters inform risk, they never emit weights)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol, runtime_checkable

import numpy as np


@dataclass(frozen=True)
class ForecastResult:
    point: np.ndarray  # shape (horizon,)
    quantiles: dict[float, np.ndarray] = field(default_factory=dict)  # level -> (horizon,)


@runtime_checkable
class Forecaster(Protocol):
    name: str

    def forecast(self, history: np.ndarray, horizon: int) -> ForecastResult:
        """Forecast ``horizon`` steps ahead using only ``history`` (oldest first)."""
        ...


def pinball_loss(y: np.ndarray, q_pred: np.ndarray, level: float) -> float:
    diff = y - q_pred
    return float(np.mean(np.maximum(level * diff, (level - 1) * diff)))


def qlike(realized_var: np.ndarray, forecast_var: np.ndarray) -> float:
    """QLIKE loss for variance forecasts (robust to noisy realized-variance proxies)."""
    ratio = realized_var / forecast_var
    return float(np.mean(ratio - np.log(ratio) - 1))


def skill_score(model_loss: float, baseline_loss: float) -> float:
    """> 0 means the model beats the baseline. Models with skill <= 0 stay disabled."""
    return 1.0 - model_loss / baseline_loss
