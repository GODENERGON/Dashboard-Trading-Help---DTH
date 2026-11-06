from __future__ import annotations

import numpy as np
import pandas as pd

from dth.risk import DEFAULT_LIMITS
from dth.signals import MultiAssetTrend
from dth.testing import synthetic_prices


def _prices_with_cash() -> pd.DataFrame:
    px = synthetic_prices(periods=252 * 6)
    px["CASH"] = 100 * np.exp(np.arange(len(px)) * 0.02 / 252)
    return px


def test_weights_sum_to_one_with_cash_and_respect_policy() -> None:
    px = _prices_with_cash()
    w = MultiAssetTrend(cash_symbol="CASH").compute(px)
    assert np.allclose(w.sum(axis=1), 1.0)
    risky = w.drop(columns="CASH")
    assert (risky <= DEFAULT_LIMITS.max_weight + 1e-12).all().all()
    assert (risky >= 0).all().all()


def test_goes_to_cash_when_nothing_trends() -> None:
    idx = pd.bdate_range("2015-01-01", periods=600)
    falling = 100 * np.exp(-np.arange(600) * 0.001)
    px = pd.DataFrame({"A": falling, "B": falling * 0.5, "CASH": 100.0}, index=idx)
    w = MultiAssetTrend(cash_symbol="CASH").compute(px)
    assert (w["CASH"].iloc[300:] == 1.0).all()
    assert (w[["A", "B"]].iloc[300:] == 0).all().all()


def test_assets_without_history_get_zero_weight() -> None:
    px = _prices_with_cash()
    px.loc[px.index[:800], "GOLD"] = np.nan  # listed later
    w = MultiAssetTrend(cash_symbol="CASH").compute(px)
    assert (w["GOLD"].iloc[:1000] == 0).all()
    assert not w.isna().any().any()


def test_top_k_limits_number_of_holdings() -> None:
    px = _prices_with_cash()
    w = MultiAssetTrend(top_k=2, cash_symbol="CASH").compute(px)
    assert ((w.drop(columns="CASH") > 0).sum(axis=1) <= 2).all()


def test_hold_buffer_reduces_switching() -> None:
    px = _prices_with_cash()

    def switches(sig: MultiAssetTrend) -> int:
        held = sig.compute(px).drop(columns="CASH") > 0
        return int((held != held.shift()).sum().sum())

    base = switches(MultiAssetTrend(top_k=2, cash_symbol="CASH"))
    buffered = switches(MultiAssetTrend(top_k=2, hold_buffer=2, cash_symbol="CASH"))
    assert buffered <= base


def test_equal_weighting() -> None:
    px = _prices_with_cash()
    w = MultiAssetTrend(top_k=4, weighting="equal", cash_symbol="CASH").compute(px)
    risky = w.drop(columns="CASH")
    assert set(np.unique(risky.to_numpy().round(10))) <= {0.0, 0.25}


def test_core_satellite_weights_and_fallback() -> None:
    from dth.signals import CoreSatellite

    px = _prices_with_cash()
    px.loc[px.index[:500], "EQ_WORLD"] = np.nan  # world ETF listed later → fallback to EQ_EM
    sig = CoreSatellite(
        core=((("EQ_WORLD", "EQ_EM"), 0.6), (("BOND_GOV",), 0.4)),
        satellite=MultiAssetTrend(cash_symbol="CASH"),
        satellite_share=0.3,
    )
    w = sig.compute(px)
    assert np.allclose(w.sum(axis=1), 1.0)
    early, late = px.index[100], px.index[-1]
    assert w.loc[early, "EQ_EM"] >= 0.42 - 1e-12  # 0.7 * 0.6 from the core fallback
    assert w.loc[early, "EQ_WORLD"] == 0
    assert w.loc[late, "BOND_GOV"] >= 0.28 - 1e-12  # 0.7 * 0.4 core bond
