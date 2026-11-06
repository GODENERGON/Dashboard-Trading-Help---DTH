# DTH — Dashboard Trading Help

> Il punto focale di tutte le informazioni rilevanti per decidere *se, cosa e quanto* tradare.
> Non un oracolo: un cruscotto di contesto, rischio e strategie validate.

DTH è un'**applicazione desktop per Windows** (Tauri + backend Python incluso) che riunisce dati
di mercato, macro, notizie, temi (immobiliare, ETF, indici, crypto, materie prime), startup, IPO
e posizioni dei portali di trading in una dashboard unica. Usa modelli per serie storiche
(TimesFM, Chronos, Kronos…) come strumenti di contesto, un LLM opzionale con l'account
dell'utente, e **si colora solo quando una regola esplicita trova qualcosa da considerare**.

## Installazione su Windows

> La prima versione installabile arriverà con la milestone M1 (vedi [`docs/ROADMAP.md`](docs/ROADMAP.md)).
> Questa guida vale da quel momento. Serve Windows 10 o 11 a 64 bit; non serve installare altro.

### 1. Scarica l'installer

1. Apri la pagina [Releases](https://github.com/GODENERGON/Dashboard-Trading-Help---DTH/releases).
2. Nell'ultima versione, sotto **Assets**, scarica il file che finisce con **`.msi`**
   (per esempio `DTH_0.1.0_x64_it-IT.msi`).

Il browser potrebbe avvisarti che il file "non viene scaricato comunemente". È normale per
un'app nuova e senza certificato.
- **Edge:** passa il mouse sul download, clicca sui tre puntini **…** → **Mantieni** →
  **Mostra altro** → **Mantieni comunque**.
- **Chrome:** clicca **Mantieni** (o **Scarica comunque**) nell'avviso del download.

### 2. Avvia l'installazione e supera l'avviso di Windows

1. Fai doppio clic sul file `.msi` scaricato.
2. Comparirà una finestra blu **"Windows ha protetto il PC"**. Succede perché l'app non ha
   ancora un certificato di firma a pagamento, non perché sia pericolosa.
3. Clicca **Ulteriori informazioni** (il link sotto il testo).
4. Clicca **Esegui comunque**.
5. Se Windows chiede **"Vuoi consentire a questa app di apportare modifiche?"**, clicca **Sì**.
6. Segui l'installazione con **Avanti** fino a **Fine**.

DTH compare nel menu Start e, se l'hai scelto, sul desktop.

### Se Windows blocca l'app senza il pulsante "Esegui comunque"

Su alcuni PC con Windows 11 è attivo **Smart App Control**, che blocca le app senza firma e non
offre il pulsante per proseguire. In quel caso:
1. Apri **Impostazioni** → **Privacy e sicurezza** → **Sicurezza di Windows** →
   **Controllo app e browser**.
2. Apri **Impostazioni di Smart App Control** e scegli **Disattivato**.
3. Ripeti il passo 2.

⚠️ Su alcune versioni di Windows, Smart App Control non si può riattivare senza reinstallare il
sistema. Se preferisci non disattivarlo, scrivimi: aspettiamo la versione firmata.

### Primo avvio, aggiornamenti, disinstallazione

- Al primo avvio una breve guida in tre passi ti chiede quali temi ti interessano. Non servono
  account né chiavi: l'app parte con le fonti gratuite.
- Gli aggiornamenti arrivano da soli: quando c'è una nuova versione, l'app chiede se installarla.
- Per lasciare un commento usa il pulsante **Invia feedback** in basso a sinistra.
- Per disinstallare: **Impostazioni** → **App** → **App installate** → **DTH** → **Disinstalla**.
  I dati restano nella cartella `%LOCALAPPDATA%\DTH`, che puoi cancellare a mano.

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
| [`docs/DESIGN.md`](docs/DESIGN.md) | Direzione visiva "sala controllo in metallo liquido" |
| [`docs/PRODUCTS.md`](docs/PRODUCTS.md) | Classifica prodotti per caratteristiche e portafogli modello |
| [`docs/TOOLS.md`](docs/TOOLS.md) | Strumenti open source valutati |
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
    alerts/         Notifiche
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
# studio su dati reali (serve internet): python -m dth.cli ucits-trend
# oppure da GitHub: Actions → research → Run workflow
```

`docker-compose.yml` serve solo per lo sviluppo (il NUC è fuori perimetro, ADR 0007).

## Stato

**Fase 0 — Harness** completata. Strategie testate su dati reali, nessuna validata al netto
delle tasse finora: [trend multi-asset](docs/research/2026-11-06-ucits-trend.md),
[core-satellite e regime](docs/research/2026-11-06-core-satellite-results.md) (pre-registrati). L'applicativo (UI e pannelli) non è ancora costruito. Prossimo passo: la prima build
installabile per un tester (milestone M1).

## Disclaimer

Software sperimentale. Nulla di ciò che produce costituisce consulenza finanziaria.
Il trading comporta il rischio di perdere capitale.
