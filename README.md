# DTH — Dashboard Trading Help

> Il punto focale di tutte le informazioni rilevanti per decidere *se, cosa e quanto* tradare.
> Non un oracolo: un cruscotto di contesto, rischio e strategie validate.

DTH è un'**applicazione desktop per Windows** (Tauri + backend Python incluso) che riunisce dati
di mercato, macro, notizie, temi (immobiliare, ETF, indici, crypto, materie prime), startup, IPO
e posizioni dei portali di trading in una dashboard unica. Usa modelli per serie storiche
(TimesFM, Chronos, Kronos…) come strumenti di contesto, un LLM opzionale con l'account
dell'utente, e **si colora solo quando una regola esplicita trova qualcosa da considerare**.

## Principi non negoziabili

1. **Nessun modello è un oracolo.** LLM e modelli per serie storiche (TimesFM, Chronos…) sono
   *strumenti di ricerca e di contesto*, non generatori di segnali. Entrano nel sistema solo se
   battono una baseline semplice in walk-forward.
2. **Il rischio viene prima del rendimento.** Dimensionamento, drawdown massimo, esposizione:
   sono la parte centrale della dashboard, non un'appendice.
3. **Niente lookahead, niente overfitting.** Ogni segnale passa l'harness anti-lookahead e una
   validazione walk-forward con costi realistici prima di comparire in UI.
4. **Dati prima dei modelli.** Qualità, freschezza e tracciabilità del dato sono monitorate e
   visibili.
5. **Paper prima del live.** L'esecuzione automatica è l'ultima milestone, dietro gate espliciti
   (vedi [`docs/RISK_POLICY.md`](docs/RISK_POLICY.md)). I connettori ai portali sono in sola lettura.
6. **Informazione ≠ segnale.** Notizie, startup, IPO e forecast informano; solo le strategie
   validate producono pesi. Ogni colore in UI è spiegato dalla regola che l'ha acceso.

## Mappa della documentazione

| Documento | Contenuto |
|---|---|
| [`docs/VISION.md`](docs/VISION.md) | Perché esiste, per chi, cosa non è |
| [`docs/MODULES.md`](docs/MODULES.md) | Catalogo dei pannelli/informazioni della dashboard |
| [`docs/DATA_SOURCES.md`](docs/DATA_SOURCES.md) | Fonti dati, costi, limiti, licenze |
| [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) | Architettura, flussi, contratti tra i layer |
| [`docs/VALIDATION.md`](docs/VALIDATION.md) | Come si valida un segnale (harness walk-forward) |
| [`docs/RISK_POLICY.md`](docs/RISK_POLICY.md) | Guardrail su rischio ed esecuzione |
| [`docs/DESIGN.md`](docs/DESIGN.md) | Direzione visiva "financial-tech" |
| [`docs/ROADMAP.md`](docs/ROADMAP.md) | Milestone e criteri di uscita |
| [`docs/OPEN_QUESTIONS.md`](docs/OPEN_QUESTIONS.md) | Decisioni aperte prima della costruzione |
| [`docs/adr/`](docs/adr/) | Architecture Decision Records |
| [`CLAUDE.md`](CLAUDE.md) | Regole operative per gli agenti AI che lavorano sul repo |

## Struttura del repository

```
backend/            Pacchetto Python `dth` (API, ingestione, segnali, backtest, rischio)
  src/dth/
    core/           Config, tipi di dominio
    providers/      Adattatori fonti dati (contratto DataProvider)
    store/          Persistenza (DuckDB + Parquet)
    signals/        Segnali (contratto Signal, no-lookahead)
    forecast/       Forecaster (baseline + adattatori TSFM opzionali)
    backtest/       Harness walk-forward e metriche
    risk/           Sizing e limiti di rischio
    alerts/         Notifiche (Telegram)
    api/            FastAPI
  tests/            Test unitari + harness anti-lookahead
frontend/           App desktop Tauri + React (da costruire, vedi docs/DESIGN.md)
config/             Universo, registro fonti, regole di evidenza, alert (esempi)
docs/               Documentazione di progetto
```

## Avvio rapido (sviluppo)

```bash
make install        # crea venv e installa backend in modalità sviluppo
make test           # test + harness anti-lookahead
make lint           # ruff
make api            # avvia l'API su http://localhost:8000 (docs su /docs)
make backtest       # esegue un walk-forward di esempio su dati sintetici
```

Installer Windows: dalla milestone M2 (vedi [`docs/ROADMAP.md`](docs/ROADMAP.md)).
Backend opzionale sul NUC: `docker compose up -d`.

## Stato

**Fase 0 — Harness.** Documentazione, contratti, test harness e scaffold sono pronti.
L'applicativo (UI e pannelli) non è ancora costruito: prima vanno chiuse le decisioni in
[`docs/OPEN_QUESTIONS.md`](docs/OPEN_QUESTIONS.md).

## Disclaimer

Software di ricerca personale. Nulla di ciò che produce costituisce consulenza finanziaria.
Il trading comporta il rischio di perdere capitale.
