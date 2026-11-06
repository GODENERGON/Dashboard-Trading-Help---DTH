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
