"""Yahoo Finance provider (research grade). Requires the ``[data]`` extra.

Unofficial API: use as a primary source for research only, and cross-check with a second
provider (e.g. Stooq) before trusting it for live decisions.
"""

from __future__ import annotations

from datetime import date, timedelta

import pandas as pd

from dth.providers.base import normalize_ohlcv


class YFinanceProvider:
    name = "yfinance"

    def fetch(self, symbol: str, start: date, end: date) -> pd.DataFrame:
        import yfinance as yf  # lazy: optional dependency

        raw = yf.download(
            symbol,
            start=start.isoformat(),
            end=(end + timedelta(days=1)).isoformat(),  # yfinance end is exclusive
            auto_adjust=True,
            progress=False,
            multi_level_index=False,
        )
        if raw is None or raw.empty:
            raise LookupError(f"yfinance returned no data for {symbol!r}")
        return normalize_ohlcv(raw)[["open", "high", "low", "close", "volume"]]
