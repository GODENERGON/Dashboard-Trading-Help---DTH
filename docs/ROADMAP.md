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

**Stato al 06/11/2026: fatto (M1a)** — shell Tauri + motore PyInstaller, installer NSIS per
utente senza permessi di amministratore, pacchetti Linux `.deb` e AppImage, CI `release` con smoke test del motore e
pre-release su GitHub, seme di prezzi incluso + aggiornamento automatico da Yahoo, motore delle
regole (drawdown dell'esempio, dati vecchi/fonte rotta; regime disattivato), guida al primo
avvio, feedback salvato sul PC (e-mail opzionale da segreto di build), Panoramica e Prodotti.
**Resta per M1b:** aggiornamento automatico dell'app, Stooq/BCE/World Bank/VIX, tab Materie
prime, Confronti, Startup, Fonti, glossario.
- Shell Tauri + sidecar Python (PyInstaller), installer `.exe` (NSIS), CI di build su Windows,
  pubblicazione su GitHub Releases, aggiornamento automatico.
- Primo avvio guidato, glossario contestuale, pulsante "Invia feedback".
- Fonti gratuite senza chiave: prezzi (yfinance + Stooq per l'incrocio), BCE, World Bank (materie
  prime), Cboe (VIX).
- Tab **Panoramica** (banda di regime, regime corrente, evidenze, salute delle fonti), **Materie
  prime** (oro e principali), **Confronti** (base 100, rapporto, correlazione), **Startup** (sola
  lettura della watchlist di partenza), **Fonti**.
- Motore delle `HighlightRule` con le prime regole di regime e dati.
- Design "Sala controllo in metallo liquido" ([`DESIGN.md`](DESIGN.md)), con Paper Shaders per la banda di regime.
- Tab **Prodotti** con classifica e portafogli modello.
- **Uscita:** il tester installa l'app da solo seguendo il README, la usa per 2 settimane e invia
  almeno un feedback; nessun crash bloccante.

## M2 — Strategie e rischio
- ✅ Strategia trend riscritta da zero (`MultiAssetTrend`), simulatore con tasse italiane,
  studio su dati reali via workflow `research`
  ([esito](research/2026-11-06-ucits-trend.md): non validata al netto delle tasse).
- ✅ Core-satellite e indicatore di regime pre-registrati e testati
  ([esito](research/2026-11-06-core-satellite-results.md)): core-satellite non validato;
  regime solo informativo (endpoint `/regime/trend`, regola `trend_regime` disattivata).
- ✅ Classifica prodotti per caratteristiche e portafogli modello (ADR 0009, [`PRODUCTS.md`](PRODUCTS.md)).
- Prossimo, se si continua la ricerca: trend solo sull'oro (ETC, redditi diversi) o uscite più
  lente, sempre pre-registrati.
- Tab **Strategie** con schede di validazione reali.
- Tab **Portafoglio**: conti con inserimento manuale e import CSV (DEGIRO, Scalable, generico),
  limiti di rischio (crypto ≤ 10%, startup ≤ 15%), quota non liquidabile, stress test
  ([ADR 0008](adr/0008-accounts-brokers-and-tax-ledger.md)).
- Tab **Fiscale**: registro plus/minus, scadenze delle minusvalenze, IVAFE e IVCA, export CSV.
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
- Connettori in sola lettura: Interactive Brokers (Flex Web Service), Coinbase, Binance,
  Bitfinex, Kraken, Bitpanda (ccxt), crowdfunding dove possibile; avvisi di piattaforma.
- Patrimonio aggregato, look-through degli ETF, riconciliazione.
- Paper trading per le strategie `validated`.
- **Uscita:** 3 mesi di paper con tracking error accettabile e riconciliazione senza errori.

## M5 — Live con capitale minimo
- Esecuzione con conferma umana e limiti hard, previo ADR.
- **Uscita:** 6 mesi senza violazioni di policy → valutazione dello scale-up.
