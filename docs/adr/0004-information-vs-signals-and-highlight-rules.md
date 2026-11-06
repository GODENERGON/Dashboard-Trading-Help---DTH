# ADR 0004 — Informazione e segnali separati; il colore nasce solo da regole esplicite

- Stato: accettato
- Data: 2026-11-06

## Contesto
La dashboard deve "colorarsi quando ci sono eventi o info che ha senso considerare". Senza
regole, ogni notizia o variazione diventa un'evidenza e la dashboard si trasforma in rumore, che
spinge all'iperattività. Inoltre si aggiungono contenuti informativi (startup, IPO, notizie, temi)
che non hanno la stessa validazione delle strategie.

## Decisione
1. **Due classi di contenuto.**
   - *Informazione*: notizie, schede startup e IPO, dati di tema, forecast. Mostrata con fonte e
     data. Non produce mai pesi né ordini.
   - *Segnale*: pesi target prodotti da una strategia `validated` ([`VALIDATION.md`](../VALIDATION.md)).
2. **Il colore nasce solo da una `HighlightRule`** con: id, categoria, condizione verificabile,
   livello (`attention` = Ambra, `critical` = Colata), fonte, cooldown e scadenza.
3. Ogni elemento colorato mostra, con un clic, **quale regola l'ha acceso, su quali dati e
   quando**.
4. Le regole sono in un file di configurazione modificabile dall'utente
   (`config/highlights.example.yaml`); le regole di rischio di [`RISK_POLICY.md`](../RISK_POLICY.md)
   sono sempre attive e non disattivabili.
5. Un LLM può **proporre** una regola o riassumere perché una notizia è rilevante, ma non
   accende direttamente un'evidenza.
6. Budget di attenzione: se più di 5 evidenze sono attive contemporaneamente, si mostrano le più
   gravi e le altre restano in una coda, per evitare l'effetto albero di Natale.

## Conseguenze
La dashboard resta leggibile e ogni colore è spiegabile. Le regole diventano un oggetto di primo
livello, testato come i segnali.
