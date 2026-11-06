# Roadmap

Ogni milestone ha criteri di uscita verificabili. Si passa alla successiva solo quando sono
soddisfatti. Priorità attuale: **avere presto una build installabile per il primo tester**
([ADR 0007](adr/0007-first-tester-zero-config-no-nuc.md)), poi allargare.

## M0 — Harness ✅
- Documentazione, contratti, harness walk-forward, test anti-lookahead, CI.
- Decisioni: app Windows (ADR 0003), regole di evidenza (ADR 0004), connettori in sola lettura
  (ADR 0005), limiti crypto e startup (ADR 0006), primo tester e niente NUC (ADR 0007).
- Registro fonti, regole di evidenza e watchlist startup di partenza.

## M1 — Prima build per il tester ("fetta verticale")
Poche cose, ma installabili e funzionanti dall'inizio alla fine.
- Shell Tauri + sidecar Python (PyInstaller), installer `.msi`, CI di build su Windows,
  pubblicazione su GitHub Releases, aggiornamento automatico.
- Primo avvio guidato, glossario contestuale, pulsante "Invia feedback".
- Fonti gratuite senza chiave: prezzi (yfinance + Stooq per l'incrocio), BCE, World Bank (materie
  prime), Cboe (VIX).
- Tab **Panoramica** (banda di regime, regime corrente, evidenze, salute delle fonti), **Materie
  prime** (oro e principali), **Confronti** (base 100, rapporto, correlazione), **Startup** (sola
  lettura della watchlist di partenza), **Fonti**.
- Motore delle `HighlightRule` con le prime regole di regime e dati.
- Design "Sala controllo" ([`DESIGN.md`](DESIGN.md)).
- **Uscita:** il tester installa l'app da solo seguendo il README, la usa per 2 settimane e invia
  almeno un feedback; nessun crash bloccante.

## M2 — Strategie e rischio
- Porting di `backtest_trend_refined.py` nel contratto `Signal`; universo UCITS definitivo.
- Tab **Strategie** con schede di validazione reali; tab **Portafoglio** con inserimento manuale,
  limiti di rischio (inclusi crypto ≤ 10%, startup ≤ 15%), quota non liquidabile, stress test.
- Correzioni e priorità dal feedback del tester.
- **Uscita:** report di validazione reale della strategia trend; tempo di decisione < 5 minuti.

## M3 — Contesto
- Notizie (`NewsProvider`), temi completi (immobiliare con ponte allo scraper, ETF, indici,
  crypto, obbligazioni, energia e nucleare).
- Tab **IPO** con calendario, schede e statistiche; schede startup complete.
- FRED e altre fonti con chiave gratuita (configurazione guidata).
- LLM opzionale (Anthropic, OpenAI, Ollama) per riassunti e bozze di schede con fonti.
- Plug-in di modelli (TimesFM 2.5, Chronos-2, Moirai-2, Kronos) con skill score vs baseline.
- Vista fiscale, journal, checklist pre-trade.
- **Uscita:** ogni pannello ha fonte, aggiornamento e test; nessun modello attivo con skill ≤ 0.

## M4 — Connettori e paper trading
- Connettori in sola lettura: broker scelto, exchange crypto (ccxt), crowdfunding dove possibile.
- Patrimonio aggregato, look-through degli ETF, riconciliazione.
- Paper trading per le strategie `validated`.
- **Uscita:** 3 mesi di paper con tracking error accettabile e riconciliazione senza errori.

## M5 — Live con capitale minimo
- Esecuzione con conferma umana e limiti hard, previo ADR.
- **Uscita:** 6 mesi senza violazioni di policy → valutazione dello scale-up.
