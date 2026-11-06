"""Command-line entry points: ``dth backtest-demo``, ``dth ucits-trend``."""

from __future__ import annotations

import argparse
import json
import logging
from dataclasses import asdict
from datetime import date
from pathlib import Path

import pandas as pd

from dth.backtest import BacktestConfig, walk_forward
from dth.core.config import REPO_ROOT, load_universe
from dth.signals import DualMomentumTopK
from dth.testing import synthetic_prices

# Share of government bonds per instrument (blended 12.5% / 26% rate, ADR 0008).
GOVT_BOND_SHARE = {"IBGL.MI": 1.0}


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


def _ucits_trend(args: argparse.Namespace) -> None:
    from dth.backtest.taxes import TaxModel
    from dth.research.ucits_trend import build_price_panel, render_markdown, run_study

    universe = load_universe(REPO_ROOT / "config" / "universe.example.yaml")
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    if args.prices_csv:
        prices = pd.read_csv(args.prices_csv, index_col=0, parse_dates=True)
        meta_path = Path(args.prices_csv).with_name("panel_meta.json")
        meta = json.loads(meta_path.read_text()) if meta_path.exists() else []
    else:
        from dth.providers.yfinance_provider import YFinanceProvider

        prices, panel_meta = build_price_panel(
            YFinanceProvider(), universe, date.fromisoformat(args.start), date.today()
        )
        meta = [asdict(m) for m in panel_meta]
        prices.to_csv(out / "prices_eur.csv")
        (out / "panel_meta.json").write_text(json.dumps(meta, indent=2))

    tax = TaxModel.from_config(
        REPO_ROOT / "config" / "tax.it.example.yaml", universe, GOVT_BOND_SHARE
    )
    report = run_study(prices, tax)
    (out / "report.json").write_text(json.dumps(report, indent=2, default=str))
    (out / "report.md").write_text(render_markdown(report, meta), encoding="utf-8")
    logging.getLogger(__name__).info("report written to %s", out)


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    parser = argparse.ArgumentParser(prog="dth")
    sub = parser.add_subparsers(required=True)
    sub.add_parser("backtest-demo", help="walk-forward on synthetic data").set_defaults(
        func=_backtest_demo
    )
    p = sub.add_parser("ucits-trend", help="multi-asset trend study on the UCITS universe")
    p.add_argument("--start", default="2004-01-01")
    p.add_argument("--out", default="reports/ucits_trend")
    p.add_argument("--prices-csv", help="reuse a saved EUR price panel instead of downloading")
    p.set_defaults(func=_ucits_trend)
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
