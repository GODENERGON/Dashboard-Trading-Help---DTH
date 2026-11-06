"""Panoramica payload: regime, example risk, highlights, data status."""

from __future__ import annotations

from typing import Any

import pandas as pd

from dth.backtest import BacktestConfig
from dth.backtest.portfolio import simulate_portfolio
from dth.highlights import Context
from dth.highlights.engine import evaluate_rules
from dth.highlights.rules import ExampleDrawdownRule, StaleDataRule
from dth.regime import TrendRegimeRule, asset_in_trend, regime_series
from dth.signals import CoreSatellite, MultiAssetTrend

CASH = "XEON.MI"
WORLD = ("SWDA.MI", "CSSPX.MI")
EXAMPLE_LABEL = "Esempio: bilanciato 55/35/10 da 100.000 € (dati reali, lordo)"


def example_equity(prices: pd.DataFrame, start: str = "2016-01-01") -> pd.Series:
    balanced = CoreSatellite(
        core=((WORLD, 0.55), (("IBGL.MI",), 0.35), (("SGLD.MI",), 0.10)),
        satellite=MultiAssetTrend(cash_symbol=None),
        satellite_share=0.0,
    )
    eq = simulate_portfolio(balanced, prices, BacktestConfig(rebalance="YE")).equity
    return eq.loc[start:]


def build_overview(prices: pd.DataFrame, data_status: dict[str, Any]) -> dict[str, Any]:
    as_of = prices.index[-1]
    regime = regime_series(prices, CASH, WORLD)
    weekly = regime[regime != "n/d"].resample("W-FRI").last().dropna()
    eq = example_equity(prices)
    dd = eq / eq.cummax() - 1
    ctx = Context(
        prices=prices, as_of=as_of, extras={"data_status": data_status, "example_equity": eq}
    )
    rules = [ExampleDrawdownRule(), StaleDataRule(), TrendRegimeRule()]
    highlights = evaluate_rules(rules, ctx)
    trend_last = asset_in_trend(prices.drop(columns=[c for c in [CASH] if c in prices])).iloc[-1]
    return {
        "as_of": str(as_of.date()),
        "current": regime.iloc[-1],
        "in_trend": {k: bool(v) for k, v in trend_last.items() if pd.notna(v)},
        "weekly": [{"d": str(d.date()), "s": s} for d, s in weekly.items()],
        "risk": {
            "label": EXAMPLE_LABEL,
            "value": float(eq.iloc[-1] / eq.iloc[0] * 100_000),
            "drawdown_now": float(dd.iloc[-1]),
            "drawdown_max": float(dd.min()),
            "vol_3m": float(eq.pct_change().iloc[-63:].std() * (252**0.5)),
            "equity_monthly": [
                {"d": str(d.date()), "v": round(float(v), 2)}
                for d, v in (eq / eq.iloc[0] * 100).resample("ME").last().items()
            ],
        },
        "highlights": [h.to_dict() for h in highlights],
        "data_status": data_status,
    }
