"""Trend-following signals (reference implementations for the M1 port)."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

import pandas as pd


@dataclass(frozen=True)
class TrendFilter:
    """Long an asset (equal weight across symbols) when close > its N-day moving average."""

    window: int = 200
    name: str = "trend_filter"

    def compute(self, prices: pd.DataFrame) -> pd.DataFrame:
        ma = prices.rolling(self.window, min_periods=self.window).mean()
        on = (prices > ma).astype(float)
        return (on / prices.shape[1]).fillna(0.0)

    def params(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class DualMomentumTopK:
    """Dual momentum: rank by trailing return, hold the top K that also have positive
    absolute momentum, each at 1/K. Unfilled slots stay in cash.

    ``skip`` excludes the most recent days from the lookback (short-term reversal).
    """

    lookback: int = 252
    top_k: int = 2
    skip: int = 21
    name: str = "dual_momentum_topk"

    def compute(self, prices: pd.DataFrame) -> pd.DataFrame:
        if self.top_k < 1:
            raise ValueError("top_k must be >= 1")
        past = prices.shift(self.skip)
        mom = past / prices.shift(self.lookback) - 1.0
        rank = mom.rank(axis=1, ascending=False, method="first")
        chosen = (rank <= self.top_k) & (mom > 0)
        return (chosen.astype(float) / self.top_k).fillna(0.0)

    def params(self) -> dict[str, Any]:
        return asdict(self)
