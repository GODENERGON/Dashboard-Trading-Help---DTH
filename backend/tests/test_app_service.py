from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pandas as pd
import pytest
from fastapi.testclient import TestClient

from dth.app.data_service import DataService
from dth.app.overview import build_overview
from dth.core.config import REPO_ROOT
from dth.highlights import Context
from dth.highlights.engine import evaluate_rules
from dth.highlights.rules import ExampleDrawdownRule, StaleDataRule

CONFIG = REPO_ROOT / "config"


@pytest.fixture
def svc(tmp_path) -> DataService:
    return DataService(data_dir=tmp_path, config_dir=CONFIG)


def test_seed_is_used_offline(svc) -> None:
    panel = svc.panel()
    assert panel.index.is_monotonic_increasing and not panel.index.has_duplicates
    assert {"SWDA.MI", "IBGL.MI", "SGLD.MI", "XEON.MI"} <= set(panel.columns)
    st = svc.status()
    assert st["source"].startswith("seme") and st["fetched_at"] is None
    assert svc.needs_refresh()


def test_refresh_failure_keeps_seed_and_counts(svc, monkeypatch) -> None:
    import dth.research.ucits_trend as ut

    def boom(*a, **k):
        raise ConnectionError("rete non disponibile")

    monkeypatch.setattr(ut, "build_price_panel", boom)
    for _ in range(3):
        assert svc.refresh(provider=object()) is False
    st = svc.status()
    assert st["failures"] == 3 and "rete" in st["last_error"]
    assert not svc.panel_path.exists()


def test_refresh_success_writes_panel(svc, monkeypatch) -> None:
    import dth.research.ucits_trend as ut

    seed = svc.panel()
    monkeypatch.setattr(ut, "build_price_panel", lambda *a, **k: (seed, {}))
    assert svc.refresh(provider=object()) is True
    assert svc.panel_path.exists()
    st = svc.status()
    assert st["source"] == "Yahoo Finance" and st["failures"] == 0
    assert not svc.needs_refresh()
    assert svc.needs_refresh(now=datetime.now(UTC) + timedelta(days=1))


def test_refresh_rejects_truncated_download(svc, monkeypatch) -> None:
    import dth.research.ucits_trend as ut

    seed = svc.panel()
    monkeypatch.setattr(ut, "build_price_panel", lambda *a, **k: (seed.iloc[-100:], {}))
    assert svc.refresh(provider=object()) is False
    assert "incompleti" in svc.status()["last_error"]


def test_stale_and_broken_source_rules(svc) -> None:
    panel = svc.panel()
    as_of = panel.index[-1]
    fresh = Context(panel, as_of, extras={"today": as_of, "data_status": {}})
    assert StaleDataRule().evaluate(fresh) is None
    old = Context(panel, as_of, extras={"today": as_of + pd.Timedelta(days=14)})
    h = StaleDataRule().evaluate(old)
    assert h is not None and h.level == "attention"
    broken = Context(panel, as_of, extras={"data_status": {"failures": 3, "last_error": "x"}})
    assert StaleDataRule().evaluate(broken).level == "critical"


def test_drawdown_rule_levels() -> None:
    idx = pd.bdate_range("2024-01-01", periods=4)
    ctx = lambda eq: Context(pd.DataFrame(index=idx), idx[-1], extras={"example_equity": eq})  # noqa: E731
    assert ExampleDrawdownRule().evaluate(ctx(pd.Series([100, 101, 99, 98.0], idx))) is None
    assert ExampleDrawdownRule().evaluate(ctx(pd.Series([100, 95, 89, 88.0], idx))).level == (
        "attention"
    )
    assert ExampleDrawdownRule().evaluate(ctx(pd.Series([100, 90, 79, 75.0], idx))).level == (
        "critical"
    )


def test_engine_sorts_critical_first_and_survives_broken_rule() -> None:
    from dth.highlights import Highlight

    class Fixed:
        def __init__(self, level):
            self.id, self.level = level, level

        def evaluate(self, ctx):
            return Highlight(self.id, self.level, "t", "e", "2024-01-01")

    class Broken:
        id = "broken"

        def evaluate(self, ctx):
            raise RuntimeError

    out = evaluate_rules([Fixed("attention"), Broken(), Fixed("critical")], None)
    assert [h.level for h in out] == ["critical", "attention"]


def test_overview_shape(svc) -> None:
    body = build_overview(svc.panel(), svc.status())
    assert body["current"] in {"positivo", "misto", "difensivo"}
    assert len(body["weekly"]) > 500
    assert -1 < body["risk"]["drawdown_max"] <= 0
    assert all(h["level"] in {"attention", "critical"} for h in body["highlights"])
    assert not any(h["rule_id"] == "trend_regime" for h in body["highlights"])  # disabled


def test_overview_endpoint(svc, monkeypatch) -> None:
    import dth.api.main as api

    monkeypatch.setattr(api, "data_service", lambda: svc)
    client = TestClient(api.app)
    assert client.get("/status").json()["source"].startswith("seme")
    body = client.get("/overview").json()
    assert body["data_status"]["as_of"] == body["as_of"]


def test_token_required_when_set(svc, monkeypatch) -> None:
    import dth.api.main as api
    from dth.core.config import get_settings

    monkeypatch.setattr(api, "data_service", lambda: svc)
    monkeypatch.setattr(get_settings(), "api_token", "s3cret")
    client = TestClient(api.app)
    assert client.get("/health").status_code == 200
    assert client.get("/status").status_code == 401
    assert client.get("/status", headers={"X-Dabitur-Token": "s3cret"}).status_code == 200


def test_feedback_saved_locally(tmp_path, monkeypatch) -> None:
    import json

    import dth.api.main as api
    from dth.core.config import get_settings

    monkeypatch.setattr(get_settings(), "data_dir", tmp_path)
    client = TestClient(api.app)
    r = client.post("/feedback", json={"message": "Non capisco la banda", "view": "panoramica"})
    assert r.status_code == 200
    line = (tmp_path / "feedback" / "feedback.jsonl").read_text().strip()
    assert json.loads(line)["message"] == "Non capisco la banda"
    assert client.post("/feedback", json={"message": ""}).status_code == 422


def test_sidecar_environment(tmp_path, monkeypatch) -> None:
    from dth.sidecar import configure_environment

    monkeypatch.delenv("DTH_CONFIG_DIR", raising=False)
    monkeypatch.setenv("DTH_DATA_DIR", str(tmp_path / "d"))
    configure_environment(tmp_path / "bundle")
    import os

    assert os.environ["DTH_CONFIG_DIR"] == str(tmp_path / "bundle" / "config")
    assert (tmp_path / "d").is_dir()
