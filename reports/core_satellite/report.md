# Esito — Core-satellite e indicatore di regime

Test eseguiti come da [pre-registrazione](2026-11-06-preregistration-core-satellite-and-regime.md), senza modifiche ai parametri. Dati 2004-01-02 → 2026-11-06.

**Verdetto core-satellite: NON validata** (stato `research`).

## Criteri pre-registrati (configurazione primaria)

| Finestra | Criterio | Valore | Soglia | Esito |
|---|---|---|---|---|
| Tutto il periodo (include il 2008) | CAGR netto >= 60/40 - 0,25 punti | 4,6% | 5,8% | ❌ |
| Tutto il periodo (include il 2008) | Sharpe netto >= 60/40 | 0,52 | 0,63 | ❌ |
| Dalla quotazione dell'MSCI World UCITS | CAGR netto >= 60/40 - 0,25 punti | 5,7% | 5,8% | ❌ |
| Dalla quotazione dell'MSCI World UCITS | Sharpe netto >= 60/40 | 0,69 | 0,72 | ❌ |
| Tutto il periodo (include il 2008) | Max drawdown almeno 20% più basso del 60/40 | -23,0% | -25,3% | ✅ |

## Tutto il periodo (include il 2008) — dal 2005-02-05

| | CAGR lordo | CAGR netto | Sharpe netto | Max drawdown | Turnover | Tasse pagate |
|---|---|---|---|---|---|---|
| Core-satellite 70/30 (primaria) | 6.4% | 4.6% | 0.52 | -23.0% | 120.2% | 76.550 € |
| Sensibilità: satellite 20% | 6.2% | 4.6% | 0.53 | -25.5% | 67.9% | 74.185 € |
| Sensibilità: satellite 50% | 6.6% | 4.8% | 0.56 | -17.7% | 203.0% | 81.880 € |
| Sensibilità: 70/30 senza banda | 6.4% | 4.5% | 0.51 | -23.0% | 152.1% | 76.012 € |
| Solo trend (studio precedente) | 7.7% | 5.3% | 0.59 | -22.0% | 452.8% | 102.185 € |
| 60/40 S&P 500 / titoli di Stato | 7.6% | 6.1% | 0.63 | -31.7% | 11.2% | 108.904 € |

## Dalla quotazione dell'MSCI World UCITS — dal 2009-09-25

| | CAGR lordo | CAGR netto | Sharpe netto | Max drawdown | Turnover | Tasse pagate |
|---|---|---|---|---|---|---|
| Core-satellite 70/30 (primaria) | 7.8% | 5.7% | 0.69 | -20.2% | 123.8% | 71.275 € |
| Sensibilità: satellite 20% | 7.8% | 5.9% | 0.73 | -21.2% | 68.4% | 72.420 € |
| Sensibilità: satellite 50% | 7.7% | 5.6% | 0.67 | -17.7% | 211.8% | 69.951 € |
| Sensibilità: 70/30 senza banda | 7.7% | 5.7% | 0.68 | -19.9% | 154.6% | 70.287 € |
| Solo trend (studio precedente) | 7.7% | 5.3% | 0.60 | -22.0% | 475.6% | 70.898 € |
| 60/40 MSCI World / titoli di Stato | 7.7% | 6.1% | 0.72 | -22.7% | 11.4% | 73.183 € |

## Indicatore di regime

Valutato sul 60/40. **Utile secondo il criterio pre-registrato: no.** Cambi di stato: 13,86 all'anno. Stato attuale (2026-11-06): **positivo**.

| Stato | Quota del tempo | Rendimento medio 60/40 nei 21 giorni dopo | Probabilità di un calo ≥ 10% nei 63 giorni dopo |
|---|---|---|---|
| positivo | 68,2% | 0,5% | 4,4% |
| misto | 10,1% | 0,7% | 2,2% |
| difensivo | 21,7% | 0,7% | 8,4% |

Limiti: gli stessi dello [studio precedente](2026-11-06-ucits-trend.md) (proxy USD convertiti in euro prima della quotazione degli UCITS, tasse semplificate, dati Yahoo). Nel periodo completo il nucleo passa da CSSPX a SWDA quando SWDA viene quotato: la vendita relativa è tassata. Risultati passati, non consulenza finanziaria.
