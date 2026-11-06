# Architettura

## Vista d'insieme ([ADR 0003](adr/0003-windows-desktop-app-with-tauri.md))

```
┌──────────────────────────── App Dabitur (Windows, installer .msi) ────────────────────────────┐
│                                                                                           │
│  ┌──────────────── Shell Tauri ────────────────┐      ┌──────── Sidecar Python `dth` ────────┐ │
│  │  UI React + TS (design "Sala controllo")    │ HTTP │  api/  FastAPI su 127.0.0.1 + token  │ │
│  │  tab: Panoramica · Temi · Startup · IPO ·   │◀────▶│                                       │ │
│  │  Materie prime · Confronti · Portafoglio ·  │      │  connectors/  registro fonti          │ │
│  │  Fonti · Impostazioni                       │      │  providers/   dati    news/  notizie  │ │
│  │  portachiavi Windows (segreti)              │      │  store/       DuckDB + Parquet        │ │
│  └─────────────────────────────────────────────┘      │  signals/  backtest/  risk/           │ │
│                                                       │  forecast/ (plug-in TSFM scaricabili) │ │
│                                                       │  highlights/ regole di evidenza       │ │
│                                                       │  llm/  provider opzionale             │ │
│                                                       │  jobs/ aggiornamenti pianificati      │ │
│                                                       └──────────────┬────────────────────────┘ │
└──────────────────────────────────────────────────────────────────────┼──────────────────────────┘
                                                                       │
          Fonti dati e notizie (registro aggiornabile) · Broker/exchange in sola lettura · LLM utente
```

Tutto gira sul PC dell'utente: il NUC è fuori perimetro ([ADR 0007](adr/0007-first-tester-zero-config-no-nuc.md)).

Dati utente in `%LOCALAPPDATA%\Dabitur\`: `lake/` (Parquet), `dth.duckdb`, `config/`, `logs/`, `models/`.

## Layer e contratti

### `connectors/` — registro fonti
- Il **registro fonti** (`config/sources.example.yaml`, schema in `dth.core.sources`) elenca ogni
  fonte con tipo (`data`, `news`, `portal`, `llm`), categorie, accesso, costo, autenticazione,
  affidabilità e stato. L'utente può aggiungere, disattivare e riordinare le fonti dalla tab
  *Fonti*; gli aggiornamenti del registro non richiedono una nuova versione dell'app.
- Ogni fonte attiva è collegata a un adattatore: `DataProvider` (serie storiche), `NewsProvider`
  (notizie) o `PortalConnector` (saldi e posizioni, sola lettura).

### `providers/` — `DataProvider`
```python
class DataProvider(Protocol):
    name: str
    def fetch(self, symbol: str, start: date, end: date) -> pd.DataFrame: ...
```
- DataFrame indicizzato per date di chiusura tz-naive, colonne canoniche
  (`open, high, low, close, volume` per i prezzi; `value` per le serie macro).
- Prezzi aggiustati per split e dividendi, salvo indicazione contraria nei metadati.
- Non salva nulla: la persistenza è compito di `store/`.

### `news/` — `NewsProvider` (M2)
```python
class NewsProvider(Protocol):
    name: str
    def fetch(self, since: datetime, topics: list[str]) -> list[NewsItem]: ...
```
- `NewsItem`: titolo, link, fonte, data di pubblicazione, lingua, entità e temi collegati. Il
  testo completo degli articoli non si archivia: si conservano titolo, estratto e link.

### `connectors/portals` — `PortalConnector` (M4, [ADR 0005](adr/0005-read-only-connectors-and-secrets.md))
```python
class PortalConnector(Protocol):
    name: str
    def balances(self) -> list[Balance]: ...
    def positions(self) -> list[Position]: ...
```
- Nessun metodo per inviare ordini. Credenziali dal portachiavi di Windows.

### `store/` — persistenza
- DuckDB come motore di query, Parquet su disco (`lake/<dataset>/<symbol>.parquet`).
- Ogni scrittura registra i metadati (`source`, `fetched_at`, `as_of`).
- Le letture accettano un `as_of` per riprodurre lo stato dei dati a una certa data.

### `signals/` — `Signal`
```python
class Signal(Protocol):
    name: str
    def compute(self, prices: pd.DataFrame) -> pd.DataFrame: ...
```
- Output: pesi target in [-1, 1] calcolati solo con informazioni disponibili alla chiusura di
  quella data. Lo shift di esecuzione lo applica l'harness.
- Ogni segnale deve passare `tests/test_no_lookahead.py`.

### `forecast/` — `Forecaster` e plug-in di modelli
```python
class Forecaster(Protocol):
    name: str
    def forecast(self, history: np.ndarray, horizon: int) -> ForecastResult: ...
```
- Baseline sempre incluse (EWMA, quantili storici). I modelli foundation (TimesFM 2.5,
  Chronos-2, Moirai-2, Kronos) sono **plug-in** scaricati su richiesta in `models/`.
- La tab *Modelli* mostra per ciascuno lo skill score vs baseline in walk-forward; un modello con
  skill ≤ 0 si nasconde da solo ([ADR 0002](adr/0002-models-are-not-oracles.md)).

### `highlights/` — regole di evidenza ([ADR 0004](adr/0004-information-vs-signals-and-highlight-rules.md))
```python
class HighlightRule(Protocol):
    id: str
    level: Literal["attention", "critical"]
    def evaluate(self, ctx: Context) -> Highlight | None: ...
```
- Ogni `Highlight` porta con sé regola, dati usati, timestamp e scadenza: è ciò che la UI mostra
  quando l'utente chiede "perché è colorato?".

### `llm/` — provider opzionale
- Interfaccia unica per Anthropic, OpenAI e Ollama (locale). Usi: riassunti delle notizie, schede
  aziende e IPO, domande in linguaggio naturale sui dati, proposte di regole.
- Senza chiave configurata, le funzioni LLM sono nascoste e il resto dell'app funziona.

### `backtest/`, `risk/`
- Invariati: walk-forward con costi, metriche, limiti di policy come codice testato.

### `api/`
- FastAPI su `127.0.0.1`, porta assegnata da Tauri all'avvio, header `X-DTH-Token` obbligatorio.
- Sola lettura verso l'esterno; le scritture riguardano solo configurazione locale (fonti,
  watchlist, regole, journal).
- OpenAPI su `/docs`: i tipi TypeScript si generano dallo schema.

## Scelte tecnologiche

| Area | Scelta | Motivo |
|---|---|---|
| Shell desktop | Tauri 2 (WebView2) | Installer leggero, aggiornamenti firmati, sidecar nativo |
| UI | Vite + React + TypeScript | Ecosistema dei grafici più ricco |
| Grafici | `lightweight-charts` (prezzi), D3 (banda di regime, confronti custom) | |
| Backend | Python ≥ 3.11, FastAPI, pandas, DuckDB, Parquet | Ecosistema quant e ML |
| Impacchettamento backend | PyInstaller → eseguibile sidecar | Nessun Python richiesto all'utente |
| Segreti | Credential Manager di Windows via `keyring` | Fuori da file e log |
| Scheduling | APScheduler nel sidecar: aggiornamenti all'avvio e periodici mentre l'app è aperta | |

## Build e distribuzione

- `make test` / `make check`: backend su Linux (CI attuale).
- CI Windows (M2): build del sidecar con PyInstaller, build Tauri, artefatto `.msi`.
- Aggiornamenti: updater di Tauri con manifest firmato su GitHub Releases.

- Distribuzione: installer `.msi` su GitHub Releases, senza certificato di firma in questa fase
  (istruzioni per superare SmartScreen nel README).

## Feedback e diagnostica ([ADR 0007](adr/0007-first-tester-zero-config-no-nuc.md))

- Log a rotazione in `%LOCALAPPDATA%\Dabitur\logs\` (7 giorni), senza chiavi né importi.
- "Invia feedback" crea un pacchetto diagnostico (versione, sistema operativo, log, stato delle
  fonti) e apre un'email precompilata. Nessuna telemetria automatica.

## Sviluppo

`docker compose up -d` avvia il backend in un container per lo sviluppo e i test: non è un
canale di distribuzione.
