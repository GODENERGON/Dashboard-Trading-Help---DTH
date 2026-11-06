"""Parquet lake with metadata, queried through DuckDB.

Layout: ``<root>/<dataset>/<symbol>.parquet`` plus ``<root>/<dataset>/<symbol>.meta.json``.
"""

from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path

import pandas as pd

_SAFE = re.compile(r"[^A-Za-z0-9._-]")


@dataclass(frozen=True)
class SeriesMeta:
    source: str
    fetched_at: str
    as_of: str
    rows: int
    adjusted: bool = True
    currency: str | None = None


class ParquetStore:
    def __init__(self, root: Path) -> None:
        self.root = Path(root)

    def _path(self, dataset: str, symbol: str, suffix: str) -> Path:
        return self.root / _SAFE.sub("_", dataset) / f"{_SAFE.sub('_', symbol)}{suffix}"

    def write(
        self,
        dataset: str,
        symbol: str,
        df: pd.DataFrame,
        *,
        source: str,
        adjusted: bool = True,
        currency: str | None = None,
    ) -> SeriesMeta:
        if df.empty:
            raise ValueError("refusing to write an empty series")
        path = self._path(dataset, symbol, ".parquet")
        path.parent.mkdir(parents=True, exist_ok=True)
        df.sort_index().to_parquet(path)
        meta = SeriesMeta(
            source=source,
            fetched_at=datetime.now(UTC).isoformat(timespec="seconds"),
            as_of=pd.Timestamp(df.index.max()).date().isoformat(),
            rows=len(df),
            adjusted=adjusted,
            currency=currency,
        )
        self._path(dataset, symbol, ".meta.json").write_text(json.dumps(asdict(meta), indent=2))
        return meta

    def read(self, dataset: str, symbol: str, as_of: str | None = None) -> pd.DataFrame:
        """Read a series, optionally truncated at ``as_of`` (inclusive)."""
        df = pd.read_parquet(self._path(dataset, symbol, ".parquet"))
        if as_of is not None:
            df = df.loc[: pd.Timestamp(as_of)]
        return df

    def meta(self, dataset: str, symbol: str) -> SeriesMeta:
        raw = json.loads(self._path(dataset, symbol, ".meta.json").read_text())
        return SeriesMeta(**raw)

    def symbols(self, dataset: str) -> list[str]:
        folder = self.root / dataset
        return sorted(p.stem for p in folder.glob("*.parquet")) if folder.exists() else []

    def query(self, sql: str) -> pd.DataFrame:
        """Run DuckDB SQL; ``{root}`` in the query is replaced by the lake path."""
        import duckdb  # lazy: only SQL queries need it (not in the desktop build)

        with duckdb.connect() as con:
            return con.execute(sql.replace("{root}", self.root.as_posix())).df()
