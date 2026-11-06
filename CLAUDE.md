# CLAUDE.md — Regole operative per gli agenti

Questo file guida qualsiasi agente AI (Claude Code o altri; vedi anche `AGENTS.md`) che lavora
su DTH. Leggilo per intero prima di modificare il codice.

## Contesto in 30 secondi

DTH è un'app desktop per Windows (Tauri + sidecar Python, ADR 0003) di supporto alle decisioni
di investimento per un solo utente: dati, notizie, temi, startup, IPO, posizioni in sola lettura,
modelli per serie storiche, LLM opzionale. Il backend è Python (`backend/src/dth`), il frontend è
in `frontend/` (non ancora costruito). Il NUC è fuori perimetro (ADR 0007). Il primo
utente esterno è un tester **non tecnico**: zero configurazione, linguaggio semplice, ogni
termine tecnico spiegato in una riga. La lingua della documentazione e della UI è l'italiano;
codice, identificatori e commenti sono in inglese.

Leggi in quest'ordine: `README.md` → `docs/ARCHITECTURE.md` → `docs/VALIDATION.md` →
`docs/RISK_POLICY.md` → gli ADR in `docs/adr/` pertinenti al tuo task.

## Regole non negoziabili

1. **Nessun lookahead.** Un `Signal` usa solo dati fino alla chiusura della data *t*. Lo shift di
   esecuzione lo applica l'harness. Ogni nuovo segnale va registrato in
   `tests/test_no_lookahead.py` (lista `SIGNALS_UNDER_TEST`).
2. **Nessun modello come oracolo** (ADR 0002). Forecaster e LLM non producono pesi né ordini.
3. **Nessun ordine reale.** Non scrivere codice che invia ordini live senza un ADR accettato che
   lo autorizzi. In ogni caso, nessun agente esegue ordini.
4. **Niente segreti nel repo.** Le chiavi vanno in `.env` (escluso da git). Usa `.env.example`
   per documentare le variabili.
5. **I limiti di rischio sono codice.** Non alzare i default di `risk/limits.py` senza un ADR.
6. **Import pesanti isolati.** `torch`, `timesfm`, `chronos` e simili si importano solo dentro
   `forecast/tsfm_*.py` e in modo lazy. Il core deve installarsi senza l'extra `[tsfm]`.
7. **I provider non salvano, lo store non scarica.** Rispetta i layer di `ARCHITECTURE.md`.
8. **Il colore nasce solo da una `HighlightRule`** (ADR 0004). Nessun componente UI decide da
   solo di evidenziare qualcosa.
9. **Connettori in sola lettura, segreti nel portachiavi** (ADR 0005). Mai inviare posizioni,
   saldi o credenziali a un LLM senza consenso esplicito per richiesta.
10. **Ogni fonte passa dal registro** (`config/sources.example.yaml`): niente URL di fonti
    scritti nel codice.

## Workflow

1. Prima di scrivere codice, individua il contratto coinvolto (`DataProvider`, `Signal`,
   `Forecaster`) e i test esistenti.
2. Scrivi o aggiorna prima i test, poi l'implementazione.
3. Esegui `make check` (lint + test). Non dichiarare finito un task con check rossi.
4. Se cambi un contratto o una policy, aggiungi un ADR (`docs/adr/template.md`).
5. Aggiorna la documentazione toccata (`MODULES.md`, `DATA_SOURCES.md`, `ROADMAP.md`).
6. Commit piccoli, messaggi in stile Conventional Commits (`feat(signals): …`, `fix(store): …`).

## Definizione di "fatto"

- [ ] `make check` è verde
- [ ] I nuovi segnali passano l'harness anti-lookahead
- [ ] Nessuna dipendenza pesante nel core
- [ ] La documentazione è aggiornata
- [ ] Per i dati: fonte, `as_of` e controlli di qualità sono presenti

## Convenzioni di codice

- Python ≥ 3.11, type hint ovunque, `ruff` per lint e format (config in `backend/pyproject.toml`).
- DataFrame dei prezzi: indice `DatetimeIndex` ordinato e senza duplicati, colonne = simboli.
- Pesi: DataFrame allineato ai prezzi, valori in [-1, 1], NaN non ammessi in output (usa 0).
- Date: tz-naive, data di chiusura di borsa.
- Niente `print` nel codice di libreria: usa `logging`.
- Test: `pytest`, dati sintetici deterministici (`dth.testing.synthetic_prices`), nessuna rete.

## Frontend (quando si costruisce)

- Segui `docs/DESIGN.md` (direzione "Sala controllo in metallo liquido"): colore solo per gli stati fuori norma; effetto metallo liquido solo su banda di regime e logo.
- I tipi TypeScript si generano dallo schema OpenAPI dell'API, non si scrivono a mano.

## Comandi utili

```bash
make install    # venv + dipendenze di sviluppo
make check      # lint + test (da eseguire prima di ogni commit)
make api        # API di sviluppo con reload
make backtest   # walk-forward di esempio su dati sintetici
```
