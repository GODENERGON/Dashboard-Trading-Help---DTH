from __future__ import annotations

import numpy as np
import pandas as pd

from dth.highlights import Context, HighlightRule
from dth.regime import DEFENSIVE, MIXED, POSITIVE, TrendRegimeRule, evaluate_regime, regime_series
from dth.testing import synthetic_prices


def _panel(trend_up: bool, n: int = 400) -> pd.DataFrame:
    idx = pd.bdate_range("2020-01-01", periods=n)
    step = 0.001 if trend_up else -0.001
    base = 100 * np.exp(np.arange(n) * step)
    return pd.DataFrame(
        {"SWDA.MI": base, "B": base * 0.5, "C": base * 2, "XEON.MI": 100.0}, index=idx
    )


def test_regime_states() -> None:
    assert regime_series(_panel(True)).iloc[-1] == POSITIVE
    assert regime_series(_panel(False)).iloc[-1] == DEFENSIVE
    mixed = _panel(True)
    mixed["B"] = mixed["B"].iloc[::-1].to_numpy()  # falling
    mixed["C"] = mixed["C"].iloc[::-1].to_numpy()
    assert regime_series(mixed).iloc[-1] == MIXED
    assert regime_series(_panel(True)).iloc[0] == "n/d"


def test_regime_has_no_lookahead() -> None:
    px = synthetic_prices(periods=252 * 5).rename(columns={"EQ_WORLD": "SWDA.MI"})
    base = regime_series(px, cash_symbol=None)
    cut = px.index[700]
    pert = px.copy()
    pert.loc[pert.index > cut] *= 0.5
    pd.testing.assert_series_equal(base.loc[:cut], regime_series(pert, cash_symbol=None).loc[:cut])


def test_rule_is_informational_by_default() -> None:
    down = _panel(False)
    ctx = Context(prices=down, as_of=down.index[-1])
    assert TrendRegimeRule().evaluate(ctx) is None
    assert TrendRegimeRule().explain(ctx).level == "critical"


def test_rule_levels() -> None:
    rule = TrendRegimeRule(colors_dashboard=True)
    assert isinstance(rule, HighlightRule)
    up, down = _panel(True), _panel(False)
    assert rule.evaluate(Context(prices=up, as_of=up.index[-1])) is None
    h = rule.evaluate(Context(prices=down, as_of=down.index[-1]))
    assert h is not None and h.level == "critical" and h.data["regime"] == DEFENSIVE
    assert "200 giorni" in h.explanation


def test_evaluate_regime_shapes() -> None:
    px = synthetic_prices(periods=252 * 8).rename(columns={"EQ_WORLD": "SWDA.MI"})
    reg = regime_series(px, cash_symbol=None)
    stats = evaluate_regime(reg, px["SWDA.MI"])
    assert set(stats) == {POSITIVE, MIXED, DEFENSIVE}
    assert abs(sum(s["share_of_time"] for s in stats.values()) - 1) < 1e-9
