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


def _core_satellite(args: argparse.Namespace) -> None:
    from dth.backtest.taxes import TaxModel
    from dth.research.core_satellite import render_core_satellite, run_core_satellite_study

    universe = load_universe(REPO_ROOT / "config" / "universe.example.yaml")
    prices = pd.read_csv(args.prices_csv, index_col=0, parse_dates=True)
    tax = TaxModel.from_config(
        REPO_ROOT / "config" / "tax.it.example.yaml", universe, GOVT_BOND_SHARE
    )
    report = run_core_satellite_study(prices, tax)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    (out / "report.json").write_text(json.dumps(report, indent=2, default=str))
    (out / "report.md").write_text(render_core_satellite(report), encoding="utf-8")
    logging.getLogger(__name__).info("report written to %s", out)


def _allocation_study(args: argparse.Namespace) -> None:
    from dth.backtest.taxes import TaxModel
    from dth.research.allocation_study import render_allocation, run_allocation_study

    universe = load_universe(REPO_ROOT / "config" / "universe.example.yaml")
    prices = pd.read_csv(args.prices_csv, index_col=0, parse_dates=True)
    tax = TaxModel.from_config(
        REPO_ROOT / "config" / "tax.it.example.yaml", universe, GOVT_BOND_SHARE
    )
    report = run_allocation_study(prices, tax)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    (out / "report.json").write_text(json.dumps(report, indent=2, default=str))
    (out / "report.md").write_text(render_allocation(report), encoding="utf-8")
    logging.getLogger(__name__).info("report written to %s", out)


def _products_report(args: argparse.Namespace) -> None:
    from dth.products import load_catalog, rank_catalog
    from dth.products.report import render_products_markdown

    ranking = rank_catalog(load_catalog(REPO_ROOT / "config" / "products.example.yaml"))
    Path(args.out).write_text(render_products_markdown(ranking), encoding="utf-8")
    logging.getLogger(__name__).info("product ranking written to %s", args.out)


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
    c = sub.add_parser("core-satellite", help="pre-registered core-satellite + regime study")
    c.add_argument("--prices-csv", required=True, help="EUR panel saved by `ucits-trend`")
    c.add_argument("--out", default="reports/core_satellite")
    c.set_defaults(func=_core_satellite)
    a = sub.add_parser("allocation-study", help="pre-registered skfolio allocation study")
    a.add_argument("--prices-csv", required=True)
    a.add_argument("--out", default="reports/allocation")
    a.set_defaults(func=_allocation_study)
    r = sub.add_parser("products-report", help="render the product ranking to Markdown")
    r.add_argument("--out", default=str(REPO_ROOT / "docs" / "PRODUCTS.md"))
    r.set_defaults(func=_products_report)
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
