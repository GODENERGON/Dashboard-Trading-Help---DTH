"""Study: multi-asset trend strategy on the UCITS universe, gross and net of Italian taxes.

Pipeline: build an EUR price panel (UCITS history, extended backwards with USD proxies
converted to EUR) → pre-registered default config → parameter grid (robustness) →
walk-forward out-of-sample → benchmarks (buy & hold world equity, 60/40) → report.
"""

from __future__ import annotations

import itertools
import logging
from dataclasses import dataclass
from datetime import date
from typing import Any

import numpy as np
import pandas as pd

from dth.backtest import BacktestConfig, compute_metrics, walk_forward
from dth.backtest.portfolio import PortfolioResult, simulate_portfolio
from dth.backtest.taxes import TaxModel
from dth.core.config import Universe
from dth.providers.base import DataProvider
from dth.signals import MultiAssetTrend

log = logging.getLogger(__name__)

FX_SYMBOL = "EURUSD=X"  # USD per 1 EUR
MAX_GAP_DAYS = 5
INITIAL = 100_000.0


# ── Data ─────────────────────────────────────────────────────────────────────


@dataclass
class PanelMeta:
    symbol: str
    first_ucits: str | None
    proxy: str | None
    first_date: str | None
    spliced_days: int
    suspicious_jumps: int


def _close(provider: DataProvider, symbol: str, start: date, end: date) -> pd.Series:
    try:
        s = provider.fetch(symbol, start, end)["close"]
    except LookupError:
        log.warning("no data for %s", symbol)
        return pd.Series(dtype=float)
    return s[s > 0].dropna()


def splice(ucits: pd.Series, proxy_eur: pd.Series) -> tuple[pd.Series, int]:
    """Extend ``ucits`` backwards with ``proxy_eur`` returns, rescaled at the first UCITS date."""
    if ucits.empty:
        return proxy_eur, len(proxy_eur)
    if proxy_eur.empty:
        return ucits, 0
    first = ucits.index[0]
    before = proxy_eur.loc[:first]
    if len(before) < 2:
        return ucits, 0
    scaled = before * (ucits.iloc[0] / before.iloc[-1])
    out = pd.concat([scaled.iloc[:-1], ucits])
    return out[~out.index.duplicated(keep="last")], len(scaled) - 1


def build_price_panel(
    provider: DataProvider,
    universe: Universe,
    start: date,
    end: date,
    cash_symbol: str | None = "XEON.MI",
) -> tuple[pd.DataFrame, list[PanelMeta]]:
    fx = _close(provider, FX_SYMBOL, start, end)
    series: dict[str, pd.Series] = {}
    meta: list[PanelMeta] = []
    for inst in universe.instruments:
        ucits = _close(provider, inst.symbol, start, end)
        first_ucits = str(ucits.index[0].date()) if len(ucits) else None
        spliced_days = 0
        if inst.proxy:
            proxy_usd = _close(provider, inst.proxy, start, end)
            proxy_eur = (proxy_usd / fx.reindex(proxy_usd.index).ffill()).dropna()
            ucits, spliced_days = splice(ucits, proxy_eur)
        jumps = int((ucits.pct_change().abs() > 0.25).sum()) if len(ucits) else 0
        if not ucits.empty:
            series[inst.symbol] = ucits
        meta.append(
            PanelMeta(
                symbol=inst.symbol,
                first_ucits=first_ucits,
                proxy=inst.proxy,
                first_date=str(ucits.index[0].date()) if len(ucits) else None,
                spliced_days=spliced_days,
                suspicious_jumps=jumps,
            )
        )
    panel = pd.DataFrame(series).sort_index()
    panel.index = pd.DatetimeIndex(panel.index)
    panel = panel[panel.index.dayofweek < 5].ffill(limit=MAX_GAP_DAYS)
    if cash_symbol in panel.columns:
        panel[cash_symbol] = panel[cash_symbol].bfill()  # flat before inception
    first_valid = panel.dropna(how="all").index[0]
    return panel.loc[first_valid:], meta


# ── Study ────────────────────────────────────────────────────────────────────

GRID_AXES: dict[str, list[Any]] = {
    "lookbacks": [(63, 126, 252), (126, 252), (21, 63, 126, 252)],
    "sma_window": [150, 200],
    "top_k": [2, 3, 4],
}


def grid() -> list[dict[str, Any]]:
    keys = list(GRID_AXES)
    return [dict(zip(keys, combo, strict=True)) for combo in itertools.product(*GRID_AXES.values())]


class _StaticWeights:
    """Benchmark helper: fixed weights on the available assets, renormalized."""

    def __init__(self, weights: dict[str, float], name: str) -> None:
        self.weights = weights
        self.name = name

    def compute(self, prices: pd.DataFrame) -> pd.DataFrame:
        w = pd.DataFrame(0.0, index=prices.index, columns=prices.columns)
        avail = prices[list(self.weights)].notna()
        for sym, wt in self.weights.items():
            w[sym] = avail[sym] * wt
        total = w.sum(axis=1).replace(0, np.nan)
        return w.div(total, axis=0).fillna(0.0)

    def params(self) -> dict[str, Any]:
        return dict(self.weights)


class _Windowed:
    """Signal computed on the full history (causal warm-up), traded only inside a window."""

    def __init__(self, signal: Any, full: pd.DataFrame, start: pd.Timestamp) -> None:
        self._w = signal.compute(full).loc[start:]
        self.name = signal.name

    def compute(self, prices: pd.DataFrame) -> pd.DataFrame:
        return self._w.loc[prices.index]

    def params(self) -> dict[str, Any]:
        return {}


def _summary(res: PortfolioResult) -> dict[str, float]:
    rets = res.equity.pct_change().dropna()
    m = compute_metrics(rets)
    years = m["years"]
    out = {
        "cagr": m["cagr"],
        "volatility": m["volatility"],
        "sharpe": m["sharpe"],
        "max_drawdown": m["max_drawdown"],
        "annual_turnover": float(res.turnover.sum() / years),
    }
    if res.tax_history:
        out["cagr_after_liquidation_tax"] = (res.liquidation_value / INITIAL) ** (1 / years) - 1
        out["taxes_paid_total"] = float(res.taxes_paid.sum())
    return out


def _yearly(res: PortfolioResult) -> dict[int, float]:
    eq = res.equity
    ye = eq.groupby(eq.index.year).last()
    prev = ye.shift(1)
    prev.iloc[0] = eq.iloc[0]
    return {int(y): float(v) for y, v in (ye / prev - 1).items()}


def _pair(sig: Any, prices: pd.DataFrame, cfg: BacktestConfig, tax: TaxModel) -> dict[str, Any]:
    g = simulate_portfolio(sig, prices, cfg, initial=INITIAL)
    n = simulate_portfolio(sig, prices, cfg, tax=tax, initial=INITIAL)
    return {"gross": _summary(g), "net": _summary(n), "yearly": _yearly(g), "_net_res": n,
            "_gross_res": g}  # fmt: skip


def _strip(d: dict[str, Any]) -> dict[str, Any]:
    return {k: v for k, v in d.items() if not k.startswith("_")}


def run_study(
    prices: pd.DataFrame,
    tax: TaxModel,
    *,
    cash_symbol: str = "XEON.MI",
    world: str = "SWDA.MI",
    us: str = "CSSPX.MI",
    bond: str = "IBGL.MI",
    config: BacktestConfig | None = None,
) -> dict[str, Any]:
    config = config or BacktestConfig(rebalance="ME", cost_bps=10.0)
    bench_cfg = BacktestConfig(rebalance="YE", cost_bps=config.cost_bps)
    default = MultiAssetTrend(cash_symbol=cash_symbol)

    # Windows: whole history, and since the world-equity UCITS exists (fair comparison).
    full_start = prices.index[0] + pd.Timedelta(days=400)  # warm-up for 12m momentum
    world_start = prices[world].first_valid_index() if world in prices else full_start
    windows = {
        "full": (max(full_start, prices[us].first_valid_index()) if us in prices else full_start),
        "since_world": max(world_start, full_start),
    }
    benches = {
        "full": {
            "buy_and_hold_us": _StaticWeights({us: 1.0}, "bh_us"),
            "sixty_forty_us": _StaticWeights({us: 0.6, bond: 0.4}, "60_40_us"),
        },
        "since_world": {
            "buy_and_hold_world": _StaticWeights({world: 1.0}, "bh_world"),
            "sixty_forty_world": _StaticWeights({world: 0.6, bond: 0.4}, "60_40_world"),
        },
    }

    comparisons: dict[str, Any] = {}
    default_detail: dict[str, Any] = {}
    for wname, start in windows.items():
        win = prices.loc[start:]
        strat = _pair(_Windowed(default, prices, start), win, config, tax)
        rows = {"strategy": strat}
        for bname, bsig in benches[wname].items():
            if all(c in win for c in bsig.weights):
                rows[bname] = _pair(bsig, win, bench_cfg, tax)
        comparisons[wname] = {
            "start": str(start.date()),
            "rows": {k: _strip(v) for k, v in rows.items()},
        }
        if wname == "full":
            net_eq = strat["_net_res"].equity
            default_detail = {
                "params": default.params(),
                "net_sharpe": compute_metrics(net_eq.pct_change().dropna())["sharpe"],
                "tax_history": strat["_net_res"].tax_history,
                "avg_weights": {k: float(v) for k, v in strat["_gross_res"].weights.mean().items()},
                "time_mostly_cash": float(
                    (strat["_gross_res"].weights.get(cash_symbol, 0) > 0.5).mean()
                ),
            }

    grid_rows = []
    gstart = windows["full"]
    for params in grid():
        sig = _Windowed(MultiAssetTrend(cash_symbol=cash_symbol, **params), prices, gstart)
        pr = _pair(sig, prices.loc[gstart:], config, tax)
        grid_rows.append(
            {
                "params": {**params, "lookbacks": list(params["lookbacks"])},
                "gross": pr["gross"],
                "net": pr["net"],
            }
        )
    sharpes = [r["gross"]["sharpe"] for r in grid_rows]
    net_cagrs = [r["net"]["cagr_after_liquidation_tax"] for r in grid_rows]

    wf = walk_forward(
        lambda **p: MultiAssetTrend(cash_symbol=cash_symbol, **p),
        prices,
        grid=grid(),
        config=config,
        train_years=5,
        test_years=1,
    )

    return {
        "period": {"start": str(prices.index[0].date()), "end": str(prices.index[-1].date())},
        "config": {**config.__dict__, "initial": INITIAL},
        "default": default_detail,
        "comparisons": comparisons,
        "grid": {
            "rows": grid_rows,
            "share_positive_sharpe": float(np.mean([s > 0 for s in sharpes])),
            "median_sharpe": float(np.median(sharpes)),
            "median_net_cagr": float(np.median(net_cagrs)),
            "min_net_cagr": float(np.min(net_cagrs)),
            "max_net_cagr": float(np.max(net_cagrs)),
        },
        "walk_forward": {
            "oos": wf.oos_metrics,
            "folds": [
                {
                    "test": f"{f.test_start}..{f.test_end}",
                    "params": f.params,
                    "sharpe": f.test_metrics["sharpe"],
                }
                for f in wf.folds
            ],  # fmt: skip
            "note": "fast engine, gross of taxes",
        },
    }


# ── Report ───────────────────────────────────────────────────────────────────


def _pct(x: float) -> str:
    return f"{x * 100:,.1f}%".replace(",", "X").replace(".", ",").replace("X", ".")


def _eur(x: float) -> str:
    return f"{x:,.0f} €".replace(",", ".")


def _num(x: float) -> str:
    return f"{x:.2f}".replace(".", ",")


LABELS = {
    "strategy": "Strategia trend",
    "buy_and_hold_us": "Buy & hold S&P 500",
    "sixty_forty_us": "60/40 S&P 500 / titoli di Stato",
    "buy_and_hold_world": "Buy & hold MSCI World",
    "sixty_forty_world": "60/40 MSCI World / titoli di Stato",
}
WINDOW_TITLES = {
    "full": "Tutto il periodo (include la crisi del 2008)",
    "since_world": "Dalla quotazione dell'MSCI World UCITS (solo il ciclo 2009-oggi)",
}


def _table(rows: dict[str, Any]) -> list[str]:
    out = [
        "| | CAGR lordo | CAGR netto | Volatilità | Sharpe lordo | Max drawdown | Turnover |",
        "|---|---|---|---|---|---|---|",
    ]
    for key, r in rows.items():
        g, n = r["gross"], r["net"]
        out.append(
            f"| {LABELS.get(key, key)} | {_pct(g['cagr'])} | "
            f"{_pct(n['cagr_after_liquidation_tax'])} | {_pct(g['volatility'])} | "
            f"{_num(g['sharpe'])} | {_pct(g['max_drawdown'])} | {_pct(g['annual_turnover'])} |"
        )
    return out


def render_markdown(report: dict[str, Any], panel_meta: list[dict[str, Any]]) -> str:
    d = report["default"]
    g = report["grid"]
    full = report["comparisons"]["full"]["rows"]
    lines = [
        "# Studio: trend multi-asset sull'universo UCITS",
        "",
        f"Dati {report['period']['start']} → {report['period']['end']}. Ribilanciamento "
        f"mensile, costi {report['config']['cost_bps']:.0f} bps per lato, esecuzione alla "
        "chiusura successiva alla decisione. Capitale iniziale 100.000 €. "
        "**CAGR netto** = dopo tasse annuali (26%, 12,5% sui titoli di Stato, IVAFE 0,2%) e "
        "dopo aver venduto tutto alla fine.",
        "",
        "Configurazione di default scelta prima di vedere i dati: momentum medio 3/6/12 mesi, "
        "filtro media mobile 200 giorni, 4 strumenti al massimo, pesi a volatilità inversa "
        "con tetto 25%, resto in liquidità (XEON).",
        "",
    ]
    for wname, comp in report["comparisons"].items():
        lines += [f"## {WINDOW_TITLES[wname]} — dal {comp['start']}", "", *_table(comp["rows"]), ""]
    lines += [
        f"Sharpe della strategia al netto delle tasse: {_num(d['net_sharpe'])}. "
        f"Tasse pagate in totale: {_eur(full['strategy']['net']['taxes_paid_total'])}. "
        f"Mesi prevalentemente in liquidità: {_pct(d['time_mostly_cash'])}.",
        "",
        "## Robustezza dei parametri",
        "",
        f"Griglia di {len(g['rows'])} combinazioni sul periodo completo. Sharpe > 0 nel "
        f"{_pct(g['share_positive_sharpe'])} dei casi; Sharpe mediano "
        f"{_num(g['median_sharpe'])}; CAGR netto mediano "
        f"{_pct(g['median_net_cagr'])} (min {_pct(g['min_net_cagr'])}, "
        f"max {_pct(g['max_net_cagr'])}).",
        "",
        "## Walk-forward (fuori campione, lordo)",
        "",
        f"CAGR {_pct(report['walk_forward']['oos']['cagr'])}, Sharpe "
        f"{_num(report['walk_forward']['oos']['sharpe'])}, max drawdown "
        f"{_pct(report['walk_forward']['oos']['max_drawdown'])}, su "
        f"{len(report['walk_forward']['folds'])} anni di test.",
        "",
        "## Rendimenti per anno (lordi, periodo completo)",
        "",
        "| Anno | Strategia | Buy & hold S&P 500 | 60/40 |",
        "|---|---|---|---|",
    ]
    ys = full["strategy"]["yearly"]
    bh = full.get("buy_and_hold_us", {}).get("yearly", {})
    sf = full.get("sixty_forty_us", {}).get("yearly", {})
    for year, r in ys.items():
        lines.append(
            f"| {year} | {_pct(r)} | {_pct(bh[year]) if year in bh else '—'} | "
            f"{_pct(sf[year]) if year in sf else '—'} |"
        )
    lines += [
        "",
        "## Dati",
        "",
        "| Strumento | Proxy | Primo dato UCITS | Primo dato usato | Giorni da proxy "
        "| Salti > 25% |",
        "|---|---|---|---|---|---|",
    ]
    for m in panel_meta:
        lines.append(
            f"| {m['symbol']} | {m['proxy'] or '—'} | {m['first_ucits'] or '—'} "
            f"| {m['first_date']} | {m['spliced_days']} | {m['suspicious_jumps']} |"
        )
    lines += [
        "",
        "## Limiti noti",
        "",
        "- Prima della quotazione degli UCITS si usano ETF USA convertiti in euro: il proxy di "
        "IBGL (Treasury USA a lunga scadenza) non è un titolo di Stato europeo.",
        "- XEON prima della quotazione è trattato come liquidità a rendimento zero.",
        "- Tasse pagate a fine anno invece che a giugno; costo medio ponderato; IVAFE 0,2% annuo.",
        "- Dati Yahoo Finance: fonte non ufficiale, da incrociare prima di decisioni reali.",
        "- Risultati passati, nessuna garanzia sul futuro. Non è consulenza finanziaria.",
    ]
    return "\n".join(lines) + "\n"
