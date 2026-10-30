from __future__ import annotations

from datetime import date
from pathlib import Path

import pandas as pd

from dth.providers import DataProvider, SyntheticProvider
from dth.providers.base import normalize_ohlcv
from dth.store import ParquetStore


def test_synthetic_provider_honours_contract() -> None:
    p = SyntheticProvider()
    assert isinstance(p, DataProvider)
    df = p.fetch("EQ_WORLD", date(2010, 1, 1), date(2010, 12, 31))
    assert list(df.columns) == ["open", "high", "low", "close", "volume"]
    assert df.index.min() >= pd.Timestamp("2010-01-01")
    assert df.index.max() <= pd.Timestamp("2010-12-31")


def test_normalize_ohlcv() -> None:
    idx = pd.DatetimeIndex(
        ["2024-01-03 16:00", "2024-01-02 16:00", "2024-01-03 16:00"], tz="Europe/Rome"
    )
    raw = pd.DataFrame({"Close": [3.0, 2.0, 4.0]}, index=idx)
    out = normalize_ohlcv(raw)
    assert out.index.tz is None
    assert out["close"].tolist() == [2.0, 4.0]


def test_store_roundtrip_with_meta_and_as_of(tmp_path: Path) -> None:
    store = ParquetStore(tmp_path)
    df = SyntheticProvider().fetch("GOLD", date(2015, 1, 1), date(2015, 6, 30))
    meta = store.write("prices", "GOLD", df, source="synthetic", currency="EUR")
    assert meta.rows == len(df)
    assert meta.as_of == df.index.max().date().isoformat()
    assert store.meta("prices", "GOLD") == meta
    assert store.symbols("prices") == ["GOLD"]
    cut = store.read("prices", "GOLD", as_of="2015-03-31")
    assert cut.index.max() <= pd.Timestamp("2015-03-31")
    n = store.query("select count(*) as n from '{root}/prices/GOLD.parquet'")["n"].iloc[0]
    assert n == len(df)
