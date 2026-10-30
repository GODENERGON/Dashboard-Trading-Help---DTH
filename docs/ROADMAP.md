# Roadmap

Ogni milestone ha criteri di uscita verificabili. Si passa alla successiva solo quando sono
soddisfatti.

## M0 — Harness ✅ (questa fase)
- Documentazione, contratti (`DataProvider`, `Signal`, `Forecaster`), harness walk-forward,
  test anti-lookahead, CI.
- **Uscita:** `make test` e `make lint` verdi in CI; un walk-forward di esempio gira su dati
  sintetici.

## M1 — Dati e backtest reali
- Adattatori yfinance + Stooq (prezzi), FRED (macro), CBOE (VIX); store Parquet/DuckDB; job
  giornaliero.
- Porting di `backtest_trend_refined.py` nel contratto `Signal` (trend-following multi-ETF con
  dual momentum e top-K, rendimento della liquidità).
- Universo UCITS definito (`config/universe.yaml`).
- **Uscita:** report di validazione reale per la strategia trend; pannello "Salute dei dati"
  esposto via API.

## M2 — Dashboard MVP (moduli P0)
- Frontend: banda di regime, titolo di regime, rischio, segnali validati, salute dei dati.
- Alert Telegram.
- **Uscita:** uso quotidiano per 2 settimane; tempo di decisione < 5 minuti.

## M3 — Contesto (moduli P1)
- Calendario eventi, COT, sentiment, cross-asset, prediction market.
- Forecaster TSFM (TimesFM 2.5, Chronos-2) in modalità sperimentale con skill score vs baseline.
- **Uscita:** ogni pannello P1 ha fonte, freschezza e test; il forecaster è attivo solo se lo
  skill score è > 0.

## M4 — Paper trading
- Integrazione IBKR paper, riconciliazione, journal.
- **Uscita:** 3 mesi di paper con tracking error vs backtest accettabile.

## M5 — Live con capitale minimo
- Esecuzione con conferma umana e limiti hard.
- **Uscita:** 6 mesi senza violazioni di policy → valutazione dello scale-up.
