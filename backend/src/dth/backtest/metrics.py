"""Performance metrics on daily return series."""

from __future__ import annotations

import numpy as np
import pandas as pd

TRADING_DAYS = 252


def max_drawdown(returns: pd.Series) -> float:
    equity = (1 + returns).cumprod()
    return float((equity / equity.cummax() - 1).min())


def compute_metrics(returns: pd.Series, turnover: pd.Series | None = None) -> dict[str, float]:
    r = returns.dropna()
    n = len(r)
    if n == 0:
        raise ValueError("empty return series")
    total = float((1 + r).prod())
    years = n / TRADING_DAYS
    cagr = total ** (1 / years) - 1 if total > 0 else -1.0
    vol = float(r.std(ddof=0) * np.sqrt(TRADING_DAYS))
    downside = float(r[r < 0].std(ddof=0) * np.sqrt(TRADING_DAYS)) if (r < 0).any() else 0.0
    mean_ann = float(r.mean() * TRADING_DAYS)
    mdd = max_drawdown(r)
    out = {
        "cagr": cagr,
        "volatility": vol,
        "sharpe": mean_ann / vol if vol > 0 else 0.0,
        "sortino": mean_ann / downside if downside > 0 else 0.0,
        "max_drawdown": mdd,
        "calmar": cagr / abs(mdd) if mdd < 0 else 0.0,
        "hit_rate": float((r > 0).mean()),
        "years": years,
    }
    if turnover is not None:
        out["annual_turnover"] = float(turnover.loc[r.index].sum() / years)
    return out
