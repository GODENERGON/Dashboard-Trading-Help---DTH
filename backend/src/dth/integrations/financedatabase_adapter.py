"""FinanceDatabase (github.com/JerBouma/FinanceDatabase, MIT) — product discovery.

Metadata only (no prices, no TER): used to propose ETF candidates for the product catalog that
are not yet in it. Requires the ``[catalog]`` extra; the import is lazy.
"""

from __future__ import annotations

import logging
from dataclasses import asdict, dataclass
from typing import Any

import pandas as pd

from dth.products.catalog import Catalog

log = logging.getLogger(__name__)

# Borsa Italiana exchange code used by FinanceDatabase.
BORSA_ITALIANA = "MIL"


@dataclass(frozen=True)
class Candidate:
    symbol: str
    isin: str | None
    name: str
    currency: str | None
    category_group: str | None
    category: str | None
    family: str | None
    exchange: str | None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _frame_to_candidates(df: pd.DataFrame) -> list[Candidate]:
    out = []
    for symbol, row in df.iterrows():
        get = row.get
        isin = get("isin")
        out.append(
            Candidate(
                symbol=str(symbol),
                isin=str(isin) if isinstance(isin, str) and len(isin) == 12 else None,
                name=str(get("name", "")),
                currency=get("currency"),
                category_group=get("category_group"),
                category=get("category"),
                family=get("family"),
                exchange=get("exchange"),
            )
        )
    return out


def search_etfs(
    name: str, exchange: str | None = BORSA_ITALIANA, etfs: Any = None
) -> list[Candidate]:
    """Search ETFs by name (e.g. "MSCI World"), by default among Borsa Italiana listings."""
    if etfs is None:
        import financedatabase as fd  # lazy: optional dependency

        etfs = fd.ETFs()
    kwargs = {"name": name}
    if exchange:
        kwargs["exchange"] = exchange
    df = etfs.search(**kwargs)
    df = df[~df.get("delisted", pd.Series(False, index=df.index)).fillna(False).astype(bool)]
    return _frame_to_candidates(df)


def new_candidates(catalog: Catalog, candidates: list[Candidate]) -> list[Candidate]:
    """Candidates whose ISIN is not already in the catalog (deduplicated by ISIN)."""
    known = {p.isin for p in catalog.products}
    seen: set[str] = set()
    out = []
    for c in candidates:
        if not c.isin or c.isin in known or c.isin in seen:
            continue
        seen.add(c.isin)
        out.append(c)
    return out
