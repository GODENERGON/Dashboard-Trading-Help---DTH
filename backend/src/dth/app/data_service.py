"""Price panel for the desktop app: bundled seed → refreshed from the internet in background."""

from __future__ import annotations

import json
import logging
import threading
from datetime import UTC, date, datetime, timedelta
from pathlib import Path
from typing import Any

import pandas as pd

from dth.core.config import get_settings, load_universe

log = logging.getLogger(__name__)
SEED_FILE = "seed_prices_eur.csv.gz"
REFRESH_AFTER = timedelta(hours=12)
HISTORY_START = date(2004, 1, 1)


class DataService:
    def __init__(self, data_dir: Path | None = None, config_dir: Path | None = None) -> None:
        settings = get_settings()
        self.data_dir = Path(data_dir or settings.data_dir)
        self.config_dir = Path(config_dir or settings.config_dir)
        self.panel_path = self.data_dir / "lake" / "panel" / "prices_eur.parquet"
        self.meta_path = self.panel_path.with_suffix(".meta.json")
        self._lock = threading.Lock()
        self.refreshing = False
        self.failures = 0
        self.last_error: str | None = None
        self._cache: tuple[float, pd.DataFrame] | None = None

    # ── reading ──────────────────────────────────────────────────────────────
    def _meta(self) -> dict[str, Any]:
        if self.meta_path.exists():
            return json.loads(self.meta_path.read_text())
        return {"source": "seme incluso nell'app", "fetched_at": None}

    def panel(self) -> pd.DataFrame:
        if self.panel_path.exists():
            mtime = self.panel_path.stat().st_mtime
            if self._cache is None or self._cache[0] != mtime:
                self._cache = (mtime, pd.read_parquet(self.panel_path))
            return self._cache[1]
        if self._cache is None:
            seed = pd.read_csv(self.config_dir / SEED_FILE, index_col=0, parse_dates=True)
            self._cache = (0.0, seed)
        return self._cache[1]

    def status(self) -> dict[str, Any]:
        meta = self._meta()
        panel = self.panel()
        return {
            "as_of": str(panel.index[-1].date()),
            "source": meta["source"],
            "fetched_at": meta["fetched_at"],
            "refreshing": self.refreshing,
            "failures": self.failures,
            "last_error": self.last_error,
        }

    def needs_refresh(self, now: datetime | None = None) -> bool:
        fetched = self._meta().get("fetched_at")
        if not fetched:
            return True
        now = now or datetime.now(UTC)
        return now - datetime.fromisoformat(fetched) > REFRESH_AFTER

    # ── refreshing ───────────────────────────────────────────────────────────
    def refresh(self, provider: Any = None) -> bool:
        from dth.research.ucits_trend import build_price_panel

        if not self._lock.acquire(blocking=False):
            return False
        self.refreshing = True
        try:
            if provider is None:
                from dth.providers.yfinance_provider import YFinanceProvider

                provider = YFinanceProvider()
            universe = load_universe(self.config_dir / get_settings().universe_file)
            panel, _ = build_price_panel(provider, universe, HISTORY_START, date.today())
            current = self.panel()
            if len(panel) < 0.9 * len(current) or panel.shape[1] < current.shape[1]:
                raise ValueError("dati scaricati incompleti, tengo quelli precedenti")
            self.panel_path.parent.mkdir(parents=True, exist_ok=True)
            tmp = self.panel_path.with_suffix(".tmp")
            panel.to_parquet(tmp)
            tmp.replace(self.panel_path)
            self.meta_path.write_text(
                json.dumps({"source": "Yahoo Finance", "fetched_at": datetime.now(UTC).isoformat()})
            )
            self.failures, self.last_error = 0, None
            return True
        except Exception as exc:  # network, provider changes, validation
            self.failures += 1
            self.last_error = str(exc)[:200]
            log.warning("price refresh failed: %s", exc)
            return False
        finally:
            self.refreshing = False
            self._lock.release()

    def refresh_in_background(self) -> None:
        threading.Thread(target=self.refresh, name="dth-refresh", daemon=True).start()
