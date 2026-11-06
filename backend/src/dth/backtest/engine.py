"""Vectorized daily backtest engine.

Timing convention (the single place where execution lag is applied):
    weights decided at close of day t  →  held over day t+1  →  earn return(t → t+1).
"""

from __future__ import annotations

from dataclasses import dataclass, field

import pandas as pd

from dth.core.types import validate_price_frame, validate_weights
from dth.signals.base import Signal

TRADING_DAYS = 252


@dataclass(frozen=True)
class BacktestConfig:
    rebalance: str = "ME"  # pandas offset alias: "ME" month-end, "W-FRI" weekly, "D" daily
    cost_bps: float = 10.0  # one-way cost (commission + spread + slippage), basis points
    cash_rate: float = 0.0  # annual yield on uninvested capital
    # No-trade band (portfolio simulator only): an asset is traded at a rebalance only if its
    # weight is off target by more than this, or it must be fully entered or exited.
    rebalance_band: float = 0.0


@dataclass
class BacktestResult:
    returns: pd.Series  # net daily strategy returns
    weights: pd.DataFrame  # weights actually held each day
    turnover: pd.Series  # one-way turnover each day
    config: BacktestConfig = field(default_factory=BacktestConfig)

    @property
    def equity(self) -> pd.Series:
        return (1 + self.returns).cumprod()


def _rebalance_mask(index: pd.DatetimeIndex, rule: str) -> pd.Series:
    if rule == "D":
        return pd.Series(True, index=index)
    # Last available trading day of each period ("ME" month-end, "YE" year-end, "W-FRI"...).
    periods = index.to_period({"ME": "M", "YE": "Y", "QE": "Q"}.get(rule, rule))
    last = pd.Series(index, index=index).groupby(periods).transform("max")
    return pd.Series(index == last.to_numpy(), index=index)


def target_weights(signal: Signal, prices: pd.DataFrame, rebalance: str) -> pd.DataFrame:
    """Signal weights sampled on rebalance dates and carried forward (still decision-time)."""
    raw = validate_weights(signal.compute(prices), prices)
    mask = _rebalance_mask(prices.index, rebalance)
    return raw.where(mask, axis=0).ffill().fillna(0.0)


def run_backtest(
    signal: Signal, prices: pd.DataFrame, config: BacktestConfig | None = None
) -> BacktestResult:
    config = config or BacktestConfig()
    validate_price_frame(prices)
    decided = target_weights(signal, prices, config.rebalance)
    held = decided.shift(1).fillna(0.0)  # execution lag: one bar

    asset_rets = prices.pct_change().fillna(0.0)
    gross = (held * asset_rets).sum(axis=1)
    cash_w = (1 - held.abs().sum(axis=1)).clip(lower=0.0)
    cash = cash_w * config.cash_rate / TRADING_DAYS
    turnover = held.diff().abs().sum(axis=1).fillna(held.abs().sum(axis=1))
    costs = turnover * config.cost_bps / 10_000
    return BacktestResult(
        returns=gross + cash - costs, weights=held, turnover=turnover, config=config
    )
