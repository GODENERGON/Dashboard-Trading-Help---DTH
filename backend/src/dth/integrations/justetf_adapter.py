"""justETF data via justetf-scraping (github.com/druzsan/justetf-scraping, MIT).

Used only to *propose* updates (TER, fund size) for the product catalog: the result is a diff
report reviewed by a person, never an automatic overwrite. Run on demand (workflow
`research`), not from the desktop app: justETF's terms of use must be checked before any
regular automation (see config/sources.example.yaml, source `justetf`).
Requires the ``[justetf]`` extra; the import is lazy.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

import pandas as pd

from dth.products.catalog import Catalog

# Column names in justetf_scraping.load_overview(); kept in one place in case they change.
COLS = {"isin": "isin", "ter": "ter", "size": "size"}
TER_TOLERANCE = 0.005  # percentage points
SIZE_TOLERANCE = 0.25  # relative change in fund size worth reporting


@dataclass(frozen=True)
class CatalogChange:
    isin: str
    ticker: str
    field: str
    catalog_value: float
    justetf_value: float

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def load_overview() -> pd.DataFrame:  # pragma: no cover - network
    import justetf_scraping  # lazy: optional dependency

    return justetf_scraping.load_overview()


def _overview_by_isin(overview: pd.DataFrame) -> pd.DataFrame:
    df = overview.reset_index() if COLS["isin"] not in overview.columns else overview
    return df.drop_duplicates(COLS["isin"]).set_index(COLS["isin"])


def diff_catalog(catalog: Catalog, overview: pd.DataFrame) -> dict[str, Any]:
    """Compare catalog TER and fund size with justETF; report changes and missing ISINs."""
    data = _overview_by_isin(overview)
    changes: list[CatalogChange] = []
    missing: list[str] = []
    for p in catalog.products:
        if not p.eu_retail:
            continue
        if p.isin not in data.index:
            missing.append(p.isin)
            continue
        row = data.loc[p.isin]
        ter = row.get(COLS["ter"])
        if pd.notna(ter) and abs(float(ter) - p.ter_pct) > TER_TOLERANCE:
            changes.append(CatalogChange(p.isin, p.ticker, "ter_pct", p.ter_pct, float(ter)))
        size = row.get(COLS["size"])
        moved = pd.notna(size) and p.aum_eur_m > 0
        if moved and abs(float(size) / p.aum_eur_m - 1) > SIZE_TOLERANCE:
            changes.append(CatalogChange(p.isin, p.ticker, "aum_eur_m", p.aum_eur_m, float(size)))
    return {"changes": [c.to_dict() for c in changes], "missing_isins": missing}
