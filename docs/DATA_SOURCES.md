# Fonti dati

Regola: ogni fonte ha un adattatore in `backend/src/dth/providers/` che implementa il contratto
`DataProvider` (vedi [`ARCHITECTURE.md`](ARCHITECTURE.md)). Nessun modulo legge una fonte
direttamente.

> ⚠️ Costi, limiti e termini d'uso cambiano: verificarli prima di implementare ogni adattatore e
> aggiornare questa tabella.

## Prezzi

| Fonte | Copertura | Costo | Note |
|---|---|---|---|
| yfinance (Yahoo) | Globale, inclusi ETF UCITS (`.MI`, `.DE`, `.L`, `.AS`) | Gratis | Non ufficiale, può rompersi: va bene per la ricerca, non come unica fonte |
| Stooq | Indici, ETF, azioni | Gratis | Utile come fonte secondaria e per i controlli incrociati |
| Tiingo | USA, buona qualità EOD | Gratis o economico | Ottima per azioni e ETF USA |
| EODHD | Borse EU incluse (Borsa Italiana, Xetra) | A pagamento | Candidata come fonte "seria" per gli UCITS |
| Interactive Brokers API | Quello che il conto vede | Con il conto | Fonte di verità per l'esecuzione |

## Macro e condizioni finanziarie

| Fonte | Cosa | Costo |
|---|---|---|
| FRED (St. Louis Fed) | Curva dei tassi, spread HY, NFCI, inflazione, occupazione | Gratis (API key) |
| ECB Data Portal | Tassi BCE, €STR, aggregati monetari area euro | Gratis |
| Eurostat | Macro UE | Gratis |

## Volatilità, opzioni, posizionamento

| Fonte | Cosa | Costo |
|---|---|---|
| CBOE | VIX, VIX3M, VVIX, SKEW, put/call | Gratis (CSV storici) |
| CFTC | Commitments of Traders (settimanale) | Gratis |
| AAII / NAAIM | Sondaggi di sentiment ed esposizione | Gratis o con iscrizione |

## Eventi e sentiment

| Fonte | Cosa | Costo |
|---|---|---|
| Calendari banche centrali (Fed, BCE) | Date delle riunioni | Gratis |
| Polymarket / Kalshi | Probabilità implicite su eventi | API pubbliche (verificare i termini) |
| GDELT / RSS | Notizie | Gratis |
| Google Trends (`pytrends`) | Interesse di ricerca | Gratis, rate-limited |
| SEC EDGAR | Form 4, 13F, trimestrali | Gratis (User-Agent obbligatorio) |

## Modelli

| Modello | Uso | Licenza |
|---|---|---|
| TimesFM 2.5 (Google) | Forecast di volatilità e quantili | Apache-2.0 |
| Chronos-2 (Amazon) | Alternativa multivariata | Apache-2.0 |
| FinBERT | Sentiment delle notizie | Verificare sul model card |
| `hmmlearn` | Rilevazione di regime | BSD |
| `arch` | GARCH (baseline di volatilità) | NCSA |

## Contratto di qualità

Ogni serie salvata porta con sé: `source`, `fetched_at`, `as_of` (ultima osservazione),
`adjusted` (sì/no), `currency`. I controlli di qualità (gap, salti > N sigma, valori negativi,
duplicati) girano a ogni ingestione e alimentano il pannello "Salute dei dati".
