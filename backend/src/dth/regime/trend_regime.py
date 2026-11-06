"""Trend regime indicator (pre-registered in docs/research/2026-11-06-preregistration-...).

An instrument is "in trend" when its close is above the 200-day average AND its averaged
3/6/12-month momentum is positive. The market regime is:
- POSITIVE   world equity in trend and >= 50% of risky instruments in trend;
- DEFENSIVE  world equity not in trend and < 50% of risky instruments in trend;
- MIXED      anything else.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass, field

import numpy as np
import pandas as pd

from dth.highlights.base import Context, Highlight

POSITIVE, MIXED, DEFENSIVE, UNKNOWN = "positivo", "misto", "difensivo", "n/d"
LOOKBACKS = (63, 126, 252)
SMA_WINDOW = 200
WORLD_CANDIDATES = ("SWDA.MI", "CSSPX.MI")


def asset_in_trend(
    prices: pd.DataFrame, lookbacks: Sequence[int] = LOOKBACKS, sma_window: int = SMA_WINDOW
) -> pd.DataFrame:
    """True/False per instrument and day; NaN where history is insufficient."""
    mom = sum(prices / prices.shift(lb) - 1.0 for lb in lookbacks) / len(lookbacks)
    sma = prices.rolling(sma_window, min_periods=sma_window).mean()
    known = mom.notna() & sma.notna()
    return ((mom > 0) & (prices > sma)).where(known)


def _world_trend(trend: pd.DataFrame, candidates: Sequence[str]) -> pd.Series:
    out = pd.Series(np.nan, index=trend.index, dtype=object)
    for sym in candidates:
        if sym in trend:
            out = out.where(out.notna(), trend[sym])
    return out


def regime_series(
    prices: pd.DataFrame,
    cash_symbol: str | None = "XEON.MI",
    world_candidates: Sequence[str] = WORLD_CANDIDATES,
) -> pd.Series:
    risky = prices.drop(columns=[c for c in [cash_symbol] if c in prices])
    trend = asset_in_trend(risky)
    world = _world_trend(trend, world_candidates)
    share = trend.sum(axis=1, min_count=1) / trend.notna().sum(axis=1).replace(0, np.nan)

    regime = pd.Series(UNKNOWN, index=prices.index)
    known = world.notna() & share.notna()
    w = world.astype("boolean").fillna(False)
    regime[known & w & (share >= 0.5)] = POSITIVE
    regime[known & ~w & (share < 0.5)] = DEFENSIVE
    regime[known & (regime == UNKNOWN)] = MIXED
    return regime


def evaluate_regime(
    regime: pd.Series, equity: pd.Series, horizon: int = 21, dd_horizon: int = 63
) -> dict[str, dict[str, float]]:
    """Forward statistics of ``equity`` (e.g. a 60/40) by regime state, starting next day."""
    eq = equity.reindex(regime.index).ffill()
    start = eq.shift(-1)
    fwd = eq.shift(-(horizon + 1)) / start - 1
    fut_min = eq[::-1].rolling(dd_horizon, min_periods=dd_horizon).min()[::-1].shift(-1)
    dd_event = (fut_min / start - 1) <= -0.10
    valid = fwd.notna() & fut_min.notna() & (regime != UNKNOWN)
    out = {}
    for state in (POSITIVE, MIXED, DEFENSIVE):
        mask = valid & (regime == state)
        n = int(mask.sum())
        out[state] = {
            "share_of_time": float(mask.sum() / valid.sum()) if valid.sum() else 0.0,
            "days": n,
            "avg_fwd_21d_return": float(fwd[mask].mean()) if n else float("nan"),
            "prob_drawdown_10pct_63d": float(dd_event[mask].mean()) if n else float("nan"),
        }
    return out


@dataclass
class TrendRegimeRule:
    """Highlight rule: MIXED → attention, DEFENSIVE → critical, POSITIVE → nothing.

    ``colors_dashboard`` is False by default: the pre-registered test of 2026-11-06 found that
    the DEFENSIVE state doubles the odds of a 10% drop but does not lower average forward
    returns, so it is information only (docs/research/2026-11-06-core-satellite-results.md).
    """

    cash_symbol: str | None = "XEON.MI"
    world_candidates: Sequence[str] = field(default=WORLD_CANDIDATES)
    colors_dashboard: bool = False
    id: str = "trend_regime"

    def evaluate(self, ctx: Context) -> Highlight | None:
        return self.explain(ctx) if self.colors_dashboard else None

    def explain(self, ctx: Context) -> Highlight | None:
        """The highlight the rule would raise, for informational display."""
        prices = ctx.prices.loc[: ctx.as_of]
        regime = regime_series(prices, self.cash_symbol, self.world_candidates)
        state = regime.iloc[-1]
        if state in (POSITIVE, UNKNOWN):
            return None
        risky = prices.drop(columns=[c for c in [self.cash_symbol] if c in prices])
        last = asset_in_trend(risky).iloc[-1]
        in_trend = sorted(s for s, v in last.items() if v is True or v == 1.0)
        out_trend = sorted(s for s, v in last.items() if v is False or v == 0.0)
        level = "critical" if state == DEFENSIVE else "attention"
        title = "Mercato in fase difensiva" if state == DEFENSIVE else "Mercato senza una direzione"
        explanation = (
            f"Regime {state}: {len(in_trend)} strumenti su {len(in_trend) + len(out_trend)} "
            "sono in trend (prezzo sopra la media a 200 giorni e momentum 3/6/12 mesi "
            "positivo). Le azioni mondo "
            f"{'non ' if state == DEFENSIVE else ''}sono in trend."
            if state == DEFENSIVE
            else f"Regime {state}: {len(in_trend)} strumenti su "
            f"{len(in_trend) + len(out_trend)} sono in trend; azioni mondo e resto del mercato "
            "non sono d'accordo."
        )
        return Highlight(
            rule_id=self.id,
            level=level,
            title=title,
            explanation=explanation,
            as_of=str(pd.Timestamp(regime.index[-1]).date()),
            data={"regime": state, "in_trend": in_trend, "not_in_trend": out_trend},
        )
