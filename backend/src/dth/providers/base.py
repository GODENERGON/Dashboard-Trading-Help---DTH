"""DataProvider contract. Providers fetch; they never persist (that is the store's job)."""

from __future__ import annotations

from datetime import date
from typing import Protocol, runtime_checkable

import pandas as pd


@runtime_checkable
class DataProvider(Protocol):
    """Fetches one symbol's history.

    Returns a DataFrame indexed by tz-naive close dates, sorted ascending, with canonical
    lower-case columns: ``open, high, low, close, volume`` for prices or ``value`` for
    macro series. Prices are split- and dividend-adjusted unless stated otherwise.
    """

    name: str

    def fetch(self, symbol: str, start: date, end: date) -> pd.DataFrame: ...


def normalize_ohlcv(df: pd.DataFrame) -> pd.DataFrame:
    """Lower-case columns, tz-naive sorted unique index, drop all-NaN rows."""
    out = df.copy()
    out.columns = [str(c).lower().replace(" ", "_") for c in out.columns]
    out.index = pd.DatetimeIndex(out.index)
    if out.index.tz is not None:
        out.index = out.index.tz_localize(None)
    out.index = out.index.normalize()
    out = out[~out.index.duplicated(keep="last")].sort_index()
    return out.dropna(how="all")
