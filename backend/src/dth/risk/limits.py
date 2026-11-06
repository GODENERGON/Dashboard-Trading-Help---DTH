"""Portfolio limits from docs/RISK_POLICY.md. Raising any default requires an ADR."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

import pandas as pd


@dataclass(frozen=True)
class RiskLimits:
    max_weight: float = 0.25
    max_gross: float = 1.0
    target_vol: float = 0.10
    dd_warning: float = -0.10
    dd_stop: float = -0.20
    max_trade_risk: float = 0.01
    max_crypto: float = 0.10  # ADR 0006
    max_startups: float = 0.15  # ADR 0006 (startups + crowdfunding, illiquid)

    def tightened(self, **overrides: float) -> RiskLimits:
        """Return a copy with stricter limits; loosening raises ValueError."""
        current = self.__dict__.copy()
        for key, new in overrides.items():
            old = current[key]
            looser = new > old if key not in ("dd_warning", "dd_stop") else new < old
            if looser:
                raise ValueError(f"{key}: {new} is looser than policy {old} (needs an ADR)")
            current[key] = new
        return RiskLimits(**current)


DEFAULT_LIMITS = RiskLimits()


class DrawdownState(StrEnum):
    NORMAL = "normal"
    WARNING = "warning"
    STOP = "stop"


def apply_limits(weights: pd.DataFrame, limits: RiskLimits = DEFAULT_LIMITS) -> pd.DataFrame:
    """Clip per-instrument weights, then scale rows whose gross exposure exceeds the cap."""
    clipped = weights.clip(lower=-limits.max_weight, upper=limits.max_weight)
    gross = clipped.abs().sum(axis=1)
    scale = (limits.max_gross / gross).where(gross > limits.max_gross, 1.0)
    return clipped.mul(scale, axis=0)


def allocation_breaches(
    values_by_class: dict[str, float], limits: RiskLimits = DEFAULT_LIMITS
) -> dict[str, float]:
    """Asset classes whose share of total monitored wealth exceeds its cap (ADR 0006).

    ``values_by_class`` maps asset class (e.g. "crypto", "startups", "etf") to market value.
    Returns {class: share} for each breach.
    """
    total = sum(values_by_class.values())
    if total <= 0:
        return {}
    caps = {"crypto": limits.max_crypto, "startups": limits.max_startups}
    shares = {k: v / total for k, v in values_by_class.items()}
    return {k: s for k, s in shares.items() if k in caps and s > caps[k] + 1e-12}


def drawdown_state(equity: pd.Series, limits: RiskLimits = DEFAULT_LIMITS) -> DrawdownState:
    dd = float(equity.iloc[-1] / equity.cummax().iloc[-1] - 1)
    if dd <= limits.dd_stop:
        return DrawdownState.STOP
    if dd <= limits.dd_warning:
        return DrawdownState.WARNING
    return DrawdownState.NORMAL
