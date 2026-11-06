"""Multi-asset trend strategy for the UCITS universe (written from scratch, M2).

At each decision date:
1. score every risky asset by its average total return over several lookbacks (momentum);
2. keep only assets with positive score AND close above their long moving average (trend);
3. hold the top K of those, weighted by inverse volatility, each capped at ``max_weight``;
4. park whatever is left in the cash instrument (or leave it uninvested if there is none).

Everything uses data up to the decision close only; the harness applies the execution lag.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class MultiAssetTrend:
    lookbacks: tuple[int, ...] = (63, 126, 252)
    sma_window: int = 200
    top_k: int = 4
    vol_window: int = 63
    max_weight: float = 0.25
    cash_symbol: str | None = "XEON.MI"
    weighting: str = "inverse_vol"  # or "equal"
    # Hysteresis: an asset already held stays while it is still eligible and ranked within
    # top_k + hold_buffer. Fewer round trips → lower costs and fewer taxable sales.
    hold_buffer: int = 0
    name: str = "multi_asset_trend"

    def _with_buffer(self, rank: pd.DataFrame) -> pd.DataFrame:
        r = rank.to_numpy()
        out = np.zeros(r.shape, dtype=bool)
        held = np.zeros(r.shape[1], dtype=bool)
        for t in range(r.shape[0]):
            row = r[t]
            ok = ~np.isnan(row)
            keep = held & ok & (row <= self.top_k + self.hold_buffer)
            slots = self.top_k - int(keep.sum())
            candidates = np.flatnonzero(ok & ~keep)
            new = candidates[np.argsort(row[candidates])][: max(slots, 0)]
            held = keep.copy()
            held[new] = True
            out[t] = held
        return pd.DataFrame(out, index=rank.index, columns=rank.columns)

    def compute(self, prices: pd.DataFrame) -> pd.DataFrame:
        if self.top_k < 1 or not self.lookbacks:
            raise ValueError("top_k >= 1 and at least one lookback required")
        risky = [c for c in prices.columns if c != self.cash_symbol]
        px = prices[risky]

        mom = sum(px / px.shift(lb) - 1.0 for lb in self.lookbacks) / len(self.lookbacks)
        sma = px.rolling(self.sma_window, min_periods=self.sma_window).mean()
        eligible = (mom > 0) & (px > sma)
        rank = mom.where(eligible).rank(axis=1, ascending=False, method="first")
        chosen = rank <= self.top_k
        if self.hold_buffer > 0:
            chosen = self._with_buffer(rank)

        if self.weighting == "equal":
            w = chosen.astype(float) / self.top_k
        elif self.weighting == "inverse_vol":
            vol = (
                px.pct_change(fill_method=None)
                .rolling(self.vol_window, min_periods=self.vol_window)
                .std()
            )
            inv_vol = (1.0 / vol).where(chosen & (vol > 0))
            w = inv_vol.div(inv_vol.sum(axis=1), axis=0)
        else:
            raise ValueError(f"unknown weighting {self.weighting!r}")
        w = w.clip(upper=self.max_weight).fillna(0.0)

        out = pd.DataFrame(0.0, index=prices.index, columns=prices.columns)
        out[risky] = w
        if self.cash_symbol in prices.columns:
            out[self.cash_symbol] = (1.0 - w.sum(axis=1)).clip(lower=0.0)
        return out

    def params(self) -> dict[str, Any]:
        d = asdict(self)
        d["lookbacks"] = list(self.lookbacks)
        return d
