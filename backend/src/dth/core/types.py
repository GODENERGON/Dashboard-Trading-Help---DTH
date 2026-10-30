"""Domain types shared across layers."""

from __future__ import annotations

from enum import StrEnum

import pandas as pd

PRICE_COLUMNS = ("open", "high", "low", "close", "volume")


class SignalStatus(StrEnum):
    """Lifecycle of a signal. Only VALIDATED and above may be shown in the UI."""

    RESEARCH = "research"
    VALIDATED = "validated"
    PAPER = "paper"
    LIVE = "live"


def validate_price_frame(prices: pd.DataFrame) -> pd.DataFrame:
    """Check the canonical wide price frame: DatetimeIndex, sorted, unique, columns = symbols."""
    if not isinstance(prices.index, pd.DatetimeIndex):
        raise TypeError("prices must be indexed by a DatetimeIndex")
    if prices.index.tz is not None:
        raise ValueError("prices index must be tz-naive (exchange close dates)")
    if not prices.index.is_monotonic_increasing:
        raise ValueError("prices index must be sorted ascending")
    if prices.index.has_duplicates:
        raise ValueError("prices index must not contain duplicates")
    if (prices <= 0).any().any():
        raise ValueError("prices must be strictly positive")
    return prices


def validate_weights(weights: pd.DataFrame, prices: pd.DataFrame) -> pd.DataFrame:
    """Check signal output: aligned to prices, no NaN, values within [-1, 1]."""
    if not weights.index.equals(prices.index):
        raise ValueError("weights must be aligned to the prices index")
    if list(weights.columns) != list(prices.columns):
        raise ValueError("weights columns must match prices columns")
    if weights.isna().any().any():
        raise ValueError("weights must not contain NaN (use 0 for no position)")
    if ((weights < -1) | (weights > 1)).any().any():
        raise ValueError("weights must lie within [-1, 1]")
    return weights
