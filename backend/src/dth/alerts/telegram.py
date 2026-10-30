"""Telegram notifications with a per-key cooldown (anti-spam)."""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field

import httpx

log = logging.getLogger(__name__)


@dataclass
class AlertGate:
    """Lets an alert key through at most once per ``cooldown_s`` seconds."""

    cooldown_s: float = 6 * 3600
    _last: dict[str, float] = field(default_factory=dict)

    def allow(self, key: str, now: float | None = None) -> bool:
        now = time.time() if now is None else now
        if now - self._last.get(key, float("-inf")) < self.cooldown_s:
            return False
        self._last[key] = now
        return True


class TelegramNotifier:
    def __init__(self, token: str, chat_id: str, gate: AlertGate | None = None) -> None:
        self._url = f"https://api.telegram.org/bot{token}/sendMessage"
        self._chat_id = chat_id
        self._gate = gate or AlertGate()

    def send(self, key: str, text: str) -> bool:
        if not self._gate.allow(key):
            log.debug("alert %s suppressed by cooldown", key)
            return False
        resp = httpx.post(self._url, json={"chat_id": self._chat_id, "text": text}, timeout=10)
        resp.raise_for_status()
        return True
