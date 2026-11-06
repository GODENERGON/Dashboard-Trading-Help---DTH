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
| Crypto, peso complessivo massimo ([ADR 0006](adr/0006-crypto-and-startup-allocation-limits.md)) | 10% del patrimonio monitorato |
| Startup e crowdfunding, peso complessivo massimo ([ADR 0006](adr/0006-crypto-and-startup-allocation-limits.md)) | 15% del patrimonio monitorato |

## Strumenti

- Strategie sistematiche: solo strumenti a pronti, liquidi, quotati su mercati regolamentati
  (ETF UCITS, azioni).
- Crypto: solo a pronti; nessun derivato, nessun prestito o staking con controparte non
  regolamentata.
- Startup e crowdfunding: contenuto informativo; se si investe, vale il limite di peso qui sopra
  (strumenti illiquidi, orizzonte lungo, perdita totale possibile).
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

- Le credenziali non passano mai dal repository: nell'app stanno nel portachiavi di Windows,
  in sviluppo nel file `.env` locale, escluso da git.
- L'API del backend ascolta solo su `127.0.0.1` e richiede il token di sessione.
- Nessun agente AI può inviare ordini: l'esecuzione richiede conferma umana fino a decisione
  contraria documentata in un ADR.
