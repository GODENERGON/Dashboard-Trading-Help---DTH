"""Holdings-level portfolio simulator: weights drift between rebalances, trades have costs,
and (optionally) Italian taxes are applied (see dth.backtest.taxes).

Timing: target weights decided at the close of a rebalance date are traded at the next close.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
import pandas as pd

from dth.backtest.engine import BacktestConfig, _rebalance_mask
from dth.backtest.taxes import TaxLedger, TaxModel
from dth.core.types import validate_weights
from dth.signals.base import Signal

TRADING_DAYS = 252


@dataclass
class PortfolioResult:
    equity: pd.Series  # portfolio value after costs (and taxes paid, if taxed)
    turnover: pd.Series  # one-way traded value / portfolio value, per day
    weights: pd.DataFrame  # end-of-day weights actually held
    taxes_paid: pd.Series = field(default_factory=lambda: pd.Series(dtype=float))
    tax_history: list[dict[str, float]] = field(default_factory=list)
    liquidation_value: float = float("nan")  # final value if everything were sold, after tax

    @property
    def returns(self) -> pd.Series:
        return self.equity.pct_change().fillna(0.0)


def simulate_portfolio(
    signal: Signal,
    prices: pd.DataFrame,
    config: BacktestConfig | None = None,
    tax: TaxModel | None = None,
    initial: float = 100_000.0,
    wealth_tax: bool = True,
) -> PortfolioResult:
    config = config or BacktestConfig()
    targets = validate_weights(signal.compute(prices), prices)
    decide = _rebalance_mask(prices.index, config.rebalance).to_numpy()

    px = prices.to_numpy(dtype=float)
    tgt = targets.to_numpy(dtype=float)
    n_days, n_assets = px.shape
    symbols = list(prices.columns)

    value = np.zeros(n_assets)
    basis = np.zeros(n_assets)
    cash = initial
    ledger = TaxLedger(tax) if tax is not None else None

    equity = np.empty(n_days)
    turnover = np.zeros(n_days)
    held = np.zeros((n_days, n_assets))
    taxes = np.zeros(n_days)
    years = prices.index.year.to_numpy()
    daily_cash = config.cash_rate / TRADING_DAYS

    for t in range(n_days):
        if t > 0:
            ratio = px[t] / px[t - 1]
            ratio = np.where(np.isfinite(ratio), ratio, 1.0)
            value *= ratio
            cash *= 1 + daily_cash

            if decide[t - 1]:
                total = value.sum() + cash
                target = tgt[t - 1] * total
                delta = target - value
                for i in np.flatnonzero(delta < -1e-9):
                    frac = -delta[i] / value[i] if value[i] > 0 else 0.0
                    if ledger is not None:
                        ledger.realize(symbols[i], frac * (value[i] - basis[i]))
                    basis[i] *= 1 - frac
                buys = delta > 1e-9
                basis[buys] += delta[buys]
                traded = np.abs(delta).sum()
                cost = traded * config.cost_bps / 10_000
                cash = total - target.sum() - cost
                value = target.copy()
                turnover[t] = traded / total if total > 0 else 0.0

        last_of_year = t == n_days - 1 or years[t + 1] != years[t]
        if ledger is not None and last_of_year and t < n_days - 1:
            due = ledger.settle(int(years[t]), value.sum(), wealth_tax=wealth_tax)
            cash -= due
            taxes[t] = due

        equity[t] = value.sum() + cash
        held[t] = value / equity[t] if equity[t] > 0 else 0.0

    liquidation = equity[-1]
    if ledger is not None:
        for i in range(n_assets):
            if value[i] > 0:
                ledger.realize(symbols[i], value[i] - basis[i])
        due = ledger.settle(int(years[-1]), 0.0, wealth_tax=False)
        liquidation -= due
        taxes[-1] += due

    return PortfolioResult(
        equity=pd.Series(equity, index=prices.index),
        turnover=pd.Series(turnover, index=prices.index),
        weights=pd.DataFrame(held, index=prices.index, columns=prices.columns),
        taxes_paid=pd.Series(taxes, index=prices.index),
        tax_history=ledger.history if ledger is not None else [],
        liquidation_value=float(liquidation),
    )
