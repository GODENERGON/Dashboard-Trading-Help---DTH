# ADR 0005 — Connettori in sola lettura e segreti nel portachiavi di sistema

- Stato: accettato
- Data: 2026-11-06

## Contesto
L'app si collega a broker, exchange crypto, piattaforme di crowdfunding e a un LLM con l'account
dell'utente. Sono credenziali che danno accesso a denaro e a dati personali.

## Decisione
1. **Sola lettura.** I connettori ai portali di trading leggono saldi, posizioni e movimenti. Le
   chiavi API si creano, dove il portale lo consente, con permessi di sola lettura e senza
   prelievo. L'invio di ordini resta escluso finché un ADR non lo autorizza ([`RISK_POLICY.md`](../RISK_POLICY.md)).
2. **Segreti nel portachiavi di Windows** (Credential Manager, tramite `keyring` lato Python), mai
   in file di configurazione, log o database. Il file `.env` resta solo per lo sviluppo.
3. **LLM opzionale, con la chiave dell'utente** (Anthropic, OpenAI o modello locale tramite
   Ollama). Si inviano al provider solo i testi necessari (notizie, domande): **mai posizioni,
   saldi o credenziali**, salvo consenso esplicito per singola richiesta.
4. Ogni connettore dichiara nel registro fonti: permessi richiesti, dati letti, frequenza.

## Conseguenze
Un furto della configurazione o un errore di un agente non può muovere denaro. Le funzioni LLM
degradano con eleganza quando la chiave non c'è.
