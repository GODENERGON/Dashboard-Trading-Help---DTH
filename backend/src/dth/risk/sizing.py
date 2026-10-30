"""Position sizing helpers."""

from __future__ import annotations

import numpy as np
import pandas as pd

TRADING_DAYS = 252


def vol_target_scale(
    returns: pd.Series, target_vol: float = 0.10, lookback: int = 63, max_scale: float = 1.0
) -> pd.Series:
    """Exposure multiplier so realized vol tracks ``target_vol``.

    Uses volatility known at the close of each day (no lookahead); never levers above
    ``max_scale`` (default 1.0 = no leverage, per RISK_POLICY).
    """
    realized = returns.rolling(lookback, min_periods=lookback).std() * np.sqrt(TRADING_DAYS)
    scale = (target_vol / realized).clip(upper=max_scale)
    return scale.fillna(0.0)


def position_size_atr(
    capital: float, entry: float, atr: float, atr_mult: float = 2.0, risk_frac: float = 0.01
) -> int:
    """Units to buy so that a stop at ``entry - atr_mult * atr`` loses ``risk_frac`` of capital."""
    if min(capital, entry, atr, atr_mult, risk_frac) <= 0:
        raise ValueError("all inputs must be positive")
    stop_distance = atr_mult * atr
    units = int(capital * risk_frac // stop_distance)
    return min(units, int(capital // entry))
