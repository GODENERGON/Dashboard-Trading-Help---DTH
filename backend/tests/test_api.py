from __future__ import annotations

from fastapi.testclient import TestClient

from dth.api.main import app

client = TestClient(app)


def test_health() -> None:
    assert client.get("/health").json()["status"] == "ok"


def test_universe_is_ucits_example() -> None:
    body = client.get("/universe").json()
    assert body["name"] == "ucits-core"
    assert all(i["symbol"].endswith(".MI") for i in body["instruments"])


def test_no_order_endpoints() -> None:
    paths = {r.path for r in app.routes}
    assert not any("order" in p for p in paths), "order endpoints require an ADR (RISK_POLICY)"


def test_validation_demo_shape() -> None:
    body = client.get("/validation/demo").json()
    assert body["signal"] == "dual_momentum_topk"
    assert "sharpe" in body["oos_metrics"]
    assert len(body["equity"]) > 252


def test_trend_regime_endpoint(tmp_path, monkeypatch) -> None:
    import numpy as np
    import pandas as pd

    import dth.api.main as api
    from dth.store import ParquetStore

    store = ParquetStore(tmp_path)
    monkeypatch.setattr(api, "_store", lambda: store)
    assert client.get("/regime/trend").status_code == 503

    idx = pd.bdate_range("2023-01-02", periods=400)
    for i, sym in enumerate(api.load_universe().symbols):
        close = 100 * np.exp(-np.arange(400) * 0.001 * (1 + i / 10))  # everything falling
        store.write(
            api.PRICES_DATASET, sym, pd.DataFrame({"close": close}, index=idx), source="test"
        )
    body = client.get("/regime/trend").json()
    assert body["regime"] == "difensivo"
    assert body["colors_dashboard"] is False and body["highlight"] is None
    assert body["detail"]["level"] == "critical"
    assert len(body["history"]) == 260
