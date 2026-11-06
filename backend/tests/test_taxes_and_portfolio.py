from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from dth.backtest import BacktestConfig, run_backtest
from dth.backtest.portfolio import simulate_portfolio
from dth.backtest.taxes import CAPITAL, DIVERSE, SymbolTax, TaxLedger, TaxModel
from dth.core.config import REPO_ROOT, load_universe
from dth.signals import MultiAssetTrend
from dth.testing import synthetic_prices

MODEL = TaxModel(
    symbols={
        "ETF": SymbolTax(CAPITAL, 0.26),
        "ETC": SymbolTax(DIVERSE, 0.26),
    },
    wealth_tax_rate=0.0,
)


class _Hold:
    name = "hold"

    def __init__(self, col: str) -> None:
        self.col = col

    def compute(self, prices: pd.DataFrame) -> pd.DataFrame:
        w = pd.DataFrame(0.0, index=prices.index, columns=prices.columns)
        w[self.col] = 1.0
        return w

    def params(self) -> dict:
        return {}


def test_etf_gains_are_not_offset_by_losses() -> None:
    led = TaxLedger(MODEL)
    led.realize("ETF", 1000.0)
    led.realize("ETF", -1000.0)
    assert led.settle(2020, 0.0) == pytest.approx(260.0)
    assert led.loss_pool == [[2020, 1000.0]]


def test_diverse_losses_offset_later_gains_within_four_years() -> None:
    led = TaxLedger(MODEL)
    led.realize("ETC", -500.0)
    assert led.settle(2020, 0.0) == 0.0
    led.realize("ETC", 800.0)
    assert led.settle(2022, 0.0) == pytest.approx(300 * 0.26)
    assert led.loss_pool == []


def test_losses_expire_after_four_years() -> None:
    led = TaxLedger(MODEL)
    led.realize("ETF", -500.0)
    led.settle(2020, 0.0)
    led.realize("ETC", 500.0)
    assert led.settle(2025, 0.0) == pytest.approx(500 * 0.26)


def test_wealth_tax_on_holdings() -> None:
    led = TaxLedger(TaxModel(symbols=MODEL.symbols, wealth_tax_rate=0.002))
    assert led.settle(2020, 100_000.0) == pytest.approx(200.0)


def test_buy_and_hold_defers_tax_until_liquidation() -> None:
    idx = pd.bdate_range("2018-01-01", periods=252 * 3)
    px = pd.DataFrame({"ETF": 100 * np.exp(np.arange(len(idx)) * 0.0005)}, index=idx)
    cfg = BacktestConfig(cost_bps=0)
    res = simulate_portfolio(_Hold("ETF"), px, cfg, tax=MODEL)
    assert res.taxes_paid.iloc[:-1].sum() == 0
    gain = res.equity.iloc[-1] - 100_000
    assert res.liquidation_value == pytest.approx(res.equity.iloc[-1] - 0.26 * gain, rel=1e-6)


def test_simulator_is_one_bar_more_conservative_than_fast_engine() -> None:
    # Fast engine: decided at close t, earns t→t+1 (trades at the decision close).
    # Simulator: decided at close t, trades at close t+1, earns from t+1 on.
    px = synthetic_prices(periods=600)[["EQ_WORLD"]]
    cfg = BacktestConfig(rebalance="D", cost_bps=0)
    sim = simulate_portfolio(_Hold("EQ_WORLD"), px, cfg)
    eng = run_backtest(_Hold("EQ_WORLD"), px, cfg)
    assert sim.returns.iloc[1] == 0
    np.testing.assert_allclose(sim.returns.iloc[2:], eng.returns.iloc[2:], atol=1e-12)


def test_taxed_trend_strategy_ends_below_untaxed() -> None:
    px = synthetic_prices(periods=252 * 8)
    tax = TaxModel(symbols={c: SymbolTax(CAPITAL, 0.26) for c in px.columns})
    sig = MultiAssetTrend(cash_symbol="BOND_GOV")
    gross = simulate_portfolio(sig, px)
    net = simulate_portfolio(sig, px, tax=tax)
    assert net.liquidation_value < gross.equity.iloc[-1]
    assert net.tax_history and all(h["total"] >= 0 for h in net.tax_history)


def test_tax_model_from_repo_config() -> None:
    uni = load_universe(REPO_ROOT / "config" / "universe.example.yaml")
    model = TaxModel.from_config(
        REPO_ROOT / "config" / "tax.it.example.yaml", uni, govt_bond_share={"IBGL.MI": 1.0}
    )
    assert model.for_symbol("SWDA.MI") == SymbolTax(CAPITAL, 0.26)
    assert model.for_symbol("IBGL.MI").rate == pytest.approx(0.125)
    assert model.for_symbol("SGLD.MI").gains_kind == DIVERSE
