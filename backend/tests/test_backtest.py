from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from dth.backtest import BacktestConfig, compute_metrics, run_backtest, walk_forward
from dth.backtest.metrics import max_drawdown
from dth.signals import DualMomentumTopK, TrendFilter
from dth.testing import synthetic_prices


class _AllIn:
    """Constant 100% in the first column."""

    name = "all_in"

    def compute(self, prices: pd.DataFrame) -> pd.DataFrame:
        w = pd.DataFrame(0.0, index=prices.index, columns=prices.columns)
        w.iloc[:, 0] = 1.0
        return w

    def params(self) -> dict:
        return {}


def test_execution_lag_is_one_bar() -> None:
    idx = pd.bdate_range("2024-01-01", periods=5)
    prices = pd.DataFrame({"A": [100, 110, 121, 133.1, 146.41]}, index=idx)
    res = run_backtest(_AllIn(), prices, BacktestConfig(rebalance="D", cost_bps=0))
    # Decided at close of day 0, so the first earned return is day 0 → day 1 (+10%),
    # booked on day 1. Day 0 itself earns nothing.
    assert res.returns.iloc[0] == 0
    assert res.returns.iloc[1:].round(10).tolist() == [0.1, 0.1, 0.1, 0.1]


def test_costs_reduce_returns() -> None:
    prices = synthetic_prices(periods=252 * 3)
    sig = DualMomentumTopK(lookback=63, top_k=1, skip=0)
    free = run_backtest(sig, prices, BacktestConfig(cost_bps=0)).returns.sum()
    paid = run_backtest(sig, prices, BacktestConfig(cost_bps=25)).returns.sum()
    assert paid < free


def test_cash_yield_applies_to_uninvested_capital() -> None:
    prices = synthetic_prices(periods=300)
    res = run_backtest(TrendFilter(window=10_000), prices, BacktestConfig(cash_rate=0.0252))
    assert res.returns.iloc[-1] == pytest.approx(0.0252 / 252)


def test_metrics_on_known_series() -> None:
    r = pd.Series([0.01, -0.02, 0.03, -0.01])
    assert max_drawdown(r) == pytest.approx(-0.02)
    m = compute_metrics(pd.Series(np.full(252, 0.0004)))
    assert m["cagr"] == pytest.approx(1.0004**252 - 1)
    assert m["max_drawdown"] == 0


def test_walk_forward_produces_contiguous_oos() -> None:
    prices = synthetic_prices(periods=252 * 10)
    grid = [{"lookback": lb} for lb in (63, 126)]
    report = walk_forward(DualMomentumTopK, prices, grid=grid, train_years=4, benchmark="EQ_WORLD")
    assert len(report.folds) >= 5
    assert report.oos_returns.index.is_monotonic_increasing
    assert not report.oos_returns.index.has_duplicates
    assert report.oos_returns.index[0] > pd.Timestamp(report.folds[0].train_end)
    assert 0 <= report.grid_share_positive_sharpe <= 1
    payload = report.to_dict()
    assert {"oos_metrics", "folds", "equity", "benchmark_metrics"} <= payload.keys()
