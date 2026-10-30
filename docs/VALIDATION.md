# Validazione dei segnali

Nessun segnale arriva in UI senza un `ValidationReport` che soddisfi i criteri qui sotto.

## Pipeline

1. **Test anti-lookahead** (automatico, in CI): si alterano i prezzi dopo la data *t* e si verifica
   che l'output del segnale fino a *t* sia identico. Se cambia, il segnale "vede il futuro".
2. **Walk-forward**: finestre di test consecutive e non sovrapposte. I parametri, se ottimizzati,
   si scelgono solo sulla finestra di train precedente.
3. **Costi realistici**: commissioni + spread + slippage (default 10 bps per lato sugli ETF UCITS
   liquidi; da calibrare sulle commissioni reali del broker).
4. **Confronto con le baseline**: buy & hold dell'indice di riferimento e un 60/40 semplice.
5. **Robustezza dei parametri**: sweep su una griglia; si richiede un *plateau*, non un picco
   isolato. Si riporta la mediana della griglia, non il migliore.
6. **Test di significatività** (P1): Deflated Sharpe Ratio (corregge per il numero di prove) e
   bootstrap a blocchi dell'equity curve.

## Criteri minimi per lo stato `validated`

| Metrica (fuori campione) | Soglia |
|---|---|
| Periodo coperto | ≥ 10 anni, inclusi almeno 2 bear market |
| Sharpe netto vs benchmark | ≥ benchmark, oppure Sharpe simile con max DD inferiore di almeno il 30% |
| Max drawdown | ≤ limite di [`RISK_POLICY.md`](RISK_POLICY.md) |
| Plateau dei parametri | ≥ 60% della griglia con Sharpe > 0 |
| Turnover | Compatibile con i costi (gli ETF in Italia hanno un trattamento fiscale specifico: vedi le questioni aperte) |

## Forecaster (TSFM)

Un forecaster entra nel sistema solo se il suo **skill score** in walk-forward è > 0 rispetto
alla baseline del suo compito:
- forecast di volatilità → baseline EWMA o GARCH(1,1), metrica QLIKE;
- forecast dei quantili → baseline con quantili storici rolling, metrica pinball loss.

Lo skill score è mostrato in UI accanto al modello. Se scende sotto zero nell'ultima finestra,
il modello si disattiva automaticamente.
