"""Product catalog schema (config/products.example.yaml, ADR 0009)."""

from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Literal

import yaml
from pydantic import BaseModel, Field, model_validator


class Product(BaseModel):
    isin: str = Field(min_length=12, max_length=12)
    ticker: str
    name: str
    category: str
    kind: Literal["etf", "etc"]
    ter_pct: float = Field(ge=0, le=3)
    aum_eur_m: float = Field(ge=0)
    income: Literal["accumulating", "distributing"]
    replication: Literal["physical", "synthetic"]
    domicile: str = Field(min_length=2, max_length=2)
    inception_year: int = Field(ge=1990, le=2100)
    eu_retail: bool
    source: str
    tracking_diff_pct: float | None = None
    withholding_advantage_pct: float = 0.0
    note: str | None = None


class Catalog(BaseModel):
    version: int
    verified_on: date
    categories: dict[str, str]
    products: list[Product]

    @model_validator(mode="after")
    def _consistent(self) -> Catalog:
        isins = [p.isin for p in self.products]
        if len(isins) != len(set(isins)):
            raise ValueError("duplicate ISIN in catalog")
        unknown = {p.category for p in self.products} - set(self.categories)
        if unknown:
            raise ValueError(f"unknown categories: {sorted(unknown)}")
        return self

    def in_category(self, category: str) -> list[Product]:
        return [p for p in self.products if p.category == category]


def load_catalog(path: Path) -> Catalog:
    return Catalog.model_validate(yaml.safe_load(Path(path).read_text(encoding="utf-8")))
