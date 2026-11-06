from __future__ import annotations

from datetime import date

import numpy as np
import pandas as pd
import pytest

from dth.backtest.taxes import CAPITAL, DIVERSE, SymbolTax, TaxModel
from dth.core.config import Instrument, Universe
from dth.research.ucits_trend import build_price_panel, render_markdown, run_study, splice
from dth.testing import synthetic_prices


def test_splice_rescales_proxy_at_first_ucits_date() -> None:
    idx = pd.bdate_range("2020-01-01", periods=10)
    proxy = pd.Series(np.linspace(10, 19, 10), index=idx)
    ucits = pd.Series([100.0, 101.0, 102.0], index=idx[5:8])
    out, n = splice(ucits, proxy)
    assert n == 5
    assert out.loc[idx[5]] == 100.0
    assert out.loc[idx[4]] == pytest.approx(100.0 * 14 / 15)
    assert out.index.is_monotonic_increasing and not out.index.has_duplicates


class _FakeProvider:
    """UCITS listed from 2012, USD proxies from 2005, EURUSD constant 1.25."""

    name = "fake"

    def __init__(self) -> None:
        self.px = synthetic_prices(start="2005-01-03", periods=252 * 12)

    def fetch(self, symbol: str, start: date, end: date) -> pd.DataFrame:
        idx = self.px.index
        if symbol == "EURUSD=X":
            close = pd.Series(1.25, index=idx)
        elif symbol == "CASH.MI":
            close = pd.Series(100.0, index=idx)
        elif symbol.endswith(".MI"):
            base = {"W.MI": "EQ_WORLD", "B.MI": "BOND_GOV", "G.MI": "GOLD"}[symbol]
            close = self.px[base].loc["2012-01-01":] * 0.8
        else:
            close = self.px[{"PW": "EQ_WORLD", "PB": "BOND_GOV", "PG": "GOLD"}[symbol]]
        return pd.DataFrame({"close": close})


def _universe() -> Universe:
    return Universe(
        name="t",
        instruments=[
            Instrument(symbol="W.MI", name="w", asset_class="equity", proxy="PW",
                       tax_category="etf_ucits"),
            Instrument(symbol="B.MI", name="b", asset_class="bond", proxy="PB",
                       tax_category="etf_ucits"),
            Instrument(symbol="G.MI", name="g", asset_class="commodity", proxy="PG",
                       tax_category="etc_etn"),
            Instrument(symbol="CASH.MI", name="c", asset_class="cash", tax_category="etf_ucits"),
        ],
    )  # fmt: skip


def test_panel_and_study_end_to_end() -> None:
    panel, meta = build_price_panel(
        _FakeProvider(), _universe(), date(2005, 1, 1), date(2017, 1, 1), cash_symbol="CASH.MI"
    )
    assert panel.index[0] < pd.Timestamp("2006-01-01")  # proxies extend history
    assert panel["W.MI"].notna().all()
    assert {m.symbol for m in meta} == {"W.MI", "B.MI", "G.MI", "CASH.MI"}

    tax = TaxModel(
        symbols={
            "W.MI": SymbolTax(CAPITAL, 0.26),
            "B.MI": SymbolTax(CAPITAL, 0.125),
            "G.MI": SymbolTax(DIVERSE, 0.26),
            "CASH.MI": SymbolTax(CAPITAL, 0.26),
        }
    )
    report = run_study(panel, tax, cash_symbol="CASH.MI", world="W.MI", bond="B.MI")
    d = report["default"]
    assert d["net"]["cagr_after_liquidation_tax"] < d["gross"]["cagr"]
    assert len(report["grid"]["rows"]) == 18
    assert report["walk_forward"]["folds"]
    md = render_markdown(report, [m.__dict__ for m in meta])
    assert "CAGR netto" in md and "Limiti noti" in md
