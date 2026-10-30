# ADR 0002 — I modelli non sono oracoli

- Stato: accettato
- Data: 2026-10-30

## Contesto
I modelli foundation per serie storiche (TimesFM, Chronos, Moirai) e gli LLM sono attraenti, ma
la letteratura indipendente mostra che, in zero-shot, prevedono male i rendimenti giornalieri e
sono battuti da baseline ben costruite. Sono più utili per la volatilità e l'incertezza.

## Decisione
1. Nessun forecaster o LLM genera direttamente pesi o ordini.
2. I forecaster stanno dietro il contratto `Forecaster` e l'extra opzionale `[tsfm]`.
3. Un forecaster si attiva solo con skill score > 0 vs baseline in walk-forward
   ([`VALIDATION.md`](../VALIDATION.md)) e si disattiva da solo se lo skill scende sotto zero.
4. In UI i forecast compaiono come bande di incertezza, mai come target di prezzo.

## Conseguenze
La dashboard resta credibile e la complessità ML entra solo dove dimostra valore.
