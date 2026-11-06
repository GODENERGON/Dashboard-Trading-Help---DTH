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


def test_llm_sources_are_off_by_default() -> None:
    reg = load_registry(EXAMPLE)
    llms = [s for s in reg.sources if s.kind is SourceKind.LLM]
    assert llms and all(s.status is Status.DISABLED for s in llms)


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
