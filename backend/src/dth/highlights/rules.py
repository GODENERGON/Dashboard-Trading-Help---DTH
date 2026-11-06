"""Built-in highlight rules used by the desktop app (ADR 0004)."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from dth.highlights.base import Context, Highlight
from dth.risk import DEFAULT_LIMITS, RiskLimits, drawdown_state


def _pct(x: float) -> str:
    return f"{x * 100:.1f}%".replace(".", ",")


@dataclass
class StaleDataRule:
    """Prices older than ``max_business_days`` → attention; repeated refresh failures → critical."""

    max_business_days: int = 3
    max_failures: int = 3
    id: str = "stale_source"

    def evaluate(self, ctx: Context) -> Highlight | None:
        status = ctx.extras.get("data_status", {})
        today = pd.Timestamp(ctx.extras.get("today", pd.Timestamp.today())).normalize()
        age = int(np.busday_count(ctx.as_of.date(), today.date()))
        failures = int(status.get("failures", 0))
        if failures >= self.max_failures:
            return Highlight(
                rule_id="broken_source",
                level="critical",
                title="Aggiornamento dei prezzi non riuscito",
                explanation=(
                    f"Gli ultimi {failures} tentativi di aggiornare i prezzi sono falliti "
                    f"({status.get('last_error') or 'errore sconosciuto'}). I dati mostrati sono "
                    f"fermi al {ctx.as_of.date():%d/%m/%Y}. Controlla la connessione a internet."
                ),
                as_of=str(ctx.as_of.date()),
                data={"tentativi_falliti": failures},
            )
        if age > self.max_business_days:
            return Highlight(
                rule_id=self.id,
                level="attention",
                title=f"Prezzi non aggiornati da {age} giorni lavorativi",
                explanation=(
                    f"L'ultimo prezzo disponibile è del {ctx.as_of.date():%d/%m/%Y}. "
                    "Dabitur li aggiorna da solo quando è aperto e connesso a internet."
                ),
                as_of=str(ctx.as_of.date()),
                data={"giorni": age},
            )
        return None


@dataclass
class ExampleDrawdownRule:
    """Drawdown of the example portfolio against the risk-policy limits."""

    limits: RiskLimits = DEFAULT_LIMITS
    id: str = "drawdown"

    def evaluate(self, ctx: Context) -> Highlight | None:
        equity: pd.Series | None = ctx.extras.get("example_equity")
        if equity is None or equity.empty:
            return None
        state = drawdown_state(equity, self.limits)
        if state.value == "normal":
            return None
        dd = float(equity.iloc[-1] / equity.cummax().iloc[-1] - 1)
        critical = state.value == "stop"
        limit = self.limits.dd_stop if critical else self.limits.dd_warning
        return Highlight(
            rule_id="drawdown_stop" if critical else "drawdown_warning",
            level="critical" if critical else "attention",
            title=f"Portafoglio di esempio a {_pct(dd)} dal massimo",
            explanation=(
                f"Il drawdown ({_pct(dd)}) ha superato il limite di {_pct(limit)} della policy "
                "di rischio. "
                + (
                    "La policy prevede di dimezzare l'esposizione e rivedere il portafoglio a mano."
                    if critical
                    else "È un segnale per ricontrollare il piano, non per vendere d'istinto."
                )
            ),
            as_of=str(ctx.as_of.date()),
            data={"drawdown": dd, "limit": limit, "peak": str(equity.idxmax().date())},
        )
