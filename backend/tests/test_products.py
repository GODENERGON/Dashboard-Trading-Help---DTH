from __future__ import annotations

import pytest
from pydantic import ValidationError

from dth.core.config import REPO_ROOT
from dth.products import build_model_portfolios, load_catalog, rank_catalog
from dth.products.catalog import Catalog
from dth.products.scorecard import WEIGHTS

CATALOG = REPO_ROOT / "config" / "products.example.yaml"


@pytest.fixture(scope="module")
def ranking() -> dict:
    return rank_catalog(load_catalog(CATALOG))


def test_weights_sum_to_one() -> None:
    assert sum(WEIGHTS.values()) == pytest.approx(1.0)


def test_catalog_valid_and_rejects_duplicates() -> None:
    cat = load_catalog(CATALOG)
    assert len(cat.products) >= 20
    raw = cat.model_dump()
    raw["products"].append(raw["products"][0])
    with pytest.raises(ValidationError):
        Catalog.model_validate(raw)


def test_featured_come_first_and_respect_threshold(ranking: dict) -> None:
    for cat in ranking["categories"].values():
        featured, others = cat["featured"], cat["others"]
        assert len(featured) <= 2
        assert all(f["total"] >= 60 for f in featured)
        if featured and others:
            assert min(f["total"] for f in featured) >= max(o["total"] for o in others)
        ranks = [p["rank"] for p in featured + others]
        assert ranks == sorted(ranks)


def test_us_domiciled_etf_is_not_available(ranking: dict) -> None:
    us = ranking["categories"]["equity_us"]
    assert [x["product"]["ticker"] for x in us["not_available"]] == ["SPY"]
    listed = [p["product"]["ticker"] for p in us["featured"] + us["others"]]
    assert "SPY" not in listed


def test_tax_and_cost_logic_shows_in_ranking(ranking: dict) -> None:
    us = ranking["categories"]["equity_us"]
    order = [p["product"]["ticker"] for p in us["featured"] + us["others"]]
    assert order.index("IUSA") > order.index("CSSPX")  # distributing ranks below accumulating
    gold = ranking["categories"]["gold"]
    gold_order = [p["product"]["ticker"] for p in gold["featured"] + gold["others"]]
    assert gold_order[-1] == "PHAU"  # 0.39% TER is the most expensive gold ETC
    re_ = ranking["categories"]["real_estate"]
    first = (re_["featured"] + re_["others"])[0]
    assert "accumulazione" in first["reasons"]["fiscalita"]


def test_every_score_is_explained(ranking: dict) -> None:
    for cat in ranking["categories"].values():
        for p in cat["featured"] + cat["others"]:
            assert set(p["reasons"]) == set(WEIGHTS)
            assert all(0 <= v <= 100 for v in p["criteria"].values())


def test_model_portfolios(ranking: dict) -> None:
    models = build_model_portfolios(ranking)
    assert "non è una raccomandazione" in models["disclaimer"].lower()
    for m in models["models"].values():
        assert sum(line["weight"] for line in m["lines"]) == pytest.approx(1.0)
        assert all(line["ticker"] for line in m["lines"])
        assert 0 < m["weighted_ter_pct"] < 0.3


def test_products_markdown_matches_repo_doc(ranking: dict) -> None:
    from dth.products.report import render_products_markdown

    md = render_products_markdown(ranking)
    assert md == (REPO_ROOT / "docs" / "PRODUCTS.md").read_text(encoding="utf-8"), (
        "docs/PRODUCTS.md is stale: run `python -m dth.cli products-report`"
    )
