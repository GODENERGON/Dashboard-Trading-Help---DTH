"""Pre-registered study: skfolio allocations vs the static balanced model portfolio
(docs/research/2026-11-06-preregistration-skfolio-allocation.md). Requires ``[portfolio]``.
"""

from __future__ import annotations

from typing import Any

import pandas as pd

from dth.backtest import BacktestConfig
from dth.backtest.taxes import TaxModel
from dth.research.ucits_trend import _num, _pair, _pct, _strip, _Windowed
from dth.signals import CoreSatellite, MultiAssetTrend
from dth.signals.annual_optimized import AnnualOptimized

SLOTS = {
    "world": ("SWDA.MI", "CSSPX.MI"),
    "europe": ("MEUD.MI",),
    "em": ("EIMI.MI",),
    "bonds": ("IBGL.MI",),
    "gold": ("SGLD.MI",),
    "real_estate": ("IWDP.MI",),
}
CAPS = {"world": 0.60, "europe": 0.25, "em": 0.25, "real_estate": 0.25}
LABELS = {
    "balanced_static": "Bilanciato statico 55/35/10",
    "hrp": "skfolio Hierarchical Risk Parity",
    "risk_budgeting": "skfolio Risk Budgeting",
}


def _models() -> dict[str, Any]:
    from skfolio.optimization import HierarchicalRiskParity, RiskBudgeting  # lazy

    return {"hrp": HierarchicalRiskParity, "risk_budgeting": RiskBudgeting}


def run_allocation_study(prices: pd.DataFrame, tax: TaxModel, cost_bps: float = 10.0) -> dict:
    cfg = BacktestConfig(rebalance="YE", cost_bps=cost_bps)
    signals: dict[str, Any] = {
        name: AnnualOptimized(model_factory=factory, slots=SLOTS, caps=CAPS)
        for name, factory in _models().items()
    }
    first = min(
        s.compute(prices).pipe(lambda w: w[w.sum(axis=1) > 0]).index[0] for s in signals.values()
    )
    signals["balanced_static"] = CoreSatellite(
        core=((SLOTS["world"], 0.55), (SLOTS["bonds"], 0.35), (SLOTS["gold"], 0.10)),
        satellite=MultiAssetTrend(cash_symbol=None),
        satellite_share=0.0,
    )
    win = prices.loc[first:]
    rows = {
        k: _strip(_pair(_Windowed(s, prices, first), win, cfg, tax)) for k, s in signals.items()
    }
    for k, s in signals.items():
        w = _Windowed(s, prices, first).compute(win)
        rows[k]["avg_weights"] = {c: float(v) for c, v in w.mean().items() if v > 0.001}

    base = rows["balanced_static"]
    criteria = {}
    for k in ("hrp", "risk_budgeting"):
        r = rows[k]
        checks = [
            ("Sharpe netto >= bilanciato + 0,05", r["net"]["sharpe"], base["net"]["sharpe"] + 0.05,
             r["net"]["sharpe"] >= base["net"]["sharpe"] + 0.05),
            ("CAGR netto >= bilanciato - 0,50 punti", r["net"]["cagr_after_liquidation_tax"],
             base["net"]["cagr_after_liquidation_tax"] - 0.005,
             r["net"]["cagr_after_liquidation_tax"]
             >= base["net"]["cagr_after_liquidation_tax"] - 0.005),
            ("Max drawdown non peggiore di 2 punti", r["gross"]["max_drawdown"],
             base["gross"]["max_drawdown"] - 0.02,
             r["gross"]["max_drawdown"] >= base["gross"]["max_drawdown"] - 0.02),
        ]  # fmt: skip
        criteria[k] = {
            "checks": [
                {"criterion": c, "value": v, "threshold": t, "passed": bool(p)}
                for c, v, t, p in checks
            ],
            "candidate": all(p for *_, p in checks),
        }
    return {
        "period": {"start": str(first.date()), "end": str(prices.index[-1].date())},
        "rows": rows,
        "criteria": criteria,
    }


def render_allocation(report: dict[str, Any]) -> str:
    lines = [
        "# Esito — Allocazioni con skfolio contro il bilanciato statico",
        "",
        "Eseguito come da [pre-registrazione](2026-11-06-preregistration-skfolio-allocation.md). "
        f"Periodo {report['period']['start']} → {report['period']['end']}, ribilanciamento "
        "annuale, costi 10 bps, tasse italiane.",
        "",
        "| | CAGR lordo | CAGR netto | Sharpe netto | Max drawdown | Turnover |",
        "|---|---|---|---|---|---|",
    ]
    for k, r in report["rows"].items():
        g, n = r["gross"], r["net"]
        lines.append(
            f"| {LABELS[k]} | {_pct(g['cagr'])} | {_pct(n['cagr_after_liquidation_tax'])} | "
            f"{_num(n['sharpe'])} | {_pct(g['max_drawdown'])} | {_pct(g['annual_turnover'])} |"
        )
    for k, c in report["criteria"].items():
        verdict = "candidato per i portafogli modello" if c["candidate"] else "non adottato"
        header = "| Criterio | Valore | Soglia | Esito |"
        lines += ["", f"## {LABELS[k]}: **{verdict}**", "", header, "|---|---|---|---|"]
        for ch in c["checks"]:
            fmt = _num if "Sharpe" in ch["criterion"] else _pct
            lines.append(
                f"| {ch['criterion']} | {fmt(ch['value'])} | {fmt(ch['threshold'])} | "
                f"{'✅' if ch['passed'] else '❌'} |"
            )
        w = report["rows"][k]["avg_weights"]
        lines += ["", "Pesi medi: " + ", ".join(f"{s} {_pct(v)}" for s, v in w.items()) + "."]
    lines += ["", "Limiti: come negli studi precedenti (proxy USD in EUR, tasse semplificate, "
              "dati Yahoo). Risultati passati, non consulenza finanziaria."]  # fmt: skip
    return "\n".join(lines) + "\n"
