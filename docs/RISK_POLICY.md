# Risk policy

Questi limiti sono implementati in `backend/src/dth/risk/` e coperti da test.
Modificarli richiede un ADR in [`adr/`](adr/).

## Limiti di portafoglio (default, configurabili verso il basso, non verso l'alto)

| Limite | Valore |
|---|---|
| Peso massimo per singolo strumento | 25% |
| Esposizione lorda massima | 100% (niente leva) |
| Target di volatilità del portafoglio | 10% annuo |
| Drawdown di allerta | −10% dal massimo |
| Drawdown di stop (si dimezza l'esposizione e si va in revisione manuale) | −20% dal massimo |
| Rischio massimo per trade discrezionale | 1% del capitale |

## Strumenti

- Strategie sistematiche: solo strumenti a pronti, liquidi, quotati su mercati regolamentati
  (ETF UCITS, azioni).
- Crypto: solo a pronti, con peso massimo complessivo del 10% del patrimonio monitorato; nessun
  derivato, nessun prestito o staking con controparte non regolamentata.
- Startup e crowdfunding: contenuto informativo; se si investe, peso massimo complessivo del 5%
  (strumenti illiquidi, perdita totale possibile).
- Esclusi forex, CFD, opzioni scritte senza copertura e prodotti a leva giornaliera.

## Connettori

- Sola lettura, chiavi senza permessi di trading né di prelievo, segreti nel portachiavi di
  Windows ([ADR 0005](adr/0005-read-only-connectors-and-secrets.md)).

## Gate verso l'esecuzione

| Da → A | Requisito |
|---|---|
| `research` → `validated` | Criteri di [`VALIDATION.md`](VALIDATION.md) |
| `validated` → `paper` | Revisione manuale della scheda di validazione |
| `paper` → `live` | ≥ 3 mesi di paper trading con tracking error vs backtest accettabile e riconciliazione senza errori |
| `live` (capitale minimo) → scala | ≥ 6 mesi live senza violazioni di policy |

## Sicurezza operativa

- Le credenziali del broker non passano mai dal repository: solo `.env` locale, escluso da git.
- L'API non è esposta su internet.
- Nessun agente AI può inviare ordini: l'esecuzione richiede conferma umana fino a decisione
  contraria documentata in un ADR.
