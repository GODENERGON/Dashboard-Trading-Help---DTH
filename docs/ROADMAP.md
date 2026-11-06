# Roadmap

Ogni milestone ha criteri di uscita verificabili. Si passa alla successiva solo quando sono
soddisfatti.

## M0 — Harness ✅
- Documentazione, contratti (`DataProvider`, `Signal`, `Forecaster`), harness walk-forward,
  test anti-lookahead, CI.
- Visione aggiornata: app Windows (ADR 0003), regole di evidenza (ADR 0004), connettori in sola
  lettura (ADR 0005), registro fonti con schema e test.
- **Uscita:** `make check` verde in CI.

## M1 — Dati e backtest reali
- Adattatori yfinance + Stooq (prezzi), FRED, BCE, Cboe, World Bank (materie prime); job
  giornalieri; controlli di qualità.
- Porting di `backtest_trend_refined.py` nel contratto `Signal`.
- Universo UCITS definitivo (`config/universe.yaml`).
- Motore delle `HighlightRule` con le regole di rischio, regime e dati.
- **Uscita:** report di validazione reale della strategia trend; API con regime, rischio,
  salute delle fonti ed evidenze.

## M2 — App Windows MVP (moduli P0)
- Shell Tauri + sidecar Python (PyInstaller), installer `.msi`, CI di build su Windows.
- Tab: Panoramica, Temi (struttura), Materie prime (oro), Confronti, Strategie, Fonti,
  Impostazioni.
- Design "Sala controllo" ([`DESIGN.md`](DESIGN.md)).
- Notifiche di Windows e Telegram.
- **Uscita:** installazione pulita su un PC Windows senza Python; uso quotidiano per 2
  settimane; tempo di decisione < 5 minuti.

## M3 — Contesto (moduli P1)
- Notizie (`NewsProvider`), temi completi (immobiliare con ponte allo scraper, crypto,
  obbligazioni, energia).
- Tab Startup e IPO con schede, watchlist e regole di evidenza.
- Materie prime complete, COT, sentiment, prediction market.
- LLM opzionale (Anthropic, OpenAI, Ollama) per riassunti e bozze di schede con fonti.
- Plug-in di modelli (TimesFM 2.5, Chronos-2, Moirai-2, Kronos) con skill score vs baseline.
- Portafoglio manuale, vista fiscale, stress test, journal.
- **Uscita:** ogni pannello ha fonte, aggiornamento e test; nessun modello attivo con skill ≤ 0.

## M4 — Connettori e paper trading
- Connettori in sola lettura: IBKR, Directa, exchange crypto (ccxt), piattaforme di
  crowdfunding dove possibile.
- Patrimonio aggregato, look-through degli ETF, riconciliazione.
- Paper trading IBKR per le strategie `validated`.
- **Uscita:** 3 mesi di paper con tracking error accettabile e riconciliazione senza errori.

## M5 — Live con capitale minimo
- Esecuzione con conferma umana e limiti hard, previo ADR.
- **Uscita:** 6 mesi senza violazioni di policy → valutazione dello scale-up.
