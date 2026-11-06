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
7. **Al netto delle imposte** (M2, [ADR 0008](adr/0008-accounts-brokers-and-tax-ledger.md)):
   il backtest applica le regole di `config/tax.it.example.yaml` per categoria fiscale. Per gli
   ETF le plusvalenze sono tassate a ogni vendita e le minusvalenze non le compensano: una
   strategia con molto turnover può essere buona al lordo e mediocre al netto. Si riportano
   entrambe le versioni; lo stato `validated` si decide sul netto.

## Due motori di backtest

| | Motore veloce (`backtest/engine.py`) | Simulatore di portafoglio (`backtest/portfolio.py`) |
|---|---|---|
| Uso | Walk-forward e griglie di ricerca | Report di validazione, confronto con i benchmark |
| Esecuzione | Alla chiusura della decisione | Alla chiusura **successiva** (più prudente) |
| Pesi | Ribilanciati ogni giorno tra le date di decisione | Derivano con i prezzi tra un ribilanciamento e l'altro |
| Tasse | No | Sì (regole di `config/tax.it.example.yaml`) |
| Extra | — | Banda di non-ribilanciamento, valore di liquidazione netto |

Semplificazioni fiscali del simulatore: tasse saldate l'ultimo giorno di borsa dell'anno (nella
realtà a giugno), costo medio ponderato, riduzione al 48,08% delle minusvalenze su titoli di Stato
ignorata, IVAFE 0,2% su tutto il detenuto a fine anno.

## Studi eseguiti

| Data | Strategia | Esito | Documento |
|---|---|---|---|
| 2026-11-06 | Trend multi-asset UCITS (`MultiAssetTrend`) | `research`: protegge nei crolli ma al netto delle tasse rende meno di un 60/40 | [studio](research/2026-11-06-ucits-trend.md) |
| 2026-11-06 | Core-satellite 70/30 (`CoreSatellite`), pre-registrato | `research`: drawdown −23% vs −32%, ma CAGR e Sharpe netti sotto il 60/40 | [pre-registrazione](research/2026-11-06-preregistration-core-satellite-and-regime.md), [esito](research/2026-11-06-core-satellite-results.md) |
| 2026-11-06 | Indicatore di regime trend, pre-registrato | Solo informativo: raddoppia la probabilità di cali ≥ 10% ma non anticipa rendimenti più bassi | [esito](research/2026-11-06-core-satellite-results.md) |

**Regola di lavoro:** ogni nuovo test si pre-registra in `docs/research/` (ipotesi, parametri,
criteri) e si pubblica nel repository **prima** di eseguirlo.

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
