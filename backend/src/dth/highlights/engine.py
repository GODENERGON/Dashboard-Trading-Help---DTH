"""Evaluate highlight rules and sort them: critical first (ADR 0004)."""

from __future__ import annotations

import logging
from collections.abc import Iterable

from dth.highlights.base import Context, Highlight, HighlightRule

log = logging.getLogger(__name__)
MAX_ACTIVE = 5


def evaluate_rules(rules: Iterable[HighlightRule], ctx: Context) -> list[Highlight]:
    out: list[Highlight] = []
    for rule in rules:
        try:
            h = rule.evaluate(ctx)
        except Exception:  # a broken rule must never break the dashboard
            log.exception("highlight rule %s failed", getattr(rule, "id", rule))
            continue
        if h is not None:
            out.append(h)
    out.sort(key=lambda h: 0 if h.level == "critical" else 1)
    return out[:MAX_ACTIVE]
