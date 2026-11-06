"""Runtime settings, loaded from environment variables (prefix ``DTH_``) or ``.env``."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

import yaml
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

REPO_ROOT = Path(__file__).resolve().parents[4]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="DTH_", env_file=".env", extra="ignore")

    data_dir: Path = REPO_ROOT / "data"
    config_dir: Path = REPO_ROOT / "config"
    universe_file: str = "universe.example.yaml"
    auto_refresh: bool = True  # download fresh prices at startup (off in tests)
    api_token: str | None = None  # set by the desktop shell; required on every call but /health

    fred_api_key: str | None = None
    telegram_bot_token: str | None = None
    telegram_chat_id: str | None = None


class Instrument(BaseModel):
    symbol: str
    name: str
    asset_class: str
    currency: str = "EUR"
    proxy: str | None = Field(
        default=None, description="Longer-history instrument used for backtests only"
    )
    tax_category: str | None = Field(
        default=None, description="Key of config/tax.it.example.yaml categories (ADR 0008)"
    )


class Universe(BaseModel):
    name: str
    instruments: list[Instrument]

    @property
    def symbols(self) -> list[str]:
        return [i.symbol for i in self.instruments]


@lru_cache
def get_settings() -> Settings:
    return Settings()


def load_universe(path: Path | None = None) -> Universe:
    settings = get_settings()
    path = path or settings.config_dir / settings.universe_file
    with path.open(encoding="utf-8") as fh:
        return Universe.model_validate(yaml.safe_load(fh))
