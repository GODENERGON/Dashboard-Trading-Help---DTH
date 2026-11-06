from __future__ import annotations

import numpy as np
import pandas as pd

from dth.signals.annual_optimized import AnnualOptimized, capped_weights
from dth.testing import synthetic_prices


class _InverseVol:
    """Tiny stand-in for a skfolio estimator (fit + weights_)."""

    def fit(self, X: pd.DataFrame) -> _InverseVol:
        iv = 1 / X.std()
        self.weights_ = (iv / iv.sum()).to_numpy()
        return self


def _signal() -> AnnualOptimized:
    return AnnualOptimized(
        model_factory=_InverseVol,
        slots={"world": ("EQ_WORLD", "EQ_EM"), "bond": ("BOND_GOV",), "gold": ("GOLD",)},
        caps={"world": 0.6},
        lookback=252,
    )


def test_capped_weights_redistributes() -> None:
    w = capped_weights(pd.Series({"a": 0.8, "b": 0.1, "c": 0.1}), {"a": 0.6})
    assert w["a"] == 0.6 and abs(w.sum() - 1) < 1e-12 and abs(w["b"] - 0.2) < 1e-12


def test_weights_constant_within_year_and_sum_to_one() -> None:
    px = synthetic_prices(periods=252 * 6)
    w = _signal().compute(px)
    live = w[w.sum(axis=1) > 0]
    assert np.allclose(live.sum(axis=1), 1.0)
    for _, grp in live.groupby(live.index.year):
        body = grp.iloc[:-1].round(12)  # the last close of the year carries the new weights
        if len(body) > 1:
            assert (body == body.iloc[0]).all().all()
    assert (w.loc[: px.index[251]] == 0).all().all()  # no weights before enough history


def test_world_slot_uses_fallback_before_listing() -> None:
    px = synthetic_prices(periods=252 * 6)
    px.loc[px.index[: 252 * 3], "EQ_WORLD"] = np.nan
    w = _signal().compute(px)
    early = w.loc[px.index[252 * 2]]
    assert early["EQ_WORLD"] == 0 and early["EQ_EM"] > 0
    late = w.iloc[-1]
    assert late["EQ_WORLD"] > 0 and late["EQ_EM"] == 0


def test_no_lookahead() -> None:
    from tests.test_no_lookahead import assert_no_lookahead

    assert_no_lookahead(_signal(), synthetic_prices(periods=252 * 6))
