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
