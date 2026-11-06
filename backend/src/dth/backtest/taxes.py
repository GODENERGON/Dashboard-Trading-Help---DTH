"""Italian tax model for the declarative regime (ADR 0008), driven by config/tax.it.example.yaml.

Simplifications (documented in docs/VALIDATION.md):
- taxes are settled on the last trading day of each year (in reality: the following June);
- cost basis is the weighted average cost;
- "redditi di capitale" gains (ETF) are taxed trade by trade and never offset by losses;
- all losses become "redditi diversi" credits usable for 4 years against diversi gains;
- government-bond ETFs use a blended rate: 26% x (1 - share) + 12.5% x share;
- the 48.08% reduction of losses on white-list government bonds is ignored;
- IVAFE (0.2%) applies to all holdings at year end; the fixed fee on foreign cash accounts is
  ignored.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import yaml

from dth.core.config import Universe

CAPITAL = "redditi_di_capitale"
DIVERSE = "redditi_diversi"
GOVT_RATE = 0.125


@dataclass(frozen=True)
class SymbolTax:
    gains_kind: str  # CAPITAL or DIVERSE
    rate: float


@dataclass
class TaxModel:
    symbols: dict[str, SymbolTax]
    carry_years: int = 4
    wealth_tax_rate: float = 0.002

    def for_symbol(self, symbol: str) -> SymbolTax:
        try:
            return self.symbols[symbol]
        except KeyError as exc:
            raise KeyError(f"no tax category for {symbol!r}") from exc

    @classmethod
    def from_config(
        cls,
        tax_file: Path,
        universe: Universe,
        govt_bond_share: dict[str, float] | None = None,
    ) -> TaxModel:
        cfg = yaml.safe_load(Path(tax_file).read_text(encoding="utf-8"))
        cats = cfg["categories"]
        govt_bond_share = govt_bond_share or {}
        symbols: dict[str, SymbolTax] = {}
        for inst in universe.instruments:
            cat = cats[inst.tax_category]
            share = govt_bond_share.get(inst.symbol, 0.0)
            rate = cat["rate"] * (1 - share) + GOVT_RATE * share
            symbols[inst.symbol] = SymbolTax(gains_kind=cat["gains"], rate=rate)
        return cls(
            symbols=symbols,
            carry_years=cfg["losses_carry_forward"]["years"],
            wealth_tax_rate=cfg["wealth_taxes"]["ivafe"]["rate"],
        )


@dataclass
class TaxLedger:
    """Accumulates realized results within a year and settles them at year end."""

    model: TaxModel
    loss_pool: list[list[float]] = field(default_factory=list)  # [year, amount]
    _capital_tax: float = 0.0
    _diverse_tax_base: list[tuple[float, float]] = field(default_factory=list)  # (pnl, rate)
    _new_losses: float = 0.0
    history: list[dict[str, float]] = field(default_factory=list)

    def realize(self, symbol: str, pnl: float) -> None:
        tax = self.model.for_symbol(symbol)
        if tax.gains_kind == CAPITAL:
            if pnl > 0:
                self._capital_tax += pnl * tax.rate
            else:
                self._new_losses += -pnl
        else:
            self._diverse_tax_base.append((pnl, tax.rate))

    def settle(self, year: int, holdings_value: float, wealth_tax: bool = True) -> float:
        """Close the year: offset diversi gains with the loss pool, return total tax due."""
        self.loss_pool = [e for e in self.loss_pool if e[0] >= year - self.model.carry_years]

        diverse_net = sum(a for a, _ in self._diverse_tax_base)
        gains = [(a, r) for a, r in self._diverse_tax_base if a > 0]
        avg_rate = sum(a * r for a, r in gains) / sum(a for a, _ in gains) if gains else 0.26

        diverse_tax = 0.0
        if diverse_net > 0:
            remaining = diverse_net
            for entry in sorted(self.loss_pool, key=lambda e: e[0]):
                used = min(entry[1], remaining)
                entry[1] -= used
                remaining -= used
                if remaining <= 0:
                    break
            self.loss_pool = [e for e in self.loss_pool if e[1] > 1e-9]
            diverse_tax = remaining * avg_rate
        elif diverse_net < 0:
            self._new_losses += -diverse_net

        if self._new_losses > 0:
            self.loss_pool.append([year, self._new_losses])

        wealth = holdings_value * self.model.wealth_tax_rate if wealth_tax else 0.0
        total = self._capital_tax + diverse_tax + wealth
        self.history.append(
            {
                "year": year,
                "capital_tax": self._capital_tax,
                "diverse_tax": diverse_tax,
                "wealth_tax": wealth,
                "total": total,
                "losses_carried": sum(e[1] for e in self.loss_pool),
            }
        )
        self._capital_tax = 0.0
        self._diverse_tax_base = []
        self._new_losses = 0.0
        return total
