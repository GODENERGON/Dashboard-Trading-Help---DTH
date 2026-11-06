# ADR 0008 — Conti, broker, exchange crypto e registro fiscale

- Stato: accettato
- Data: 2026-11-06

## Contesto
Il conto titoli non è ancora aperto; il proprietario sceglie il **regime dichiarativo**. Ha usato
Binance e indica Binance, Coinbase e Bitfinex come exchange crypto. Senza un sostituto
d'imposta, plusvalenze, minusvalenze e imposte patrimoniali vanno tenute in proprio.

Verifiche del 2026-11-06 (fonti nelle note del registro e in `config/tax.it.example.yaml`):
- broker esteri come Interactive Brokers, DEGIRO e Scalable Capital operano in regime
  dichiarativo per i residenti italiani;
- dal 1° luglio 2026 in UE possono offrire servizi crypto solo i CASP autorizzati MiCA. Coinbase e
  Kraken sono autorizzati; Binance no e deve cessare l'attività ordinaria in Italia; per Bitfinex
  non risulta un'autorizzazione pubblica;
- dal 1° gennaio 2026 le plusvalenze crypto sono tassate al 33% (26% per gli EMT in euro e per
  gli ETP/ETN quotati).

## Decisione
1. **Area "Conti" nella tab Portafoglio**, con tre modi di alimentarla, in ordine di semplicità:
   inserimento manuale → import CSV (con mappatura guidata) → connettore in sola lettura.
2. **Broker di partenza:** Interactive Brokers (connettore Flex Web Service), DEGIRO e Scalable
   Capital (import CSV, nessuna API ufficiale).
3. **Exchange di partenza:** Coinbase, Binance, Bitfinex (via ccxt, chiavi senza trading né
   prelievo), più Kraken e Bitpanda come alternative autorizzate MiCA.
4. **Avvisi di piattaforma:** il registro fonti ha un campo `warning`; se ci sono fondi su una
   piattaforma con avviso, scatta la regola bloccata `platform_warning` (livello critico).
5. **Tab "Fiscale"** con il registro di plusvalenze e minusvalenze, le scadenze delle minusvalenze
   e la stima di IVAFE e IVCA. Le aliquote e le regole stanno in `config/tax.it.example.yaml`,
   datate e con fonte, non nel codice. Il backtest delle strategie si valuta anche **al netto
   delle imposte** ([`VALIDATION.md`](../VALIDATION.md)).
6. L'app **non è un consulente fiscale**: la tab produce un riepilogo e un export CSV da
   verificare con un commercialista.

## Conseguenze
- Il tester non tecnico può usare l'app senza collegare nulla (solo inserimento manuale).
- Le regole fiscali cambiano spesso: il file datato rende visibile quando vanno ricontrollate,
  con la regola di evidenza `tax_rules_stale`.
