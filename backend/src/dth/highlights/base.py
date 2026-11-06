"""Highlight rules (ADR 0004): the only way anything in the UI gets coloured."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Literal, Protocol, runtime_checkable

import pandas as pd

Level = Literal["attention", "critical"]


@dataclass(frozen=True)
class Context:
    """Data available to rules. Everything must be known at ``as_of``."""

    prices: pd.DataFrame  # wide close panel (EUR), columns = symbols
    as_of: pd.Timestamp
    extras: dict[str, Any] = field(default_factory=dict)  # e.g. data status, example equity


@dataclass(frozen=True)
class Highlight:
    rule_id: str
    level: Level
    title: str  # short, plain Italian, shown on the coloured element
    explanation: str  # answer to "Perché?" — what fired and on which data
    as_of: str
    data: dict[str, Any] = field(default_factory=dict)
    expires: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@runtime_checkable
class HighlightRule(Protocol):
    id: str

    def evaluate(self, ctx: Context) -> Highlight | None: ...
