from __future__ import annotations

from pathlib import Path

import pytest
from pydantic import ValidationError

from dth.core.config import REPO_ROOT
from dth.core.sources import SourceKind, SourceRegistry, Status, load_registry

EXAMPLE = REPO_ROOT / "config" / "sources.example.yaml"


def test_example_registry_is_valid() -> None:
    reg = load_registry(EXAMPLE)
    assert len(reg.sources) >= 30
    assert reg.get("fred").reliability == "A"


def test_every_user_category_has_a_source() -> None:
    reg = load_registry(EXAMPLE)
    for cat in ("real_estate", "etf", "indices", "crypto", "commodities", "startups", "ipo",
                "news", "portfolio", "llm"):  # fmt: skip
        assert reg.by_category(cat, include_inactive=True), f"no source for {cat}"


def test_owner_portals_present_and_unlicensed_flagged() -> None:
    reg = load_registry(EXAMPLE)
    for pid in ("ibkr", "degiro", "scalable", "binance", "coinbase", "bitfinex", "manual"):
        assert reg.get(pid).kind is SourceKind.PORTAL
    assert reg.get("binance").warning and reg.get("bitfinex").warning
    assert reg.get("coinbase").warning is None


def test_llm_sources_are_off_by_default() -> None:
    reg = load_registry(EXAMPLE)
    llms = [s for s in reg.sources if s.kind is SourceKind.LLM]
    assert llms and all(s.status is Status.DISABLED for s in llms)


def test_startup_watchlist_covers_owner_sectors() -> None:
    import yaml

    data = yaml.safe_load((REPO_ROOT / "config" / "watchlist.startups.example.yaml").read_text())
    sectors = {s["id"]: s for s in data["sectors"]}
    assert set(sectors) == {
        "nuclear", "ai_datacenter", "biotech_longevity", "robotics", "ai",
        "advanced_materials", "food",
    }  # fmt: skip
    for s in sectors.values():
        assert s["companies"], s["id"]
        for c in s["companies"]:
            assert c["region"] in {"italia", "europa", "mondo"}
            assert c["status"] in {"seed", "candidate"}
    assert any(c["name"] == "Newcleo" for c in sectors["nuclear"]["companies"])


def test_registry_rejects_duplicates_and_unknown_categories(tmp_path: Path) -> None:
    base = {
        "id": "x", "name": "X", "kind": "data", "categories": ["prices"],
        "url": "https://example.com", "access": "api", "cost": "free", "auth": "none",
        "reliability": "A", "status": "active",
    }  # fmt: skip
    with pytest.raises(ValidationError):
        SourceRegistry.model_validate({"version": 1, "sources": [base, base]})
    with pytest.raises(ValidationError):
        SourceRegistry.model_validate(
            {"version": 1, "sources": [{**base, "categories": ["astrology"]}]}
        )
