"""Walk-forward validation harness.

For each fold: choose parameters on the train window only (if a grid is given), then run on
the following test window. Out-of-sample returns are stitched into one series.
Because signals are causal, they are computed on prices up to the fold end; any warm-up
needed by indicators is taken from history, never from the future.
"""

from __future__ import annotations

from collections.abc import Callable, Iterable
from dataclasses import dataclass, field
from typing import Any

import pandas as pd

from dth.backtest.engine import BacktestConfig, run_backtest
from dth.backtest.metrics import compute_metrics
from dth.signals.base import Signal

SignalFactory = Callable[..., Signal]


@dataclass
class Fold:
    train_start: str
    train_end: str
    test_start: str
    test_end: str
    params: dict[str, Any]
    test_metrics: dict[str, float]


@dataclass
class ValidationReport:
    signal: str
    config: dict[str, Any]
    folds: list[Fold]
    oos_metrics: dict[str, float]
    benchmark_metrics: dict[str, float] | None = None
    grid_share_positive_sharpe: float | None = None
    oos_returns: pd.Series = field(default_factory=lambda: pd.Series(dtype=float), repr=False)

    def to_dict(self) -> dict[str, Any]:
        equity = (1 + self.oos_returns).cumprod()
        return {
            "signal": self.signal,
            "config": self.config,
            "folds": [f.__dict__ for f in self.folds],
            "oos_metrics": self.oos_metrics,
            "benchmark_metrics": self.benchmark_metrics,
            "grid_share_positive_sharpe": self.grid_share_positive_sharpe,
            "equity": {d.date().isoformat(): float(v) for d, v in equity.items()},
        }


def _folds(
    index: pd.DatetimeIndex, train_years: int, test_years: int, expanding: bool
) -> Iterable[tuple[pd.Timestamp, pd.Timestamp, pd.Timestamp, pd.Timestamp]]:
    start = index[0]
    train_end = start + pd.DateOffset(years=train_years)
    while True:
        test_end = train_end + pd.DateOffset(years=test_years)
        test_idx = index[(index > train_end) & (index <= test_end)]
        if len(test_idx) < 21:
            return
        train_start = start if expanding else train_end - pd.DateOffset(years=train_years)
        yield train_start, train_end, test_idx[0], test_idx[-1]
        train_end = test_end


def walk_forward(
    factory: SignalFactory,
    prices: pd.DataFrame,
    *,
    grid: list[dict[str, Any]] | None = None,
    config: BacktestConfig | None = None,
    train_years: int = 5,
    test_years: int = 1,
    expanding: bool = True,
    benchmark: str | None = None,
) -> ValidationReport:
    config = config or BacktestConfig()
    grid = grid or [{}]
    folds: list[Fold] = []
    oos: list[pd.Series] = []
    positive_share: list[float] = []

    for tr_s, tr_e, te_s, te_e in _folds(prices.index, train_years, test_years, expanding):
        train_px = prices.loc[tr_s:tr_e]
        scores = []
        for params in grid:
            res = run_backtest(factory(**params), train_px, config)
            scores.append(compute_metrics(res.returns)["sharpe"])
        positive_share.append(sum(s > 0 for s in scores) / len(scores))
        best = grid[max(range(len(grid)), key=scores.__getitem__)]

        # Run on history up to test end, keep only the test window (causal warm-up).
        res = run_backtest(factory(**best), prices.loc[:te_e], config)
        test_rets = res.returns.loc[te_s:te_e]
        oos.append(test_rets)
        folds.append(
            Fold(
                train_start=str(tr_s.date()),
                train_end=str(tr_e.date()),
                test_start=str(te_s.date()),
                test_end=str(te_e.date()),
                params=best,
                test_metrics=compute_metrics(test_rets),
            )
        )

    if not oos:
        raise ValueError("not enough history for a single walk-forward fold")
    oos_rets = pd.concat(oos)
    bench = None
    if benchmark is not None:
        b = prices[benchmark].pct_change().loc[oos_rets.index]
        bench = compute_metrics(b)
    sample = factory(**grid[0])
    return ValidationReport(
        signal=sample.name,
        config={
            **config.__dict__,
            "grid": grid,
            "train_years": train_years,
            "test_years": test_years,
            "expanding": expanding,
        },
        folds=folds,
        oos_metrics=compute_metrics(oos_rets),
        benchmark_metrics=bench,
        grid_share_positive_sharpe=sum(positive_share) / len(positive_share),
        oos_returns=oos_rets,
    )
