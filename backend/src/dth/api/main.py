"""FastAPI app. Read-only in phase 1 (no order endpoints — see RISK_POLICY.md)."""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from functools import lru_cache
from typing import Any

import pandas as pd
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from dth import __version__
from dth.app.data_service import DataService
from dth.app.overview import build_overview
from dth.backtest import BacktestConfig, walk_forward
from dth.core.config import REPO_ROOT, get_settings, load_universe
from dth.highlights import Context
from dth.products import build_model_portfolios, load_catalog, rank_catalog
from dth.regime import TrendRegimeRule, regime_series
from dth.risk import DEFAULT_LIMITS
from dth.signals import DualMomentumTopK
from dth.store import ParquetStore
from dth.testing import synthetic_prices

PRICES_DATASET = "prices_eur"

APP_NAME = "Dabitur"


@lru_cache
def data_service() -> DataService:
    return DataService()


@asynccontextmanager
async def _lifespan(_: FastAPI) -> AsyncIterator[None]:
    svc = data_service()
    if get_settings().auto_refresh and svc.needs_refresh():
        svc.refresh_in_background()
    yield


app = FastAPI(title=APP_NAME, version=__version__, lifespan=_lifespan)

# Origins of the Tauri webview (Windows uses http://tauri.localhost) and of `npm run dev`.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["tauri://localhost", "http://tauri.localhost", "http://localhost:5173"],
    allow_methods=["GET", "POST"],
    allow_headers=["X-Dabitur-Token", "Content-Type"],
)
TOKEN_HEADER = "X-Dabitur-Token"
OPEN_PATHS = {"/health"}


@app.middleware("http")
async def _require_token(request: Request, call_next):  # type: ignore[no-untyped-def]
    """Only the desktop shell that started the sidecar knows the token (other local apps don't)."""
    token = get_settings().api_token
    if (
        token
        and request.method != "OPTIONS"
        and request.url.path not in OPEN_PATHS
        and request.headers.get(TOKEN_HEADER) != token
    ):
        return JSONResponse({"detail": "token mancante o errato"}, status_code=401)
    return await call_next(request)


class Feedback(BaseModel):
    message: str = Field(min_length=1, max_length=5000)
    view: str | None = Field(default=None, max_length=50)
    rating: int | None = Field(default=None, ge=1, le=5)


@app.post("/feedback")
def feedback(item: Feedback) -> dict[str, Any]:
    """Store feedback locally (the tester can also send it by e-mail from the UI)."""
    import json
    from datetime import UTC, datetime

    path = get_settings().data_dir / "feedback" / "feedback.jsonl"
    path.parent.mkdir(parents=True, exist_ok=True)
    record = {"at": datetime.now(UTC).isoformat(), "version": __version__, **item.model_dump()}
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(record, ensure_ascii=False) + "\n")
    return {"saved": True, "path": str(path)}


@app.get("/status")
def status() -> dict[str, Any]:
    """Where the prices come from and how fresh they are."""
    return data_service().status()


@app.post("/refresh")
def refresh() -> dict[str, Any]:
    """Start a background price refresh (idempotent while one is running)."""
    svc = data_service()
    if not svc.refreshing:
        svc.refresh_in_background()
    return {"started": True}


@app.get("/overview")
def overview() -> dict[str, Any]:
    """Panoramica: regime band, example risk, active highlights, data status."""
    svc = data_service()
    return build_overview(svc.panel(), svc.status())


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "app": APP_NAME, "version": __version__}


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


def _store() -> ParquetStore:
    return ParquetStore(get_settings().data_dir / "lake")


def _close_panel(store: ParquetStore, symbols: list[str]) -> pd.DataFrame:
    cols = {}
    for sym in symbols:
        if sym in store.symbols(PRICES_DATASET):
            cols[sym] = store.read(PRICES_DATASET, sym)["close"]
    return pd.DataFrame(cols).sort_index()


@app.get("/regime/trend")
def trend_regime() -> dict[str, Any]:
    """Current trend regime and the highlight it produces (ADR 0004)."""
    panel = _close_panel(_store(), load_universe().symbols)
    if panel.empty or len(panel) < 260:
        raise HTTPException(
            status_code=503,
            detail="Dati di prezzo non ancora disponibili: avvia l'aggiornamento delle fonti.",
        )
    regime = regime_series(panel)
    rule = TrendRegimeRule()
    ctx = Context(prices=panel, as_of=panel.index[-1])
    highlight = rule.evaluate(ctx)
    detail = rule.explain(ctx)
    history = regime.iloc[-260:]
    return {
        "as_of": str(panel.index[-1].date()),
        "regime": regime.iloc[-1],
        "colors_dashboard": rule.colors_dashboard,
        "highlight": highlight.to_dict() if highlight else None,
        "detail": detail.to_dict() if detail else None,
        "history": {str(d.date()): v for d, v in history.items()},
    }


def _ranking() -> dict[str, Any]:
    settings = get_settings()
    path = settings.config_dir / "products.example.yaml"
    if not path.exists():
        path = REPO_ROOT / "config" / "products.example.yaml"
    return rank_catalog(load_catalog(path))


@app.get("/products")
def products(category: str | None = None) -> dict[str, Any]:
    """Products ranked by objective features: featured first, then all the others (ADR 0009)."""
    ranking = _ranking()
    if category is not None:
        if category not in ranking["categories"]:
            raise HTTPException(status_code=404, detail=f"Categoria sconosciuta: {category}")
        ranking["categories"] = {category: ranking["categories"][category]}
    return ranking


@app.get("/portfolios/models")
def model_portfolios() -> dict[str, Any]:
    """Educational, non-personalised model portfolios built from the ranking (ADR 0009)."""
    return build_model_portfolios(_ranking())
