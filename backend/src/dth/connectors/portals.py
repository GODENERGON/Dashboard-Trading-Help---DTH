"""Read-only portal connectors (ADR 0005, ADR 0008).

``PortalConnector`` exposes balances only: there is deliberately no method to place, cancel or
modify orders, nor to withdraw. Crypto exchanges go through ccxt
(github.com/ccxt/ccxt, MIT); requires the ``[portals]`` extra, imported lazily.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol, runtime_checkable

# Exchanges named by the owner (ADR 0008) plus MiCA-authorised alternatives.
SUPPORTED_EXCHANGES = ("coinbase", "binance", "bitfinex", "kraken", "bitpanda")
FORBIDDEN_METHODS = ("create_order", "cancel_order", "edit_order", "withdraw", "transfer")


@dataclass(frozen=True)
class Balance:
    platform: str
    asset: str
    amount: float


@runtime_checkable
class PortalConnector(Protocol):
    name: str

    def balances(self) -> list[Balance]: ...


class CcxtConnector:
    """Wraps a ccxt exchange and exposes only ``balances``.

    The ccxt client is held privately; trading and withdrawal methods are never called and the
    wrapper refuses attribute access to them, so a bug elsewhere cannot reach them through it.
    """

    def __init__(self, exchange_id: str, api_key: str, secret: str, client: Any = None) -> None:
        if exchange_id not in SUPPORTED_EXCHANGES:
            raise ValueError(f"unsupported exchange {exchange_id!r}")
        self.name = exchange_id
        if client is None:  # pragma: no cover - needs ccxt and network
            import ccxt  # lazy: optional dependency

            client = getattr(ccxt, exchange_id)({"apiKey": api_key, "secret": secret})
        self._client = client

    def __getattr__(self, item: str) -> Any:
        if item in FORBIDDEN_METHODS:
            raise PermissionError(f"{item} is not allowed: connectors are read-only (ADR 0005)")
        raise AttributeError(item)

    def balances(self) -> list[Balance]:
        raw = self._client.fetch_balance()
        totals = raw.get("total", {}) or {}
        return [
            Balance(platform=self.name, asset=asset, amount=float(amount))
            for asset, amount in sorted(totals.items())
            if amount
        ]
