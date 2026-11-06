# Studio: trend multi-asset sull'universo UCITS

Dati 2004-01-02 → 2026-11-06. Ribilanciamento mensile, costi 10 bps per lato, esecuzione alla chiusura successiva alla decisione. Capitale iniziale 100.000 €. **CAGR netto** = dopo tasse annuali (26%, 12,5% sui titoli di Stato, IVAFE 0,2%) e dopo aver venduto tutto alla fine.

Configurazione di default scelta prima di vedere i dati: momentum medio 3/6/12 mesi, filtro media mobile 200 giorni, 4 strumenti al massimo, pesi a volatilità inversa con tetto 25%, resto in liquidità (XEON).

## Tutto il periodo (include la crisi del 2008) — dal 2005-02-05

| | CAGR lordo | CAGR netto | Volatilità | Sharpe lordo | Max drawdown | Turnover |
|---|---|---|---|---|---|---|
| Strategia trend | 7,7% | 5,3% | 9,8% | 0,80 | -22,0% | 452,8% |
| Buy & hold S&P 500 | 11,2% | 9,6% | 18,6% | 0,66 | -51,2% | 4,5% |
| 60/40 S&P 500 / titoli di Stato | 7,6% | 6,1% | 11,6% | 0,68 | -31,7% | 11,2% |

## Dalla quotazione dell'MSCI World UCITS (solo il ciclo 2009-oggi) — dal 2009-09-25

| | CAGR lordo | CAGR netto | Volatilità | Sharpe lordo | Max drawdown | Turnover |
|---|---|---|---|---|---|---|
| Strategia trend | 7,7% | 5,3% | 9,5% | 0,83 | -22,0% | 475,6% |
| Buy & hold MSCI World | 11,6% | 9,8% | 15,6% | 0,79 | -33,6% | 5,7% |
| 60/40 MSCI World / titoli di Stato | 7,7% | 6,1% | 10,2% | 0,78 | -22,7% | 11,4% |

Sharpe della strategia al netto delle tasse: 0,59. Tasse pagate in totale: 102.185 €. Mesi prevalentemente in liquidità: 16,1%.

## Robustezza dei parametri

Griglia di 18 combinazioni sul periodo completo. Sharpe > 0 nel 100,0% dei casi; Sharpe mediano 0,74; CAGR netto mediano 4,5% (min 2,6%, max 5,3%).

## Walk-forward (fuori campione, lordo)

CAGR 6,6%, Sharpe 0,77, max drawdown -19,1%, su 18 anni di test.

## Rendimenti per anno (lordi, periodo completo)

| Anno | Strategia | Buy & hold S&P 500 | 60/40 |
|---|---|---|---|
| 2005 | 14,5% | 13,6% | 12,1% |
| 2006 | 10,0% | 3,9% | -1,5% |
| 2007 | 5,0% | -5,0% | -3,1% |
| 2008 | -1,2% | -34,0% | -17,7% |
| 2009 | 12,4% | 23,3% | 12,7% |
| 2010 | 24,4% | 29,6% | 17,7% |
| 2011 | 0,0% | 4,4% | 3,1% |
| 2012 | 11,9% | 11,5% | 11,5% |
| 2013 | 12,0% | 27,1% | 14,9% |
| 2014 | 18,4% | 30,6% | 30,8% |
| 2015 | -6,1% | 12,8% | 8,9% |
| 2016 | 4,2% | 14,0% | 11,2% |
| 2017 | 8,7% | 6,7% | 3,6% |
| 2018 | -3,9% | -1,0% | 0,6% |
| 2019 | 10,1% | 34,3% | 26,7% |
| 2020 | -2,0% | 7,6% | 9,3% |
| 2021 | 28,2% | 40,9% | 21,9% |
| 2022 | -13,5% | -14,6% | -22,7% |
| 2023 | 4,1% | 22,0% | 17,3% |
| 2024 | 18,0% | 33,8% | 20,1% |
| 2025 | 14,3% | 4,3% | 0,4% |
| 2026 | 10,0% | 13,3% | 6,6% |

## Dati

| Strumento | Proxy | Primo dato UCITS | Primo dato usato | Giorni da proxy | Salti > 25% |
|---|---|---|---|---|---|
| SWDA.MI | URTH | 2009-09-25 | 2009-09-25 | 0 | 0 |
| CSSPX.MI | SPY | 2010-05-19 | 2004-01-02 | 1605 | 0 |
| MEUD.MI | VGK | 2024-02-19 | 2005-03-10 | 4767 | 0 |
| EIMI.MI | EEM | 2014-07-24 | 2004-01-02 | 2657 | 0 |
| IWDP.MI | VNQ | 2008-01-02 | 2004-09-29 | 820 | 0 |
| IBGL.MI | TLT | 2008-01-02 | 2004-01-02 | 1006 | 0 |
| SGLD.MI | GLD | 2014-11-28 | 2004-11-18 | 2524 | 0 |
| XEON.MI | — | 2008-01-02 | 2008-01-02 | 0 | 0 |

## Limiti noti

- Prima della quotazione degli UCITS si usano ETF USA convertiti in euro: il proxy di IBGL (Treasury USA a lunga scadenza) non è un titolo di Stato europeo.
- XEON prima della quotazione è trattato come liquidità a rendimento zero.
- Tasse pagate a fine anno invece che a giugno; costo medio ponderato; IVAFE 0,2% annuo.
- Dati Yahoo Finance: fonte non ufficiale, da incrociare prima di decisioni reali.
- Risultati passati, nessuna garanzia sul futuro. Non è consulenza finanziaria.
