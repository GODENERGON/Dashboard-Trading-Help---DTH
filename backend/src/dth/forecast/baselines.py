"""Cheap baselines every forecaster must beat."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from dth.forecast.base import ForecastResult


@dataclass(frozen=True)
class EwmaVolatility:
    """RiskMetrics-style EWMA variance of returns; flat forecast of daily volatility."""

    lam: float = 0.94
    name: str = "ewma_vol"

    def forecast(self, history: np.ndarray, horizon: int) -> ForecastResult:
        r = np.asarray(history, dtype=float)
        var = float(np.var(r[:20])) if len(r) >= 20 else float(np.var(r))
        for x in r:
            var = self.lam * var + (1 - self.lam) * x * x
        return ForecastResult(point=np.full(horizon, np.sqrt(var)))


@dataclass(frozen=True)
class HistoricalQuantiles:
    """Rolling empirical quantiles of the last ``window`` observations."""

    window: int = 252
    levels: tuple[float, ...] = (0.1, 0.5, 0.9)
    name: str = "historical_quantiles"

    def forecast(self, history: np.ndarray, horizon: int) -> ForecastResult:
        tail = np.asarray(history, dtype=float)[-self.window :]
        qs = {lv: np.full(horizon, np.quantile(tail, lv)) for lv in self.levels}
        return ForecastResult(point=qs.get(0.5, np.full(horizon, np.median(tail))), quantiles=qs)
