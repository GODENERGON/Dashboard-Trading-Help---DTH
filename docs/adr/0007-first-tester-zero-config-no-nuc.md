# ADR 0007 — Prima distribuzione a un tester non tecnico; NUC fuori perimetro

- Stato: accettato (modifica parzialmente ADR 0003 per la parte NUC)
- Data: 2026-11-06

## Contesto
Il primo obiettivo concreto è dare l'app a un amico con un PC Windows, **senza esperienza con
strumenti del genere**, per raccogliere feedback. Il NUC per ora non si usa.

## Decisione
1. **NUC fuori perimetro.** Niente backend remoto né job notturni: tutto gira nell'app, sul PC.
   `docker-compose.yml` resta nel repo solo per lo sviluppo e non è documentato agli utenti.
2. **Zero configurazione al primo avvio.** L'app funziona subito con le sole fonti gratuite e
   senza chiave: niente account, niente file da modificare, niente terminale.
3. **Primo avvio guidato** in 3 passi: cosa fa l'app (e cosa non fa), quali temi interessano,
   avviso "non è consulenza finanziaria". Le impostazioni avanzate (LLM, connettori) restano
   nascoste finché l'utente non le cerca.
4. **Linguaggio da non addetti**: ogni termine tecnico (drawdown, Sharpe, VIX…) ha una
   spiegazione in una riga al passaggio del mouse.
5. **Feedback dall'app**: pulsante "Invia feedback" sempre visibile, che apre una breve scheda
   (cosa stavi facendo, cosa ti aspettavi, voto 1-5) e prepara un'email con allegato un file
   diagnostico (versione, log degli ultimi giorni, nessun dato personale né chiave).
6. **Distribuzione**: installer `.msi` pubblicato su GitHub Releases (repository pubblico), con
   istruzioni di installazione nel README. Nessun certificato di firma in questa fase: l'avviso
   SmartScreen è documentato.
7. **Aggiornamenti automatici** attivi fin dalla prima build, così il tester riceve le correzioni
   senza reinstallare.
8. **Dati del tester solo locali**: nessuna telemetria automatica; il feedback parte solo quando
   lo invia lui.

## Conseguenze
- La prima build punta a una "fetta verticale" piccola ma completa e installabile, invece che a
  tutte le funzioni del backend (vedi [`ROADMAP.md`](../ROADMAP.md)).
- Il NUC si potrà riaprire con un nuovo ADR.
