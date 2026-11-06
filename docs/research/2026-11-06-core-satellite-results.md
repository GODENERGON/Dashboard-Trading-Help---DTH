# Esito 2026-11-06 — Core-satellite e indicatore di regime

Test eseguiti come da [pre-registrazione](2026-11-06-preregistration-core-satellite-and-regime.md),
pubblicata nel commit `fe4c7ec` prima dell'esecuzione. Nessun parametro è stato cambiato.
Unica precisazione: il criterio sul drawdown usa la curva lorda, come nelle tabelle dello
studio precedente (la pre-registrazione non lo specificava).

## In breve

- **Core-satellite 70/30: non validato.** Riduce il drawdown come atteso (−23% contro −32% del
  60/40 sul periodo completo), ma al netto delle tasse rende 1,5 punti l'anno in meno sul
  periodo completo e 0,4 punti in meno dal 2009, con uno Sharpe netto più basso.
  Nessuna variante di sensibilità cambia il quadro.
- **Indicatore di regime: informativo, non colora la dashboard.** Quando è *difensivo* la
  probabilità di un calo del 10% nei 3 mesi successivi quasi raddoppia (8,4% contro 4,4%), ma il
  rendimento medio del mese successivo non è più basso (spesso seguono rimbalzi) e lo stato cambia
  circa 14 volte l'anno. Il criterio pre-registrato non è soddisfatto: la regola `trend_regime`
  resta disattivata (`colors_dashboard = False`) e il regime si mostra come informazione.

## Cosa ne ricaviamo

1. Con la fiscalità italiana degli ETF, **il turnover è il nemico principale**: un'allocazione
   semplice e poco movimentata (60/40) batte al netto tutte le varianti con trend provate finora.
2. Il valore del trend sta nella **riduzione delle perdite nei crolli**, non nel rendimento.
   Nella dashboard ha senso come contesto di rischio (quanto è fragile il mercato), non come
   istruzione di compravendita.
3. Prossime ipotesi da pre-registrare, se si vuole continuare: trend applicato solo all'ETC
   sull'oro (plusvalenze in redditi diversi, compensabili) o soglie d'uscita molto più lente.

---

Test eseguiti come da [pre-registrazione](2026-11-06-preregistration-core-satellite-and-regime.md), senza modifiche ai parametri. Dati 2004-01-02 → 2026-11-06.

**Verdetto core-satellite: NON validata** (stato `research`).

### Criteri pre-registrati (configurazione primaria)

| Finestra | Criterio | Valore | Soglia | Esito |
|---|---|---|---|---|
| Tutto il periodo (include il 2008) | CAGR netto >= 60/40 - 0,25 punti | 4,6% | 5,8% | ❌ |
| Tutto il periodo (include il 2008) | Sharpe netto >= 60/40 | 0,52 | 0,63 | ❌ |
| Dalla quotazione dell'MSCI World UCITS | CAGR netto >= 60/40 - 0,25 punti | 5,7% | 5,8% | ❌ |
| Dalla quotazione dell'MSCI World UCITS | Sharpe netto >= 60/40 | 0,69 | 0,72 | ❌ |
| Tutto il periodo (include il 2008) | Max drawdown almeno 20% più basso del 60/40 | -23,0% | -25,3% | ✅ |

### Tutto il periodo (include il 2008) — dal 2005-02-05

| | CAGR lordo | CAGR netto | Sharpe netto | Max drawdown | Turnover | Tasse pagate |
|---|---|---|---|---|---|---|
| Core-satellite 70/30 (primaria) | 6,4% | 4,6% | 0,52 | -23,0% | 120,2% | 76.550 € |
| Sensibilità: satellite 20% | 6,2% | 4,6% | 0,53 | -25,5% | 67,9% | 74.185 € |
| Sensibilità: satellite 50% | 6,6% | 4,8% | 0,56 | -17,7% | 203,0% | 81.880 € |
| Sensibilità: 70/30 senza banda | 6,4% | 4,5% | 0,51 | -23,0% | 152,1% | 76.012 € |
| Solo trend (studio precedente) | 7,7% | 5,3% | 0,59 | -22,0% | 452,8% | 102.185 € |
| 60/40 S&P 500 / titoli di Stato | 7,6% | 6,1% | 0,63 | -31,7% | 11,2% | 108.904 € |

### Dalla quotazione dell'MSCI World UCITS — dal 2009-09-25

| | CAGR lordo | CAGR netto | Sharpe netto | Max drawdown | Turnover | Tasse pagate |
|---|---|---|---|---|---|---|
| Core-satellite 70/30 (primaria) | 7,8% | 5,7% | 0,69 | -20,2% | 123,8% | 71.275 € |
| Sensibilità: satellite 20% | 7,8% | 5,9% | 0,73 | -21,2% | 68,4% | 72.420 € |
| Sensibilità: satellite 50% | 7,7% | 5,6% | 0,67 | -17,7% | 211,8% | 69.951 € |
| Sensibilità: 70/30 senza banda | 7,7% | 5,7% | 0,68 | -19,9% | 154,6% | 70.287 € |
| Solo trend (studio precedente) | 7,7% | 5,3% | 0,60 | -22,0% | 475,6% | 70.898 € |
| 60/40 MSCI World / titoli di Stato | 7,7% | 6,1% | 0,72 | -22,7% | 11,4% | 73.183 € |

### Indicatore di regime

Valutato sul 60/40. **Utile secondo il criterio pre-registrato: no.** Cambi di stato: 13,86 all'anno. Stato attuale (2026-11-06): **positivo**.

| Stato | Quota del tempo | Rendimento medio 60/40 nei 21 giorni dopo | Probabilità di un calo ≥ 10% nei 63 giorni dopo |
|---|---|---|---|
| positivo | 68,2% | 0,5% | 4,4% |
| misto | 10,1% | 0,7% | 2,2% |
| difensivo | 21,7% | 0,7% | 8,4% |

Limiti: gli stessi dello [studio precedente](2026-11-06-ucits-trend.md) (proxy USD convertiti in euro prima della quotazione degli UCITS, tasse semplificate, dati Yahoo). Nel periodo completo il nucleo passa da CSSPX a SWDA quando SWDA viene quotato: la vendita relativa è tassata. Risultati passati, non consulenza finanziaria.
