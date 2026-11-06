# Classifica prodotti per caratteristiche

Generata dal catalogo `config/products.example.yaml` (dati verificati il 2026-11-06) con le regole dell'[ADR 0009](adr/0009-product-scorecard-and-model-portfolios.md). Rigenerare con `python -m dth.cli products-report` dopo ogni aggiornamento del catalogo.

**Pesi:** costo 35%, fiscalita 25%, dimensione 20%, fedelta 10%, storicita 10%. Punteggi da 0 a 100, calcolati dentro ogni categoria. Non è una raccomandazione d'investimento: TER e patrimoni cambiano, verificare sempre la scheda dell'emittente.

## Azionario mondo

| | Prodotto | ISIN | TER | Proventi | Punteggio | Perché |
|---|---|---|---|---|---|---|
| ⭐ in evidenza | XDWD — Xtrackers MSCI World UCITS ETF 1C | IE00BJ0KDQ92 | 0,12% | accumulazione | 90 | ad accumulazione: i proventi non vengono tassati anno per anno |
| ⭐ in evidenza | VWCE — Vanguard FTSE All-World UCITS ETF (Acc) | IE00BK5BQT80 | 0,14% | accumulazione | 84 | ad accumulazione: i proventi non vengono tassati anno per anno |
| 3° | SWDA — iShares Core MSCI World UCITS ETF (Acc) | IE00B4L5Y983 | 0,20% | accumulazione | 83 | ad accumulazione: i proventi non vengono tassati anno per anno |
| 4° | VWRL — Vanguard FTSE All-World UCITS ETF (Dist) | IE00B3RBWM25 | 0,14% | distribuzione | 73 | a distribuzione: ogni provento è tassato al 26% quando viene pagato |

## Azionario USA (S&P 500)

| | Prodotto | ISIN | TER | Proventi | Punteggio | Perché |
|---|---|---|---|---|---|---|
| ⭐ in evidenza | SPXS — Invesco S&P 500 UCITS ETF (Acc) | IE00B3YCGJ38 | 0,05% | accumulazione | 92 | ad accumulazione: i proventi non vengono tassati anno per anno · ⚠️ Replica sintetica: esposizione alla controparte dello swap |
| ⭐ in evidenza | CSSPX — iShares Core S&P 500 UCITS ETF (Acc) | IE00B5BMR087 | 0,07% | accumulazione | 75 | ad accumulazione: i proventi non vengono tassati anno per anno |
| 3° | VUAA — Vanguard S&P 500 UCITS ETF (Acc) | IE00BFMXXD54 | 0,07% | accumulazione | 71 | ad accumulazione: i proventi non vengono tassati anno per anno |
| 4° | IUSA — iShares Core S&P 500 UCITS ETF (Dist) | IE0031442068 | 0,07% | distribuzione | 60 | a distribuzione: ogni provento è tassato al 26% quando viene pagato |
| 🚫 | SPY — SPDR S&P 500 ETF Trust (USA) | US78462F1030 | — | — | — | ETF domiciliato negli USA: senza KID non è acquistabile da un retail UE |

## Azionario Europa

| | Prodotto | ISIN | TER | Proventi | Punteggio | Perché |
|---|---|---|---|---|---|---|
| ⭐ in evidenza | MEUD — Amundi Core Stoxx Europe 600 UCITS ETF Acc | LU0908500753 | 0,07% | accumulazione | 90 | ad accumulazione: i proventi non vengono tassati anno per anno |
| ⭐ in evidenza | SMEA — iShares Core MSCI Europe UCITS ETF (Acc) | IE00B4K48X80 | 0,12% | accumulazione | 86 | ad accumulazione: i proventi non vengono tassati anno per anno |

## Azionario paesi emergenti

| | Prodotto | ISIN | TER | Proventi | Punteggio | Perché |
|---|---|---|---|---|---|---|
| ⭐ in evidenza | EIMI — iShares Core MSCI EM IMI UCITS ETF (Acc) | IE00BKM4GZ66 | 0,18% | accumulazione | 90 | ad accumulazione: i proventi non vengono tassati anno per anno |

## Titoli di Stato area euro

| | Prodotto | ISIN | TER | Proventi | Punteggio | Perché |
|---|---|---|---|---|---|---|
| ⭐ in evidenza | VGEA — Vanguard EUR Eurozone Government Bond UCITS ETF (Acc) | IE00BH04GL39 | 0,07% | accumulazione | 82 | ad accumulazione: i proventi non vengono tassati anno per anno |
| ⭐ in evidenza | X15E — Xtrackers Eurozone Government Bond 15-30 UCITS ETF 1C | LU0290357507 | 0,15% | accumulazione | 63 | ad accumulazione: i proventi non vengono tassati anno per anno · ⚠️ Fondo piccolo: rischio di chiusura e spread più ampi |
| 3° | IBGL — iShares Euro Government Bond 15-30yr UCITS ETF (Dist) | IE00B1FZS913 | 0,15% | distribuzione | 58 | a distribuzione: ogni provento è tassato al 26% quando viene pagato |

## Oro

| | Prodotto | ISIN | TER | Proventi | Punteggio | Perché |
|---|---|---|---|---|---|---|
| ⭐ in evidenza | SGLD — Invesco Physical Gold ETC | IE00B579F325 | 0,12% | accumulazione | 95 | ad accumulazione: i proventi non vengono tassati anno per anno |
| ⭐ in evidenza | SGLN — iShares Physical Gold ETC | IE00B4ND3602 | 0,12% | accumulazione | 95 | ad accumulazione: i proventi non vengono tassati anno per anno |
| 3° | GOLD — Amundi Physical Gold ETC (C) | FR0013416716 | 0,12% | accumulazione | 91 | ad accumulazione: i proventi non vengono tassati anno per anno |
| 4° | PHAU — WisdomTree Physical Gold | JE00B1VS3770 | 0,39% | accumulazione | 69 | ad accumulazione: i proventi non vengono tassati anno per anno |

## Immobiliare quotato (REIT)

| | Prodotto | ISIN | TER | Proventi | Punteggio | Perché |
|---|---|---|---|---|---|---|
| ⭐ in evidenza | EPRA — Amundi FTSE EPRA Nareit Global UCITS ETF DR (Acc) | LU1437018838 | 0,24% | accumulazione | 72 | ad accumulazione: i proventi non vengono tassati anno per anno |
| 2° | TRET — VanEck Global Real Estate UCITS ETF | NL0009690239 | 0,25% | distribuzione | 58 | a distribuzione: ogni provento è tassato al 26% quando viene pagato |
| 3° | SPYJ — SPDR Dow Jones Global Real Estate UCITS ETF (Acc) | IE00BH4GR342 | 0,40% | accumulazione | 50 | ad accumulazione: i proventi non vengono tassati anno per anno · ⚠️ Fondo piccolo: rischio di chiusura e spread più ampi |
| 4° | IWDP — iShares Developed Markets Property Yield UCITS ETF (Dist) | IE00B1FZS350 | 0,59% | distribuzione | 35 | a distribuzione: ogni provento è tassato al 26% quando viene pagato |

## Liquidità in euro

| | Prodotto | ISIN | TER | Proventi | Punteggio | Perché |
|---|---|---|---|---|---|---|
| ⭐ in evidenza | XEON — Xtrackers II EUR Overnight Rate Swap UCITS ETF 1C | LU0290358497 | 0,10% | accumulazione | 90 | ad accumulazione: i proventi non vengono tassati anno per anno · ⚠️ Replica sintetica: esposizione alla controparte dello swap |

## Portafogli modello

> Esempio educativo, non personalizzato: non tiene conto della tua situazione, dei tuoi obiettivi né della tua tolleranza al rischio. Non è una raccomandazione d'investimento. Ribilanciamento: una volta l'anno.

- **Prudente** — Più titoli di Stato che azioni: oscillazioni contenute, crescita lenta. 25% XDWD, 55% VGEA, 10% SGLD, 10% XEON. TER medio ponderato 0,09%.
- **Bilanciato** — Il classico 60/40 con un po' di oro: il riferimento degli studi DTH. 55% XDWD, 35% VGEA, 10% SGLD. TER medio ponderato 0,10%.
- **Dinamico** — Prevalenza azionaria: più crescita attesa, cali anche del 30-50%. 70% XDWD, 10% EIMI, 10% VGEA, 10% SGLD. TER medio ponderato 0,12%.
