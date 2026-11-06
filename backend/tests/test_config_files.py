"""Consistency checks across the example configuration files."""

from __future__ import annotations

from datetime import date

import yaml

from dth.core.config import REPO_ROOT, load_universe

CONFIG = REPO_ROOT / "config"


def _yaml(name: str) -> dict:
    return yaml.safe_load((CONFIG / name).read_text(encoding="utf-8"))


def test_universe_instruments_have_known_tax_category() -> None:
    tax = _yaml("tax.it.example.yaml")
    universe = load_universe(CONFIG / "universe.example.yaml")
    assert len(universe.instruments) >= 6
    for inst in universe.instruments:
        assert inst.tax_category in tax["categories"], inst.symbol
    classes = {i.asset_class for i in universe.instruments}
    assert {"equity", "bond", "commodity", "cash"} <= classes


def test_tax_rules_are_dated_and_sane() -> None:
    tax = _yaml("tax.it.example.yaml")
    assert isinstance(tax["verified_on"], date)
    assert tax["sources"]
    cats = tax["categories"]
    assert cats["etf_ucits"]["gains"] == "redditi_di_capitale"
    assert cats["crypto"]["rate"] == 0.33
    assert all(0 < c["rate"] < 0.5 for c in cats.values())
    assert tax["losses_carry_forward"]["years"] == 4


def test_highlight_rules_have_unique_ids_and_valid_levels() -> None:
    rules = _yaml("highlights.example.yaml")["rules"]
    ids = [r["id"] for r in rules]
    assert len(ids) == len(set(ids))
    assert all(r["level"] in {"attention", "critical"} for r in rules)
    locked = {r["id"] for r in rules if r.get("locked")}
    assert {"drawdown_stop", "allocation_limits", "platform_warning"} <= locked
