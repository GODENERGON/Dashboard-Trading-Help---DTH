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


def _demo_data(args: argparse.Namespace) -> None:
    """Export real-data JSON for the frontend prototype (regime, products, risk example)."""
    from dth.backtest import BacktestConfig
    from dth.backtest.portfolio import simulate_portfolio
    from dth.highlights import Context
    from dth.products import build_model_portfolios, load_catalog, rank_catalog
    from dth.regime import TrendRegimeRule, asset_in_trend, regime_series
    from dth.signals import CoreSatellite, MultiAssetTrend

    full = pd.read_csv(args.prices_csv, index_col=0, parse_dates=True)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    if args.scenario_date:
        _scenario(full.loc[: args.scenario_date], out / "scenario.json")
        return
    prices = full

    regime = regime_series(prices, "XEON.MI", ("SWDA.MI", "CSSPX.MI"))
    weekly = regime[regime != "n/d"].resample("W-FRI").last().dropna()
    detail = TrendRegimeRule().explain(Context(prices=prices, as_of=prices.index[-1]))
    regime_json = {
        "as_of": str(prices.index[-1].date()),
        "current": regime.iloc[-1],
        "detail": detail.to_dict() if detail else None,
        "in_trend": {
            k: bool(v) for k, v in asset_in_trend(prices.drop(columns="XEON.MI")).iloc[-1].items()
        },
        "weekly": [{"d": str(d.date()), "s": s} for d, s in weekly.items()],
    }
    (out / "regime.json").write_text(json.dumps(regime_json, ensure_ascii=False))

    ranking = rank_catalog(load_catalog(REPO_ROOT / "config" / "products.example.yaml"))
    (out / "products.json").write_text(json.dumps(ranking, ensure_ascii=False, default=str))
    models = build_model_portfolios(ranking)
    (out / "models.json").write_text(json.dumps(models, ensure_ascii=False))

    balanced = CoreSatellite(
        core=((("SWDA.MI", "CSSPX.MI"), 0.55), (("IBGL.MI",), 0.35), (("SGLD.MI",), 0.10)),
        satellite=MultiAssetTrend(cash_symbol=None),
        satellite_share=0.0,
    )
    res = simulate_portfolio(balanced, prices, BacktestConfig(rebalance="YE"), initial=100_000)
    eq = res.equity.loc["2016-01-01":]
    dd = eq / eq.cummax() - 1
    vol = eq.pct_change().iloc[-63:].std() * (252**0.5)
    risk = {
        "label": "Esempio: bilanciato 55/35/10 da 100.000 € (dati reali, lordo)",
        "value": float(eq.iloc[-1] / eq.iloc[0] * 100_000),
        "drawdown_now": float(dd.iloc[-1]),
        "drawdown_max": float(dd.min()),
        "vol_3m": float(vol),
        "equity_monthly": [
            {"d": str(d.date()), "v": round(float(v), 2)}
            for d, v in (eq / eq.iloc[0] * 100).resample("ME").last().items()
        ],
        "weights": {k: float(v) for k, v in res.weights.iloc[-1].items() if v > 0.001},
    }
    (out / "risk.json").write_text(json.dumps(risk, ensure_ascii=False))
    logging.getLogger(__name__).info("demo data written to %s", out)


def _balanced_equity(prices: pd.DataFrame) -> pd.Series:
    from dth.backtest import BacktestConfig
    from dth.backtest.portfolio import simulate_portfolio
    from dth.signals import CoreSatellite, MultiAssetTrend

    balanced = CoreSatellite(
        core=((("SWDA.MI", "CSSPX.MI"), 0.55), (("IBGL.MI",), 0.35), (("SGLD.MI",), 0.10)),
        satellite=MultiAssetTrend(cash_symbol=None),
        satellite_share=0.0,
    )
    res = simulate_portfolio(balanced, prices, BacktestConfig(rebalance="YE"), initial=100_000)
    return res.equity.loc["2016-01-01":]


def _scenario(prices: pd.DataFrame, path: Path) -> None:
    """A past day replayed through the highlight rules (real prices; VIX is a stated fact)."""
    from dth.highlights import Highlight
    from dth.regime import asset_in_trend, regime_series
    from dth.risk import DEFAULT_LIMITS, drawdown_state

    as_of = prices.index[-1]
    regime = regime_series(prices, "XEON.MI", ("SWDA.MI", "CSSPX.MI"))
    weekly = regime[regime != "n/d"].resample("W-FRI").last().dropna()
    eq = _balanced_equity(prices)
    dd = eq / eq.cummax() - 1
    state = drawdown_state(eq, DEFAULT_LIMITS)
    highlights = []
    if state.value != "normal":
        level = "critical" if state.value == "stop" else "attention"
        limit = DEFAULT_LIMITS.dd_stop if level == "critical" else DEFAULT_LIMITS.dd_warning
        now_pct = f"{dd.iloc[-1] * 100:.1f}%".replace(".", ",")
        highlights.append(
            Highlight(
                rule_id="drawdown_stop" if level == "critical" else "drawdown_warning",
                level=level,
                title=f"Portafoglio a {now_pct} dal massimo",
                explanation=(
                    f"Il drawdown del portafoglio ({now_pct}) ha superato il limite di "
                    f"{limit * 100:.0f}% della policy di rischio. La policy prevede di "
                    "dimezzare l'esposizione e rivedere il portafoglio a mano."
                ),
                as_of=str(as_of.date()),
                data={
                    "drawdown": float(dd.iloc[-1]),
                    "limit": limit,
                    "peak": str(eq.idxmax().date()),
                },  # fmt: skip
            ).to_dict()
        )
    highlights.append(
        Highlight(
            rule_id="vix_backwardation",
            level="attention",
            title="Paura più alta nel breve che nel medio periodo",
            explanation=(
                "L'indice di volatilità VIX a 1 mese è sopra quello a 3 mesi da più di 2 sedute: "
                "il mercato si aspetta turbolenza immediata. Dato storico noto del marzo 2020; "
                "la fonte Cboe non è ancora collegata in Dabitur."
            ),
            as_of=str(as_of.date()),
            data={"source": "cboe (illustrativo)"},
        ).to_dict()
    )
    payload = {
        "as_of": str(as_of.date()),
        "label": "Esempio: 18 marzo 2020, crollo Covid",
        "current": regime.iloc[-1],
        "in_trend": {
            k: bool(v) for k, v in asset_in_trend(prices.drop(columns="XEON.MI")).iloc[-1].items()
        },
        "weekly": [{"d": str(d.date()), "s": st} for d, st in weekly.items()],
        "risk": {
            "label": "Esempio: bilanciato 55/35/10 da 100.000 € (dati reali, lordo)",
            "value": float(eq.iloc[-1] / eq.iloc[0] * 100_000),
            "drawdown_now": float(dd.iloc[-1]),
            "drawdown_max": float(dd.min()),
            "vol_3m": float(eq.pct_change().iloc[-63:].std() * (252**0.5)),
            "equity_monthly": [
                {"d": str(d.date()), "v": round(float(v), 2)}
                for d, v in (eq / eq.iloc[0] * 100).resample("ME").last().items()
            ],
        },
        "highlights": highlights,
    }
    path.write_text(json.dumps(payload, ensure_ascii=False))
    logging.getLogger(__name__).info("scenario written to %s", path)


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
    d = sub.add_parser("demo-data", help="export real-data JSON for the frontend prototype")
    d.add_argument("--prices-csv", required=True)
    d.add_argument("--out", default=str(REPO_ROOT / "frontend" / "src" / "data"))
    d.add_argument("--scenario-date", help="replay a past day through the rules (scenario.json)")
    d.set_defaults(func=_demo_data)
    r = sub.add_parser("products-report", help="render the product ranking to Markdown")
    r.add_argument("--out", default=str(REPO_ROOT / "docs" / "PRODUCTS.md"))
    r.set_defaults(func=_products_report)
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
