"""Deterministic synthetic data for tests and examples (no network)."""

from __future__ import annotations

import numpy as np
import pandas as pd


def synthetic_prices(
    symbols: tuple[str, ...] = ("EQ_WORLD", "EQ_EM", "BOND_GOV", "GOLD"),
    start: str = "2005-01-03",
    periods: int = 252 * 20,
    seed: int = 42,
) -> pd.DataFrame:
    """Business-day close prices from a two-regime (calm / stress) random walk.

    Each asset has its own drift and volatility; a shared regime process raises volatility
    and lowers drift during stress so that trend and risk logic have something to react to.
    """
    rng = np.random.default_rng(seed)
    index = pd.bdate_range(start=start, periods=periods)

    # Shared regime: persistent Markov chain, ~10% of the time in stress.
    stress = np.zeros(periods, dtype=bool)
    for t in range(1, periods):
        p_stay = 0.985 if stress[t - 1] else 0.998
        stress[t] = stress[t - 1] if rng.random() < p_stay else not stress[t - 1]

    params = {
        "EQ_WORLD": (0.07, 0.15, 1.0),
        "EQ_EM": (0.06, 0.20, 1.2),
        "BOND_GOV": (0.025, 0.06, -0.3),
        "GOLD": (0.04, 0.15, -0.1),
    }
    market = rng.standard_normal(periods)
    data = {}
    for i, sym in enumerate(symbols):
        mu, sigma, beta = params.get(sym, (0.05, 0.15, 0.5 + 0.1 * i))
        idio = rng.standard_normal(periods)
        vol = np.where(stress, sigma * 2.2, sigma) / np.sqrt(252)
        drift = np.where(stress, -0.25 * abs(beta), mu) / 252
        shocks = beta * market * 0.6 + idio * np.sqrt(max(1 - 0.36 * beta**2, 0.2))
        rets = drift + vol * shocks
        data[sym] = 100 * np.exp(np.cumsum(rets))
    return pd.DataFrame(data, index=index)
