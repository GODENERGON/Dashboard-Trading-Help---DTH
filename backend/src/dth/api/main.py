"""FastAPI app. Read-only in phase 1 (no order endpoints — see RISK_POLICY.md)."""

from __future__ import annotations

from functools import lru_cache
from typing import Any

from fastapi import FastAPI

from dth import __version__
from dth.backtest import BacktestConfig, walk_forward
from dth.core.config import load_universe
from dth.risk import DEFAULT_LIMITS
from dth.signals import DualMomentumTopK
from dth.testing import synthetic_prices

app = FastAPI(title="DTH — Dashboard Trading Help", version=__version__)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "version": __version__}


@app.get("/universe")
def universe() -> dict[str, Any]:
    return load_universe().model_dump()


@app.get("/risk/limits")
def risk_limits() -> dict[str, float]:
    return DEFAULT_LIMITS.__dict__


@lru_cache(maxsize=1)
def _demo_report() -> dict[str, Any]:
    prices = synthetic_prices()
    grid = [{"lookback": lb, "top_k": k} for lb in (126, 189, 252) for k in (1, 2)]
    report = walk_forward(
        DualMomentumTopK,
        prices,
        grid=grid,
        config=BacktestConfig(cash_rate=0.02),
        benchmark="EQ_WORLD",
    )
    return report.to_dict()


@app.get("/validation/demo")
def validation_demo() -> dict[str, Any]:
    """Walk-forward report on synthetic data — shape reference for the frontend."""
    return _demo_report()
