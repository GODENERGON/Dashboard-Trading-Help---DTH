"""Anti-lookahead harness.

Perturb every price AFTER a cut date and recompute the signal: weights up to and including
the cut date must be identical. If they change, the signal uses future information.

Register every new Signal in SIGNALS_UNDER_TEST (CLAUDE.md rule 1).
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
import pytest

from dth.signals import DualMomentumTopK, MultiAssetTrend, TrendFilter
from dth.signals.base import Signal
from dth.testing import synthetic_prices

SIGNALS_UNDER_TEST: list[Signal] = [
    TrendFilter(window=200),
    TrendFilter(window=50),
    DualMomentumTopK(lookback=252, top_k=2, skip=21),
    DualMomentumTopK(lookback=126, top_k=1, skip=0),
    MultiAssetTrend(cash_symbol="BOND_GOV"),
    MultiAssetTrend(lookbacks=(21, 63), sma_window=100, top_k=2, cash_symbol=None),
    MultiAssetTrend(top_k=2, hold_buffer=1, weighting="equal", cash_symbol="BOND_GOV"),
]


def assert_no_lookahead(signal: Signal, prices: pd.DataFrame, n_cuts: int = 5) -> None:
    rng = np.random.default_rng(0)
    base = signal.compute(prices)
    cut_positions = np.linspace(300, len(prices) - 50, n_cuts).astype(int)
    for pos in cut_positions:
        cut = prices.index[pos]
        future = prices.index > cut
        noise = np.exp(rng.normal(0, 0.05, size=(int(future.sum()), prices.shape[1])))
        perturbed = prices.copy()
        perturbed.loc[future] = perturbed.loc[future].to_numpy() * noise
        recomputed = signal.compute(perturbed)
        pd.testing.assert_frame_equal(
            base.loc[:cut], recomputed.loc[:cut], obj=f"{signal.name} weights up to {cut.date()}"
        )


@pytest.fixture(scope="module")
def prices() -> pd.DataFrame:
    return synthetic_prices(periods=252 * 6)


@pytest.mark.parametrize("signal", SIGNALS_UNDER_TEST, ids=lambda s: repr(s))
def test_signal_has_no_lookahead(signal: Signal, prices: pd.DataFrame) -> None:
    assert_no_lookahead(signal, prices)


@dataclass(frozen=True)
class _LeakySignal:
    """Deliberately cheats by peeking at tomorrow's return."""

    name: str = "leaky"

    def compute(self, prices: pd.DataFrame) -> pd.DataFrame:
        tomorrow = prices.pct_change().shift(-1)
        return (tomorrow > 0).astype(float) / prices.shape[1]

    def params(self) -> dict:
        return {}


def test_harness_catches_a_leaky_signal(prices: pd.DataFrame) -> None:
    with pytest.raises(AssertionError):
        assert_no_lookahead(_LeakySignal(), prices)
