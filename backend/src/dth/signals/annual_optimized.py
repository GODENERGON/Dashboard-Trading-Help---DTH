"""Allocation re-estimated once a year by a portfolio-construction model (e.g. skfolio).

``model_factory`` returns an object with ``fit(X)`` and ``weights_`` (the skfolio / scikit-learn
convention). At each year-end close the model is fitted on the trailing ``lookback`` daily
returns (known at that close) and the weights are held until the next year end.
"""

from __future__ import annotations

from collections.abc import Callable, Sequence
from dataclasses import dataclass, field
from typing import Any

import numpy as np
import pandas as pd

ModelFactory = Callable[[], Any]


def capped_weights(w: pd.Series, caps: dict[str, float]) -> pd.Series:
    """Clip weights at their caps and redistribute the excess pro rata to uncapped assets."""
    w = w.clip(lower=0)
    w = w / w.sum()
    for _ in range(len(w)):
        over = {k: c for k, c in caps.items() if k in w and w[k] > c + 1e-12}
        if not over:
            break
        excess = sum(w[k] - c for k, c in over.items())
        for k, c in over.items():
            w[k] = c
        free = [k for k in w.index if k not in caps or w[k] < caps[k] - 1e-12]
        free = [k for k in free if k not in over]
        if not free:
            break
        w[free] += excess * w[free] / w[free].sum()
    return w


@dataclass
class AnnualOptimized:
    model_factory: ModelFactory
    # slot name → candidate symbols (first available wins), e.g. world: (SWDA, CSSPX)
    slots: dict[str, Sequence[str]]
    caps: dict[str, float] = field(default_factory=dict)  # by slot name
    lookback: int = 756
    name: str = "annual_optimized"

    def _slot_prices(self, prices: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
        """Continuous slot return series (spliced over candidates) and the held symbol."""
        rets, held = {}, {}
        for slot, cands in self.slots.items():
            r = pd.Series(np.nan, index=prices.index)
            h = pd.Series(None, index=prices.index, dtype=object)
            for sym in reversed(list(cands)):  # first candidate has priority
                if sym not in prices:
                    continue
                sr = prices[sym].pct_change(fill_method=None)
                r = sr.where(sr.notna(), r)
                h = h.where(prices[sym].isna(), sym)
            rets[slot], held[slot] = r, h
        return pd.DataFrame(rets), pd.DataFrame(held)

    def compute(self, prices: pd.DataFrame) -> pd.DataFrame:
        rets, held = self._slot_prices(prices)
        out = pd.DataFrame(0.0, index=prices.index, columns=prices.columns)
        year_ends = prices.index.to_series().groupby(prices.index.year).max().to_numpy()
        current: pd.Series | None = None
        pos = {d: i for i, d in enumerate(prices.index)}
        last_fit = -1
        for ye in year_ends:
            i = pos[ye]
            window = rets.iloc[max(0, i - self.lookback + 1) : i + 1]
            if len(window) < self.lookback or window.isna().any().any():
                continue
            model = self.model_factory()
            model.fit(window)
            new = capped_weights(pd.Series(model.weights_, index=window.columns), self.caps)
            if current is not None:
                self._assign(out, held, current, last_fit, i)  # previous weights until today
            current, last_fit = new, i  # new weights decided at this close
        if current is not None:
            self._assign(out, held, current, last_fit, len(prices.index))
        return out

    @staticmethod
    def _assign(out, held, weights, start, end) -> None:
        block = held.iloc[start:end]
        for slot, wt in weights.items():
            for sym in block[slot].dropna().unique():
                mask = (block[slot] == sym).to_numpy()
                out.iloc[start:end, out.columns.get_loc(sym)] += np.where(mask, wt, 0.0)

    def params(self) -> dict[str, Any]:
        return {"slots": {k: list(v) for k, v in self.slots.items()}, "caps": self.caps,
                "lookback": self.lookback}  # fmt: skip
