# Architettura

## Vista d'insieme

```
            ┌──────────────┐  schedule   ┌──────────────┐
 Fonti ───▶ │  providers/  │ ──────────▶ │   store/     │  DuckDB + Parquet
 esterne    │ DataProvider │  (jobs/)    │ (data/lake)  │  (sul NUC)
            └──────────────┘             └──────┬───────┘
                                                │ letture versionate
                 ┌──────────────────────────────┼─────────────────────────────┐
                 ▼                              ▼                             ▼
          ┌────────────┐               ┌──────────────┐              ┌──────────────┐
          │ signals/   │──────────────▶│  backtest/   │              │  forecast/   │
          │  Signal    │  validazione  │ walk-forward │◀─────────────│  Forecaster  │
          └─────┬──────┘               └──────┬───────┘   confronto   └──────────────┘
                │                             │          vs baseline
                ▼                             ▼
          ┌────────────┐               ┌──────────────┐
          │  risk/     │               │  validation  │  report persistiti
          │  sizing    │               │   reports    │
          └─────┬──────┘               └──────┬───────┘
                └──────────────┬──────────────┘
                               ▼
                        ┌────────────┐        ┌────────────┐
                        │   api/     │───────▶│ frontend/  │
                        │  FastAPI   │        │ dashboard  │
                        └─────┬──────┘        └────────────┘
                              ▼
                        ┌────────────┐
                        │  alerts/   │──▶ Telegram
                        └────────────┘
```

## Layer e contratti

### `providers/` — `DataProvider`
```python
class DataProvider(Protocol):
    name: str
    def fetch(self, symbol: str, start: date, end: date) -> pd.DataFrame: ...
```
- Restituisce un DataFrame con indice `DatetimeIndex` (tz-naive, data di chiusura) e colonne
  canoniche (`open, high, low, close, volume` per i prezzi; `value` per le serie macro).
- Prezzi **aggiustati** per split e dividendi, salvo indicazione contraria nei metadati.
- Non salva nulla: la persistenza è compito di `store/`.

### `store/` — persistenza
- DuckDB come motore di query, Parquet come formato su disco (`data/lake/<dataset>/<symbol>.parquet`).
- Ogni scrittura registra i metadati (`source`, `fetched_at`, `as_of`).
- Le letture accettano un `as_of` per riprodurre lo stato dei dati a una certa data
  (evita il lookahead da revisioni dei dati, rilevante per le serie macro).

### `signals/` — `Signal`
```python
class Signal(Protocol):
    name: str
    def compute(self, prices: pd.DataFrame) -> pd.DataFrame: ...
```
- Input: prezzi di chiusura (colonne = simboli). Output: **pesi target** in [-1, 1] per data e
  simbolo, calcolati **solo con informazioni disponibili alla chiusura di quella data**.
- L'esecuzione avviene alla barra successiva: lo shift lo applica l'harness, non il segnale.
- Ogni segnale deve passare `tests/test_no_lookahead.py` (perturbazione del futuro → output
  passato invariato).

### `forecast/` — `Forecaster`
```python
class Forecaster(Protocol):
    name: str
    def forecast(self, history: pd.Series, horizon: int) -> ForecastResult: ...
```
- `ForecastResult` contiene la previsione puntuale e i quantili (es. 0.1/0.5/0.9).
- Le implementazioni pesanti (TimesFM, Chronos) stanno dietro l'extra opzionale `[tsfm]` e non
  vengono mai importate dai moduli core.

### `backtest/` — harness
- `walk_forward(signal, prices, config)`: finestre rolling o espanse di train e test; il segnale
  vede solo il passato; costi di transazione e slippage in punti base; ribilanciamento periodico.
- `metrics.py`: CAGR, volatilità, Sharpe, Sortino, max drawdown, Calmar, turnover, hit rate.
- Output: `ValidationReport` serializzabile (JSON) che la UI mostra come scheda di validazione.

### `risk/`
- Volatility targeting, limite di esposizione per singolo strumento e totale, stop basati su ATR.
- I limiti di policy ([`RISK_POLICY.md`](RISK_POLICY.md)) sono codice testato, non testo.

### `api/`
- FastAPI, sola lettura nella Fase 1. Endpoint principali: `/health`, `/universe`,
  `/prices/{symbol}`, `/signals`, `/validation/{signal}`, `/risk`, `/data-health`.
- OpenAPI su `/docs`: il frontend genera i tipi TypeScript dallo schema.

### `alerts/`
- Regole YAML → notifiche Telegram, con cooldown per evitare lo spam.

## Scelte tecnologiche

| Area | Scelta | Motivo |
|---|---|---|
| Linguaggio backend | Python ≥ 3.11 | Ecosistema quant e ML |
| Dati | pandas, DuckDB, Parquet | Semplice, veloce, zero server DB |
| API | FastAPI + pydantic | Tipi, OpenAPI, asincrono |
| Scheduling | APScheduler (in-process) | Basta per un nodo singolo |
| Frontend | Da confermare (vedi [`OPEN_QUESTIONS.md`](OPEN_QUESTIONS.md)) — proposta: Vite + React + TS, `lightweight-charts`, D3 per le viste custom | |
| Deploy | Docker Compose sul NUC | Già il pattern dell'infrastruttura di casa |

## Deploy

```
docker compose up -d           # api + scheduler
docker compose logs -f api
```
Volumi: `./data` (lake Parquet + DuckDB), `./config` (universo e regole di alert).
Accesso solo da LAN o tramite VPN/Tailscale: **nessuna esposizione pubblica** dell'API.
