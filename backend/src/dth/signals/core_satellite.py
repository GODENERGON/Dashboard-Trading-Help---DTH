"""Core-satellite: a static core (rarely traded, tax-efficient) plus a trend satellite."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import pandas as pd

from dth.signals.multi_asset import MultiAssetTrend


@dataclass(frozen=True)
class CoreSatellite:
    """``core`` maps a slot to an ordered list of candidate symbols (first available wins)
    and the slot weight inside the core. The satellite gets ``satellite_share`` of the total.
    """

    core: tuple[tuple[tuple[str, ...], float], ...] = (
        (("SWDA.MI", "CSSPX.MI"), 0.6),
        (("IBGL.MI",), 0.4),
    )
    satellite: MultiAssetTrend = field(default_factory=MultiAssetTrend)
    satellite_share: float = 0.30
    name: str = "core_satellite"

    def _core_weights(self, prices: pd.DataFrame) -> pd.DataFrame:
        w = pd.DataFrame(0.0, index=prices.index, columns=prices.columns)
        for candidates, slot_weight in self.core:
            assigned = pd.Series(False, index=prices.index)
            for sym in candidates:
                if sym not in prices:
                    continue
                use = prices[sym].notna() & ~assigned
                w.loc[use, sym] += slot_weight
                assigned |= use
        total = w.sum(axis=1)
        return w.div(total.where(total > 0), axis=0).fillna(0.0)

    def compute(self, prices: pd.DataFrame) -> pd.DataFrame:
        if not 0 <= self.satellite_share <= 1:
            raise ValueError("satellite_share must be within [0, 1]")
        core = self._core_weights(prices)
        sat = self.satellite.compute(prices)
        return core * (1 - self.satellite_share) + sat * self.satellite_share

    def params(self) -> dict[str, Any]:
        return {
            "core": [{"candidates": list(c), "weight": w} for c, w in self.core],
            "satellite": self.satellite.params(),
            "satellite_share": self.satellite_share,
        }
