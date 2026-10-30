"""Command-line entry point: ``dth backtest-demo``."""

from __future__ import annotations

import argparse
import json

from dth.backtest import BacktestConfig, walk_forward
from dth.signals import DualMomentumTopK
from dth.testing import synthetic_prices


def _backtest_demo(_: argparse.Namespace) -> None:
    prices = synthetic_prices()
    grid = [{"lookback": lb, "top_k": k} for lb in (126, 189, 252) for k in (1, 2)]
    report = walk_forward(
        DualMomentumTopK,
        prices,
        grid=grid,
        config=BacktestConfig(cash_rate=0.02),
        benchmark="EQ_WORLD",
    )
    summary = {
        "signal": report.signal,
        "folds": len(report.folds),
        "oos": {k: round(v, 4) for k, v in report.oos_metrics.items()},
        "benchmark": {k: round(v, 4) for k, v in (report.benchmark_metrics or {}).items()},
        "grid_share_positive_sharpe": round(report.grid_share_positive_sharpe or 0, 3),
    }
    print(json.dumps(summary, indent=2))


def main() -> None:
    parser = argparse.ArgumentParser(prog="dth")
    sub = parser.add_subparsers(required=True)
    sub.add_parser("backtest-demo", help="walk-forward on synthetic data").set_defaults(
        func=_backtest_demo
    )
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
