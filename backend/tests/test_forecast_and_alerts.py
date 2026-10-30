from __future__ import annotations

import importlib
import sys

import numpy as np

from dth.alerts import AlertGate
from dth.forecast import EwmaVolatility, Forecaster, HistoricalQuantiles
from dth.forecast.base import pinball_loss, qlike, skill_score


def test_baselines_honour_contract() -> None:
    rng = np.random.default_rng(1)
    r = rng.normal(0, 0.01, 1000)
    for f in (EwmaVolatility(), HistoricalQuantiles()):
        assert isinstance(f, Forecaster)
        res = f.forecast(r, horizon=5)
        assert res.point.shape == (5,)
    vol = EwmaVolatility().forecast(r, 1).point[0]
    assert 0.007 < vol < 0.013
    q = HistoricalQuantiles().forecast(r, 3).quantiles
    assert (q[0.1] < q[0.5]).all() and (q[0.5] < q[0.9]).all()


def test_losses_and_skill() -> None:
    y = np.array([0.0, 1.0])
    assert pinball_loss(y, np.array([0.0, 1.0]), 0.5) == 0
    assert qlike(np.array([1.0, 2.0]), np.array([1.0, 2.0])) == 0
    assert skill_score(0.8, 1.0) > 0 > skill_score(1.2, 1.0)


def test_core_does_not_import_heavy_deps() -> None:
    for mod in [m for m in sys.modules if m.startswith("dth")]:
        del sys.modules[mod]
    importlib.import_module("dth.api.main")
    assert "torch" not in sys.modules
    assert "timesfm" not in sys.modules


def test_alert_gate_cooldown() -> None:
    gate = AlertGate(cooldown_s=60)
    assert gate.allow("x", now=0)
    assert not gate.allow("x", now=30)
    assert gate.allow("y", now=30)
    assert gate.allow("x", now=61)
