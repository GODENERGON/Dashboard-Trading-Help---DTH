"""Study: core-satellite and trend-regime indicator, exactly as pre-registered in
docs/research/2026-11-06-preregistration-core-satellite-and-regime.md.
"""

from __future__ import annotations

from typing import Any

import pandas as pd

from dth.backtest import BacktestConfig
from dth.backtest.portfolio import simulate_portfolio
from dth.backtest.taxes import TaxModel
from dth.regime import DEFENSIVE, MIXED, POSITIVE, evaluate_regime, regime_series
from dth.research.ucits_trend import (
    INITIAL,
    LABELS,
    _num,
    _pair,
    _pct,
    _StaticWeights,
    _strip,
    _Windowed,
)
from dth.signals import CoreSatellite, MultiAssetTrend

PRIMARY = {"satellite_share": 0.30, "band": 0.05}
SENSITIVITY = [
    {"satellite_share": 0.20, "band": 0.05},
    {"satellite_share": 0.50, "band": 0.05},
    {"satellite_share": 0.30, "band": 0.0},
]


def _windows(prices: pd.DataFrame, world: str, us: str) -> dict[str, pd.Timestamp]:
    full_start = max(prices.index[0] + pd.Timedelta(days=400), prices[us].first_valid_index())
    return {"full": full_start, "since_world": max(prices[world].first_valid_index(), full_start)}


def run_core_satellite_study(
    prices: pd.DataFrame,
    tax: TaxModel,
    *,
    cash_symbol: str = "XEON.MI",
    world: str = "SWDA.MI",
    us: str = "CSSPX.MI",
    bond: str = "IBGL.MI",
    cost_bps: float = 10.0,
) -> dict[str, Any]:
    windows = _windows(prices, world, us)
    bench_cfg = BacktestConfig(rebalance="YE", cost_bps=cost_bps)
    benches = {
        "full": {"sixty_forty_us": _StaticWeights({us: 0.6, bond: 0.4}, "60_40_us")},
        "since_world": {
            "sixty_forty_world": _StaticWeights({world: 0.6, bond: 0.4}, "60_40_world")
        },
    }

    def make(share: float) -> CoreSatellite:
        return CoreSatellite(
            core=(((world, us), 0.6), ((bond,), 0.4)),
            satellite=MultiAssetTrend(cash_symbol=cash_symbol),
            satellite_share=share,
        )

    variants = [("primary", PRIMARY)] + [(f"sens_{i + 1}", v) for i, v in enumerate(SENSITIVITY)]
    results: dict[str, Any] = {}
    for wname, start in windows.items():
        win = prices.loc[start:]
        rows: dict[str, Any] = {}
        for vname, v in variants:
            cfg = BacktestConfig(rebalance="ME", cost_bps=cost_bps, rebalance_band=v["band"])
            rows[vname] = _strip(
                _pair(_Windowed(make(v["satellite_share"]), prices, start), win, cfg, tax)
            )
            rows[vname]["variant"] = v
        trend_cfg = BacktestConfig(rebalance="ME", cost_bps=cost_bps)
        rows["trend_only"] = _strip(
            _pair(_Windowed(MultiAssetTrend(cash_symbol=cash_symbol), prices, start), win,
                  trend_cfg, tax)
        )  # fmt: skip
        for bname, bsig in benches[wname].items():
            rows[bname] = _strip(_pair(bsig, win, bench_cfg, tax))
        results[wname] = {"start": str(start.date()), "rows": rows}

    # Pre-registered success criteria (primary configuration only).
    checks = []
    for wname, bname in (("full", "sixty_forty_us"), ("since_world", "sixty_forty_world")):
        p = results[wname]["rows"]["primary"]
        b = results[wname]["rows"][bname]
        checks.append(
            {
                "window": wname,
                "criterion": "CAGR netto >= 60/40 - 0,25 punti",
                "value": p["net"]["cagr_after_liquidation_tax"],
                "threshold": b["net"]["cagr_after_liquidation_tax"] - 0.0025,
                "passed": p["net"]["cagr_after_liquidation_tax"]
                >= b["net"]["cagr_after_liquidation_tax"] - 0.0025,
            }
        )
        checks.append(
            {
                "window": wname,
                "criterion": "Sharpe netto >= 60/40",
                "value": p["net"]["sharpe"],
                "threshold": b["net"]["sharpe"],
                "passed": p["net"]["sharpe"] >= b["net"]["sharpe"],
            }
        )
    pf, bf = results["full"]["rows"]["primary"], results["full"]["rows"]["sixty_forty_us"]
    checks.append(
        {
            "window": "full",
            "criterion": "Max drawdown almeno 20% più basso del 60/40",
            "value": pf["gross"]["max_drawdown"],
            "threshold": 0.8 * bf["gross"]["max_drawdown"],
            "passed": abs(pf["gross"]["max_drawdown"]) <= 0.8 * abs(bf["gross"]["max_drawdown"]),
        }
    )

    # Regime indicator, evaluated on the core-only 60/40 (world with S&P 500 fallback).
    full_start = windows["full"]
    sixty_forty = simulate_portfolio(
        _Windowed(make(0.0), prices, full_start), prices.loc[full_start:], bench_cfg,
        initial=INITIAL,
    ).equity  # fmt: skip
    regime = regime_series(prices, cash_symbol, (world, us)).loc[full_start:]
    stats = evaluate_regime(regime, sixty_forty)
    useful = (
        stats[DEFENSIVE]["avg_fwd_21d_return"] < stats[POSITIVE]["avg_fwd_21d_return"]
        and stats[DEFENSIVE]["prob_drawdown_10pct_63d"] > stats[POSITIVE]["prob_drawdown_10pct_63d"]
    )
    changes = int((regime != regime.shift()).sum() - 1)

    return {
        "period": {"start": str(prices.index[0].date()), "end": str(prices.index[-1].date())},
        "windows": results,
        "criteria": checks,
        "validated": all(c["passed"] for c in checks),
        "regime": {
            "stats": stats,
            "useful": bool(useful),
            "changes_per_year": changes / (len(regime) / 252),
            "current": regime.iloc[-1],
            "current_as_of": str(regime.index[-1].date()),
            "last_12m": {str(d.date()): v for d, v in regime.iloc[-252::21].items()},
        },
    }


TITLES = {
    "primary": "Core-satellite 70/30 (primaria)",
    "sens_1": "Sensibilità: satellite 20%",
    "sens_2": "Sensibilità: satellite 50%",
    "sens_3": "Sensibilità: 70/30 senza banda",
    "trend_only": "Solo trend (studio precedente)",
}
WINDOWS = {
    "full": "Tutto il periodo (include il 2008)",
    "since_world": "Dalla quotazione dell'MSCI World UCITS",
}


def render_core_satellite(report: dict[str, Any]) -> str:
    lines = [
        "# Esito — Core-satellite e indicatore di regime",
        "",
        "Test eseguiti come da [pre-registrazione]"
        "(2026-11-06-preregistration-core-satellite-and-regime.md), senza modifiche ai "
        f"parametri. Dati {report['period']['start']} → {report['period']['end']}.",
        "",
        f"**Verdetto core-satellite: {'VALIDATA' if report['validated'] else 'NON validata'}"
        f"** (stato `{'validated' if report['validated'] else 'research'}`).",
        "",
        "## Criteri pre-registrati (configurazione primaria)",
        "",
        "| Finestra | Criterio | Valore | Soglia | Esito |",
        "|---|---|---|---|---|",
    ]
    for c in report["criteria"]:
        fmt = _num if "Sharpe" in c["criterion"] else _pct
        lines.append(
            f"| {WINDOWS[c['window']]} | {c['criterion']} | {fmt(c['value'])} | "
            f"{fmt(c['threshold'])} | {'✅' if c['passed'] else '❌'} |"
        )
    for wname, w in report["windows"].items():
        lines += [
            "",
            f"## {WINDOWS[wname]} — dal {w['start']}",
            "",
            "| | CAGR lordo | CAGR netto | Sharpe netto | Max drawdown | Turnover | Tasse pagate |",
            "|---|---|---|---|---|---|---|",
        ]
        for key, r in w["rows"].items():
            g, n = r["gross"], r["net"]
            label = TITLES.get(key) or LABELS.get(key, key)
            lines.append(
                f"| {label} | {_pct(g['cagr'])} | {_pct(n['cagr_after_liquidation_tax'])} | "
                f"{_num(n['sharpe'])} | {_pct(g['max_drawdown'])} | "
                f"{_pct(g['annual_turnover'])} | "
                f"{n['taxes_paid_total']:,.0f} €".replace(",", ".")
                + " |"
            )
    rg = report["regime"]
    lines += [
        "",
        "## Indicatore di regime",
        "",
        f"Valutato sul 60/40. **Utile secondo il criterio pre-registrato: "
        f"{'sì' if rg['useful'] else 'no'}.** Cambi di stato: "
        f"{_num(rg['changes_per_year'])} all'anno. Stato attuale ({rg['current_as_of']}): "
        f"**{rg['current']}**.",
        "",
        "| Stato | Quota del tempo | Rendimento medio 60/40 nei 21 giorni dopo | "
        "Probabilità di un calo ≥ 10% nei 63 giorni dopo |",
        "|---|---|---|---|",
    ]
    for state in (POSITIVE, MIXED, DEFENSIVE):
        s = rg["stats"][state]
        lines.append(
            f"| {state} | {_pct(s['share_of_time'])} | {_pct(s['avg_fwd_21d_return'])} | "
            f"{_pct(s['prob_drawdown_10pct_63d'])} |"
        )
    lines += [
        "",
        "Limiti: gli stessi dello [studio precedente](2026-11-06-ucits-trend.md) (proxy USD "
        "convertiti in euro prima della quotazione degli UCITS, tasse semplificate, dati Yahoo). "
        "Nel periodo completo il nucleo passa da CSSPX a SWDA quando SWDA viene quotato: la "
        "vendita relativa è tassata. Risultati passati, non consulenza finanziaria.",
    ]
    return "\n".join(lines) + "\n"
