# Pre-registrazione — Allocazioni con skfolio contro il bilanciato statico (2026-11-06)

Pubblicato **prima** dell'esecuzione. Parametri e criteri non cambiano dopo i risultati.

## Ipotesi
Un'allocazione costruita con metodi di diversificazione robusti di skfolio (Hierarchical Risk
Parity e Risk Budgeting a rischio uguale), ricalcolata una volta l'anno, ottiene al netto delle
tasse uno Sharpe migliore del portafoglio modello *bilanciato* statico, senza aumentare il
turnover in modo da annullare il vantaggio.

## Dati e regole
- Pannello EUR dello studio UCITS (stessi dati e proxy), strumenti rischiosi: azioni mondo
  (SWDA, con CSSPX prima della sua quotazione), Europa (MEUD), emergenti (EIMI), titoli di Stato
  (IBGL), oro (SGLD), immobiliare (IWDP).
- **Benchmark**: bilanciato statico 55% azioni mondo, 35% titoli di Stato, 10% oro,
  ribilanciamento annuale.
- **Modelli skfolio**: `HierarchicalRiskParity()` e `RiskBudgeting()` con parametri di default,
  stimati alla fine di ogni anno sui rendimenti giornalieri dei 3 anni precedenti; pesi tenuti
  per l'anno successivo; nessun peso > 25% sulle azioni di una singola area salvo azioni mondo
  (tetto 60%).
- Simulatore con costi 10 bps, esecuzione alla chiusura successiva, tasse italiane come negli
  studi precedenti; periodo dal primo anno con 3 anni di storia per tutti gli strumenti.

## Criteri di successo (per ciascun modello, contro il bilanciato statico)
1. Sharpe netto ≥ bilanciato + 0,05;
2. CAGR netto ≥ bilanciato − 0,50 punti;
3. max drawdown non peggiore di 2 punti.

Se un modello soddisfa tutti e tre i criteri diventa candidato per i portafogli modello
(sostituendo i pesi fissi); altrimenti i portafogli modello restano statici.
