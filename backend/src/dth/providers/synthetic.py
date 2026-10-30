"""Offline provider backed by deterministic synthetic prices (tests, demos, CI)."""

from __future__ import annotations

from datetime import date

import pandas as pd

from dth.testing import synthetic_prices


class SyntheticProvider:
    name = "synthetic"

    def __init__(self, seed: int = 42) -> None:
        self._seed = seed

    def fetch(self, symbol: str, start: date, end: date) -> pd.DataFrame:
        closes = synthetic_prices(symbols=(symbol,), seed=self._seed)[symbol]
        closes = closes.loc[pd.Timestamp(start) : pd.Timestamp(end)]
        return pd.DataFrame(
            {
                "open": closes,
                "high": closes * 1.005,
                "low": closes * 0.995,
                "close": closes,
                "volume": 1_000_000.0,
            }
        )
