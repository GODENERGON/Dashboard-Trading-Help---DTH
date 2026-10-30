# Catalogo moduli (pannelli e informazioni)

Ogni modulo è un'unità indipendente: ha una o più fonti dati, una trasformazione e un pannello UI.
Priorità: **P0** = MVP, **P1** = subito dopo, **P2** = quando il resto è stabile.

## 1. Regime di mercato — P0

| Info | Come | Perché serve |
|---|---|---|
| Trend multi-orizzonte | Prezzo vs medie 50/200, momentum 3/6/12 mesi | Base del trend-following |
| Regime di volatilità | Vol realizzata, percentile storico, VIX e struttura a termine (VIX/VIX3M) | Backwardation = stress: riduce l'esposizione |
| Condizioni finanziarie | Curva 10y-2y, spread high yield (OAS), NFCI (FRED) | Anticipano i regimi di risk-off |
| Breadth | % titoli sopra la MA200, advance/decline, nuovi massimi e minimi | Un rialzo "stretto" è fragile |
| Rilevazione di regime | Hidden Markov Model (2-3 stati) su rendimenti e volatilità | Etichetta il regime in modo oggettivo |

## 2. Segnali di strategia — P0

- Segnali del sistema trend-following multi-ETF (dual momentum, top-K).
- Ogni segnale ha una **scheda di validazione**: equity curve fuori campione, Sharpe, max DD,
  turnover, costi, stabilità dei parametri (heatmap della sweep).
- Stato: `research` → `validated` → `paper` → `live`. In UI compaiono solo `validated`+.

## 3. Rischio e portafoglio — P0

- Posizioni, esposizione per asset class, valuta, area geografica.
- Drawdown corrente vs massimo storico e vs limite di policy.
- **Calcolatore di sizing**: volatility targeting, rischio per trade, ATR stop.
- VaR/CVaR storico, matrice di correlazione rolling (le diversificazioni spariscono nei crash).
- Journal dei trade: motivo di ingresso, regime al momento, esito. Serve a misurare la disciplina.

## 4. Calendario eventi — P1

- Riunioni FOMC/BCE, CPI, payroll, PIL (calendario macro).
- Trimestrali delle principali componenti degli indici.
- Scadenze opzioni (terzo venerdì), ribilanciamenti indici, stacco dividendi degli ETF.
- **Probabilità dai prediction market** (Polymarket/Kalshi) su eventi macro: quanto il mercato
  prezza un taglio dei tassi, una recessione…

## 5. Posizionamento e sentiment — P1

- **COT report CFTC** (settimanale): posizionamento di speculatori e commercial su futures
  (indici, oro, petrolio, Treasury, valute). Gli estremi sono segnali contrarian noti.
- Sondaggio AAII, esposizione NAAIM, put/call ratio CBOE.
- Flussi ETF (variazione delle quote in circolazione).
- Sentiment delle notizie: RSS/GDELT → FinBERT, aggregato per asset. Google Trends sui termini
  di panico ("recession", "crash").
- Insider trading (SEC Form 4) e 13F per singoli titoli (P2).

## 6. Cross-asset — P1

- Dollaro (DXY), oro, rame/oro (proxy di crescita), petrolio, BTC (proxy di propensione al rischio).
- Correlazione azioni-obbligazioni rolling: quando diventa positiva, il 60/40 non protegge.
- Mappa di forza relativa tra settori e regioni.

## 7. Forecast e incertezza — P1 (sperimentale)

- Forecast di **volatilità** e bande di quantili (TimesFM 2.5 / Chronos-2) confrontati con
  baseline (GARCH, vol realizzata EWMA).
- Mostrato solo come banda di incertezza e input per il sizing; mai come target di prezzo.
- Il pannello mostra sempre lo **skill score vs baseline** in walk-forward: se ≤ 0, il modello
  viene nascosto.

## 8. Statistiche e stagionalità — P2

- Distribuzione dei rendimenti (code grasse, skew), stagionalità mensile e intra-settimana.
- Storia dei drawdown e tempi di recupero.
- "Cosa è successo storicamente in regimi simili" (analoghi condizionati, con campione
  dichiarato).

## 9. Copilota di ricerca LLM — P2

- Riassunti delle notizie e trascrizioni delle trimestrali, risposte del tipo "perché si è mosso
  X oggi?", con fonti citate.
- Generazione di ipotesi da testare nell'harness (mai segnali diretti).

## 10. Salute dei dati e del sistema — P0

- Freschezza per fonte, gap, outlier, controlli su split e dividendi.
- Stato dei job di ingestione, ultimo run, errori.
- Badge di freschezza su ogni pannello (verde/ambra/rosso).

## 11. Alert — P0

- Telegram (riusa il bot già attivo sul NUC): cambio di segnale, superamento dei limiti di
  rischio, regime di stress, dato non aggiornato.
- Regole configurabili in YAML, con anti-spam (cooldown).

## 12. Esecuzione — P2 (dietro gate)

- Interactive Brokers (`ib_async`) in paper trading, poi live con limiti hard.
- Riconciliazione delle posizioni broker con la dashboard.
