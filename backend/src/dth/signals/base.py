"""Signal contract.

A Signal maps a wide close-price frame (columns = symbols) to target weights computed using
ONLY information available at each row's close. The backtest harness — not the signal —
shifts weights by one bar for execution. Every signal must pass ``tests/test_no_lookahead.py``.
"""

from __future__ import annotations

from typing import Any, Protocol, runtime_checkable

import pandas as pd


@runtime_checkable
class Signal(Protocol):
    name: str

    def compute(self, prices: pd.DataFrame) -> pd.DataFrame:
        """Return target weights in [-1, 1], aligned to ``prices``, with no NaN."""
        ...

    def params(self) -> dict[str, Any]:
        """Parameters that define this signal instance (stored in validation reports)."""
        ...
