# Vision

## Il problema

Le informazioni utili per decidere un investimento sono sparse: grafici su una piattaforma, macro
su FRED, notizie su dieci siti, startup su Dealroom, IPO su un calendario, posizioni su tre
broker diversi, il rischio in un foglio Excel. Il risultato: decisioni prese su un frammento del
quadro e, peggio, guidate dall'emotività del momento.

## La risposta

DTH è **un'applicazione desktop per Windows**, installabile, che riunisce in un solo posto dati,
notizie, modelli di analisi delle serie storiche e posizioni. È costruita come una sala controllo:
**resta calma quando non succede nulla e si colora solo quando c'è qualcosa che ha senso
considerare** (vedi [ADR 0004](adr/0004-information-vs-signals-and-highlight-rules.md)).

Ogni giorno risponde a sei domande:

1. **Che regime di mercato c'è?** Trend, volatilità, condizioni finanziarie, breadth.
2. **Cosa dicono le strategie validate?** Segnali che hanno passato la validazione fuori campione.
3. **Quanto rischio sto portando, su tutte le piattaforme?** Esposizione aggregata, drawdown,
   valuta, concentrazione.
4. **Cosa sta per succedere?** Banche centrali, dati macro, trimestrali, IPO, dividendi.
5. **Cosa succede nei temi che seguo?** Immobiliare, ETF, indici, crypto, materie prime, startup
   per settore e area geografica.
6. **C'è qualcosa di anomalo?** Regole di evidenza su dati, rischio, eventi e notizie.

## Per chi

- **Utente principale:** un investitore retail sistematico residente in Italia, che opera su ETF
  UCITS, azioni e in parte crypto, con orizzonte da settimane ad anni, interessato anche a
  immobiliare e startup, e che vuole disciplina più che "segnali caldi".
- **Primo tester:** una persona con un PC Windows e **nessuna esperienza** con strumenti del
  genere ([ADR 0007](adr/0007-first-tester-zero-config-no-nuc.md)). Se lui riesce a installarla,
  capirla e usarla senza aiuto, l'app è sulla strada giusta.

Ogni installazione serve un solo utente e tiene i dati solo sul suo PC.

## Due tipi di contenuto, tenuti separati

| | Informazione | Segnale |
|---|---|---|
| Esempi | Notizie, schede startup, IPO, temi, dati macro, forecast dei modelli | Pesi target di una strategia |
| Chi decide | L'utente | La strategia validata, con conferma dell'utente |
| Requisito | Fonte e data visibili | Scheda di validazione walk-forward ([`VALIDATION.md`](VALIDATION.md)) |

## Cosa NON è

- Non è un sistema di previsione dei prezzi: i forecast compaiono come **bande di incertezza**,
  mai come "il prezzo andrà a X".
- Non è una piattaforma di day-trading né un sostituto del broker: i connettori ai portali sono
  **in sola lettura** ([ADR 0005](adr/0005-read-only-connectors-and-secrets.md)).
- Non è un prodotto per forex o CFD (esclusi per i tassi di perdita documentati dei retail).
- Non è un consulente: niente "compra/vendi" senza contesto, fonti e metriche.

## Criteri di successo

- Il tempo per una decisione informata scende da "giro di 6 siti" a meno di 5 minuti.
- Ogni numero e ogni notizia in UI ha fonte, timestamp e stato di aggiornamento visibili.
- Ogni evidenziazione colorata è riconducibile a una regola esplicita, consultabile con un clic.
- Ogni segnale mostrato ha una scheda di validazione.
- L'app funziona anche senza un account LLM e senza fonti a pagamento.
- Un utente non tecnico la installa da solo seguendo il README e capisce la Panoramica senza
  spiegazioni.
