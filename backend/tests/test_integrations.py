from __future__ import annotations

import pandas as pd
import pytest

from dth.connectors import CcxtConnector, PortalConnector
from dth.core.config import REPO_ROOT
from dth.integrations.financedatabase_adapter import new_candidates, search_etfs
from dth.integrations.justetf_adapter import diff_catalog
from dth.products import load_catalog

CATALOG = load_catalog(REPO_ROOT / "config" / "products.example.yaml")


class _FakeETFs:
    def search(self, **kwargs):
        assert kwargs == {"name": "MSCI World", "exchange": "MIL"}
        return pd.DataFrame(
            {
                "name": ["iShares Core MSCI World", "Some MSCI World ETF", "Old ETF", "No ISIN"],
                "currency": ["EUR"] * 4,
                "category_group": ["Equities"] * 4,
                "category": ["Large Cap"] * 4,
                "family": ["iShares", "X", "Y", "Z"],
                "exchange": ["MIL"] * 4,
                "isin": ["IE00B4L5Y983", "IE0000000001", "IE0000000002", None],
                "delisted": [False, False, True, False],
            },
            index=["SWDA.MI", "XXXX.MI", "OLD.MI", "NOIS.MI"],
        )


def test_financedatabase_discovers_only_new_listed_products() -> None:
    found = search_etfs("MSCI World", etfs=_FakeETFs())
    assert {c.symbol for c in found} == {"SWDA.MI", "XXXX.MI", "NOIS.MI"}  # delisted removed
    new = new_candidates(CATALOG, found)
    assert [c.isin for c in new] == ["IE0000000001"]  # SWDA already in catalog, no-ISIN dropped


def test_justetf_diff_reports_ter_and_size_changes() -> None:
    overview = pd.DataFrame(
        {"isin": ["IE00B4L5Y983", "IE00BJ0KDQ92"], "ter": [0.20, 0.10], "size": [128000, 40000]}
    )
    report = diff_catalog(CATALOG, overview)
    fields = {(c["ticker"], c["field"]) for c in report["changes"]}
    assert fields == {("XDWD", "ter_pct"), ("XDWD", "aum_eur_m")}
    assert "IE00B3YCGJ38" in report["missing_isins"]
    assert "US78462F1030" not in report["missing_isins"]  # not EU-retail, skipped


class _FakeExchange:
    def fetch_balance(self):
        return {"total": {"BTC": 0.5, "EUR": 120.0, "ETH": 0.0}}

    def create_order(self, *a, **k):  # must never be reachable through the connector
        raise AssertionError("trading called")


def test_ccxt_connector_is_read_only() -> None:
    conn = CcxtConnector("coinbase", "k", "s", client=_FakeExchange())
    assert isinstance(conn, PortalConnector)
    assert [(b.asset, b.amount) for b in conn.balances()] == [("BTC", 0.5), ("EUR", 120.0)]
    with pytest.raises(PermissionError):
        conn.create_order("BTC/EUR", "market", "buy", 1)
    with pytest.raises(ValueError):
        CcxtConnector("unknown-exchange", "k", "s", client=_FakeExchange())
