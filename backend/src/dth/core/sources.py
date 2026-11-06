"""Source registry schema (CLAUDE.md rule 10: every source goes through the registry)."""

from __future__ import annotations

from enum import StrEnum
from pathlib import Path

import yaml
from pydantic import BaseModel, HttpUrl, field_validator, model_validator


class SourceKind(StrEnum):
    DATA = "data"
    NEWS = "news"
    PORTAL = "portal"
    LLM = "llm"


class Access(StrEnum):
    API = "api"
    CSV = "csv"
    RSS = "rss"
    WEB = "web"
    MANUAL = "manual"


class Cost(StrEnum):
    FREE = "free"
    FREEMIUM = "freemium"
    PAID = "paid"
    ACCOUNT = "account"


class Auth(StrEnum):
    NONE = "none"
    KEY = "key"
    OAUTH = "oauth"
    ACCOUNT = "account"


class Status(StrEnum):
    ACTIVE = "active"
    PLANNED = "planned"
    DISABLED = "disabled"


CATEGORIES = frozenset(
    {
        "prices", "macro", "rates", "volatility", "positioning", "sentiment", "events",
        "news", "real_estate", "etf", "indices", "crypto", "commodities", "startups", "ipo",
        "filings", "portfolio", "llm",
    }
)  # fmt: skip


class Source(BaseModel):
    id: str
    name: str
    kind: SourceKind
    categories: list[str]
    url: HttpUrl
    access: Access
    cost: Cost
    auth: Auth
    reliability: str
    status: Status
    notes: str | None = None
    warning: str | None = None  # shown to the user, e.g. missing MiCA authorisation

    @field_validator("categories")
    @classmethod
    def _known_categories(cls, v: list[str]) -> list[str]:
        unknown = set(v) - CATEGORIES
        if not v or unknown:
            raise ValueError(f"unknown or empty categories: {sorted(unknown)}")
        return v

    @field_validator("reliability")
    @classmethod
    def _reliability(cls, v: str) -> str:
        if v not in {"A", "B", "C"}:
            raise ValueError("reliability must be A, B or C")
        return v


class SourceRegistry(BaseModel):
    version: int
    sources: list[Source]

    @model_validator(mode="after")
    def _unique_ids(self) -> SourceRegistry:
        ids = [s.id for s in self.sources]
        dupes = {i for i in ids if ids.count(i) > 1}
        if dupes:
            raise ValueError(f"duplicate source ids: {sorted(dupes)}")
        return self

    def by_category(self, category: str, *, include_inactive: bool = False) -> list[Source]:
        return [
            s
            for s in self.sources
            if category in s.categories and (include_inactive or s.status is Status.ACTIVE)
        ]

    def get(self, source_id: str) -> Source:
        for s in self.sources:
            if s.id == source_id:
                return s
        raise KeyError(source_id)


def load_registry(path: Path) -> SourceRegistry:
    with Path(path).open(encoding="utf-8") as fh:
        return SourceRegistry.model_validate(yaml.safe_load(fh))
