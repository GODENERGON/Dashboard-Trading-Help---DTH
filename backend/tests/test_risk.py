from __future__ import annotations

import pandas as pd
import pytest

from dth.risk import DEFAULT_LIMITS, apply_limits, drawdown_state, position_size_atr
from dth.risk.limits import DrawdownState
from dth.risk.sizing import vol_target_scale
from dth.testing import synthetic_prices


def test_apply_limits_caps_weight_and_gross() -> None:
    w = pd.DataFrame(
        {"A": [0.6, 0.2], "B": [0.6, 0.2], "C": [0.6, 0.2], "D": [0.6, 0.2], "E": [0.6, 0.2]}
    )
    out = apply_limits(w)
    assert (out.abs() <= DEFAULT_LIMITS.max_weight + 1e-12).all().all()
    assert (out.abs().sum(axis=1) <= DEFAULT_LIMITS.max_gross + 1e-12).all()
    assert out.iloc[1].tolist() == [0.2] * 5  # untouched when within limits


def test_limits_cannot_be_loosened_without_adr() -> None:
    assert DEFAULT_LIMITS.tightened(max_weight=0.2).max_weight == 0.2
    with pytest.raises(ValueError):
        DEFAULT_LIMITS.tightened(max_weight=0.5)
    with pytest.raises(ValueError):
        DEFAULT_LIMITS.tightened(dd_stop=-0.4)


def test_allocation_limits_adr_0006() -> None:
    from dth.risk.limits import allocation_breaches

    assert DEFAULT_LIMITS.max_crypto == 0.10
    assert DEFAULT_LIMITS.max_startups == 0.15
    ok = {"etf": 75.0, "crypto": 10.0, "startups": 15.0}
    assert allocation_breaches(ok) == {}
    bad = {"etf": 70.0, "crypto": 12.0, "startups": 18.0}
    assert set(allocation_breaches(bad)) == {"crypto", "startups"}
    with pytest.raises(ValueError):
        DEFAULT_LIMITS.tightened(max_startups=0.25)


def test_drawdown_state() -> None:
    assert drawdown_state(pd.Series([1.0, 1.1, 1.05])) is DrawdownState.NORMAL
    assert drawdown_state(pd.Series([1.0, 1.0, 0.88])) is DrawdownState.WARNING
    assert drawdown_state(pd.Series([1.0, 1.0, 0.75])) is DrawdownState.STOP


def test_vol_target_never_levers() -> None:
    rets = synthetic_prices(periods=600)["BOND_GOV"].pct_change().fillna(0)
    scale = vol_target_scale(rets, target_vol=0.5)
    assert scale.max() <= 1.0


def test_position_size_atr() -> None:
    # 10k capital, 1% risk = 100; stop distance 2*2.5 = 5 → 20 units (cost 2000 < capital)
    assert position_size_atr(10_000, entry=100, atr=2.5) == 20
    with pytest.raises(ValueError):
        position_size_atr(10_000, entry=100, atr=0)
