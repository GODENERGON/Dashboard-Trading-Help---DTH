# Fonti dati, notizie e connettori

## Il registro fonti è la fonte di verità

L'elenco completo e aggiornabile è in [`config/sources.example.yaml`](../config/sources.example.yaml),
validato dallo schema `dth.core.sources` (test in `backend/tests/test_sources.py`).
Nell'app, la tab *Fonti* permette di aggiungere, disattivare e verificare le fonti senza
aggiornare il software. Nessun URL di fonte va scritto nel codice (CLAUDE.md, regola 10).

Ogni fonte dichiara:

| Campo | Valori |
|---|---|
| `kind` | `data` (serie storiche), `news`, `portal` (broker, exchange, crowdfunding), `llm` |
| `categories` | prezzi, macro, tassi, volatilità, posizionamento, sentiment, eventi, notizie, immobiliare, ETF, indici, crypto, materie prime, startup, IPO, filing, portafoglio, LLM |
| `access` | `api`, `csv`, `rss`, `web`, `manual` |
| `cost` | `free`, `freemium`, `paid`, `account` |
| `reliability` | **A** ufficiale o primaria · **B** affidabile, secondaria · **C** non ufficiale, da incrociare |
| `status` | `active`, `planned`, `disabled` |

> ⚠️ Costi, limiti e termini d'uso cambiano: verificarli prima di attivare ogni fonte. Per le
> fonti `web` serve controllare che l'uso automatizzato sia consentito; in caso contrario restano
> come link manuali.

## Sintesi per categoria (stato del registro al 2026-11-06, verifiche MiCA e fiscali incluse)

| Categoria | Fonti principali | Affidabilità |
|---|---|---|
| Prezzi ed ETF | yfinance (ricerca), Stooq, EODHD (UCITS UE), Borsa Italiana | C / B / B / A |
| Macro e tassi | FRED, ECB Data Portal, Eurostat, ISTAT, Banca d'Italia | A |
| Immobiliare | ISTAT (prezzi abitazioni), OMI Agenzia Entrate, BCE (mutui), Walliance, Mamacrowd, scraper annunci personale | A / B |
| Volatilità e posizionamento | Cboe, CFTC COT, AAII | A / B |
| Materie prime e oro | World Bank Pink Sheet, LBMA, FRED | A |
| Crypto | CoinGecko, exchange via ccxt | B |
| Eventi | Fed, BCE, Polymarket | A / B |
| IPO e filing | SEC EDGAR, Nasdaq IPO calendar, Borsa Italiana, Consob | A / B |
| Startup | Mamacrowd, Crowdcube, Dealroom (a pagamento, disattivata) | B |
| Notizie | GDELT, comunicati BCE e Fed, Consob, Il Sole 24 Ore (RSS) | A / B |
| Broker (sola lettura) | Interactive Brokers (Flex Web Service), DEGIRO e Scalable Capital (CSV) | A |
| Exchange crypto (sola lettura) | Coinbase, Kraken, Bitpanda (MiCA); Binance, Bitfinex con avviso | B / C |
| Inserimento manuale e CSV generico | Per tutto ciò che non si collega | — |
| LLM (opzionali) | Anthropic, OpenAI, Ollama locale | — |

## Catalogo prodotti

`config/products.example.yaml` (ADR 0009) raccoglie TER, patrimonio, politica dei proventi,
replica e domicilio di ogni ETF/ETC classificato, con fonte e data di verifica (justETF,
trackingdifferences.com, schede emittente). Strumenti per aggiornarlo: vedi [`TOOLS.md`](TOOLS.md).

## Modelli per serie storiche (plug-in)

| Modello | Uso in DTH | Licenza |
|---|---|---|
| TimesFM 2.5 (Google) | Forecast di volatilità e quantili | Apache-2.0 |
| Chronos-2 (Amazon) | Alternativa, supporto multivariato | Apache-2.0 |
| Moirai-2 (Salesforce) | Alternativa, quantili | Verificare sul model card |
| Kronos | Specifico per dati di mercato a candele (OHLCV) | Verificare sul repository |
| `hmmlearn` | Rilevazione di regime | BSD |
| `arch` | GARCH (baseline di volatilità) | NCSA |
| FinBERT | Sentiment delle notizie | Verificare sul model card |

## Contratto di qualità

Ogni serie salvata porta con sé `source`, `fetched_at`, `as_of`, `adjusted`, `currency`. A ogni
ingestione girano i controlli (gap, salti oltre N sigma, valori negativi, duplicati) che
alimentano la *Salute delle fonti* e le regole `stale_source` e `broken_source`.

Per le notizie si conservano solo titolo, estratto, link, fonte e data: nessun archivio dei
testi completi degli articoli.
