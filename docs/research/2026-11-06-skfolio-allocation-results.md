<!-- Generato da `python -m dth.cli allocation-study` sullo stesso pannello di prezzi del workflow `research`. -->
# Esito — Allocazioni con skfolio contro il bilanciato statico

Eseguito come da [pre-registrazione](2026-11-06-preregistration-skfolio-allocation.md). Periodo 2008-12-31 → 2026-11-06, ribilanciamento annuale, costi 10 bps, tasse italiane.

| | CAGR lordo | CAGR netto | Sharpe netto | Max drawdown | Turnover |
|---|---|---|---|---|---|
| skfolio Hierarchical Risk Parity | 6,5% | 5,0% | 0,70 | -22,3% | 25,9% |
| skfolio Risk Budgeting | 7,4% | 5,8% | 0,79 | -21,5% | 18,2% |
| Bilanciato statico 55/35/10 | 8,5% | 6,7% | 0,80 | -20,8% | 17,9% |

## skfolio Hierarchical Risk Parity: **non adottato**

| Criterio | Valore | Soglia | Esito |
|---|---|---|---|
| Sharpe netto >= bilanciato + 0,05 | 0,70 | 0,85 | ❌ |
| CAGR netto >= bilanciato - 0,50 punti | 5,0% | 6,2% | ❌ |
| Max drawdown non peggiore di 2 punti | -22,3% | -22,8% | ✅ |

Pesi medi: SWDA.MI 9,7%, CSSPX.MI 0,1%, MEUD.MI 6,7%, EIMI.MI 4,9%, IWDP.MI 13,8%, IBGL.MI 46,7%, SGLD.MI 18,0%.

## skfolio Risk Budgeting: **non adottato**

| Criterio | Valore | Soglia | Esito |
|---|---|---|---|
| Sharpe netto >= bilanciato + 0,05 | 0,79 | 0,85 | ❌ |
| CAGR netto >= bilanciato - 0,50 punti | 5,8% | 6,2% | ❌ |
| Max drawdown non peggiore di 2 punti | -21,5% | -22,8% | ✅ |

Pesi medi: SWDA.MI 12,4%, CSSPX.MI 0,4%, MEUD.MI 11,0%, EIMI.MI 9,3%, IWDP.MI 12,7%, IBGL.MI 35,0%, SGLD.MI 19,3%.

Limiti: come negli studi precedenti (proxy USD in EUR, tasse semplificate, dati Yahoo). Risultati passati, non consulenza finanziaria.

## Cosa ne ricaviamo

Anche i metodi di diversificazione di skfolio, a parità di tasse e costi, non battono il
semplice bilanciato a pesi fissi: tendono a pesare molto titoli di Stato, oro e immobiliare, e
rendono meno. I portafogli modello di Dabitur restano quindi **a pesi fissi con ribilanciamento
annuale** (ADR 0009). skfolio resta disponibile per analisi del rischio e stress test.
