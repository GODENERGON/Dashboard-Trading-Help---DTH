"""Objective, explainable product scores within each category (ADR 0009).

Each criterion yields 0-100; the total is the weighted sum. Every score carries a plain-Italian
explanation so the UI can answer "Perché è qui?".
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any

from dth.products.catalog import Catalog, Product

WEIGHTS: dict[str, float] = {
    "costo": 0.35,
    "fiscalita": 0.25,
    "dimensione": 0.20,
    "fedelta": 0.10,
    "storicita": 0.10,
}
COST_POINTS_PER_TENTH = 25.0  # points lost for every 0.10% of cost above the cheapest
FEATURED_MAX = 2
FEATURED_MIN_SCORE = 60.0


@dataclass
class ScoredProduct:
    product: Product
    total: float
    criteria: dict[str, float]
    reasons: dict[str, str]
    featured: bool = False
    rank: int = 0
    warnings: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "rank": self.rank,
            "featured": self.featured,
            "total": round(self.total, 1),
            "criteria": {k: round(v, 1) for k, v in self.criteria.items()},
            "reasons": self.reasons,
            "warnings": self.warnings,
            "product": self.product.model_dump(),
        }


def effective_cost(p: Product) -> float:
    return p.ter_pct - p.withholding_advantage_pct


def _relative(value: float, values: list[float]) -> float:
    """100 for the best (lowest) value in the category, 0 for the worst."""
    lo, hi = min(values), max(values)
    return 100.0 if hi - lo < 1e-12 else 100.0 * (hi - value) / (hi - lo)


def _cost_score(cost: float, cheapest: float) -> float:
    return max(0.0, min(100.0, 100.0 - (cost - cheapest) / 0.10 * COST_POINTS_PER_TENTH))


def _size_score(aum_eur_m: float) -> float:
    if aum_eur_m <= 0:
        return 0.0
    return max(0.0, min(100.0, (math.log10(aum_eur_m) - 2) / 2 * 100))  # 100m→0, 10bn→100


def _age_score(inception_year: int, today_year: int) -> float:
    years = today_year - inception_year
    return max(0.0, min(100.0, (years - 3) / 7 * 100))  # 3y→0, 10y→100


def _tax_score(p: Product) -> tuple[float, str]:
    score, why = 50.0, []
    if p.income == "accumulating":
        score += 30
        why.append("ad accumulazione: i proventi non vengono tassati anno per anno")
    else:
        score -= 30
        why.append("a distribuzione: ogni provento è tassato al 26% quando viene pagato")
    if p.kind == "etc":
        score += 20
        why.append("ETC: le plusvalenze sono redditi diversi e si compensano con le minusvalenze")
    elif p.withholding_advantage_pct > 0:
        score += 10
        why.append("la replica sintetica evita la ritenuta sui dividendi esteri")
    return max(0.0, min(100.0, score)), "; ".join(why)


def score_category(products: list[Product], today_year: int) -> list[ScoredProduct]:
    eligible = [p for p in products if p.eu_retail]
    costs = [effective_cost(p) for p in eligible]
    tds = [p.tracking_diff_pct for p in eligible if p.tracking_diff_pct is not None]
    out: list[ScoredProduct] = []
    for p in eligible:
        tax, tax_why = _tax_score(p)
        if p.tracking_diff_pct is not None and len(tds) > 1:
            fidelity = _relative(p.tracking_diff_pct, tds)
            fid_why = f"tracking difference {p.tracking_diff_pct:+.2f}% annuo"
        else:
            fidelity, fid_why = 50.0, "tracking difference non disponibile (valore neutro)"
        criteria = {
            "costo": _cost_score(effective_cost(p), min(costs)),
            "fiscalita": tax,
            "dimensione": _size_score(p.aum_eur_m),
            "fedelta": fidelity,
            "storicita": _age_score(p.inception_year, today_year),
        }
        cost_why = f"TER {p.ter_pct:.2f}%"
        if p.withholding_advantage_pct:
            cost_why += f", costo effettivo {effective_cost(p):.2f}% dopo il recupero sui dividendi"
        reasons = {
            "costo": cost_why,
            "fiscalita": tax_why,
            "dimensione": f"patrimonio circa {p.aum_eur_m:,.0f} mln €".replace(",", "."),
            "fedelta": fid_why,
            "storicita": f"quotato dal {p.inception_year}",
        }
        warnings = []
        if p.aum_eur_m < 100:
            warnings.append("Fondo piccolo: rischio di chiusura e spread più ampi")
        if p.replication == "synthetic":
            warnings.append("Replica sintetica: esposizione alla controparte dello swap")
        total = sum(WEIGHTS[k] * v for k, v in criteria.items())
        out.append(ScoredProduct(p, total, criteria, reasons, warnings=warnings))

    out.sort(key=lambda s: (-s.total, effective_cost(s.product), s.product.ticker))
    for i, s in enumerate(out, start=1):
        s.rank = i
        s.featured = i <= FEATURED_MAX and s.total >= FEATURED_MIN_SCORE
    return out


def rank_catalog(catalog: Catalog, today_year: int | None = None) -> dict[str, Any]:
    year = today_year or catalog.verified_on.year
    result: dict[str, Any] = {"verified_on": str(catalog.verified_on), "weights": WEIGHTS}
    cats = {}
    for cat, label in catalog.categories.items():
        products = catalog.in_category(cat)
        scored = score_category(products, year)
        cats[cat] = {
            "label": label,
            "featured": [s.to_dict() for s in scored if s.featured],
            "others": [s.to_dict() for s in scored if not s.featured],
            "not_available": [
                {"product": p.model_dump(), "reason": p.note or "Non acquistabile da un retail UE"}
                for p in products
                if not p.eu_retail
            ],
        }
    result["categories"] = cats
    return result
