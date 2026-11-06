# Questioni aperte

Ogni decisione presa qui diventa un ADR in [`adr/`](adr/).

## Decise

| # | Questione | Decisione |
|---|---|---|
| — | Piattaforma | App desktop Windows, Tauri + sidecar Python ([ADR 0003](adr/0003-windows-desktop-app-with-tauri.md)) |
| 9 | Frontend | Vite + React + TypeScript dentro Tauri |
| — | Quando si colora la dashboard | Solo da regole esplicite; informazione separata dai segnali ([ADR 0004](adr/0004-information-vs-signals-and-highlight-rules.md)) |
| — | Connettori e LLM | Sola lettura; segreti nel portachiavi di Windows; LLM opzionale ([ADR 0005](adr/0005-read-only-connectors-and-secrets.md)) |
| 8 | Limiti crypto e startup | Crypto ≤ 10%, startup e crowdfunding ≤ 15% ([ADR 0006](adr/0006-crypto-and-startup-allocation-limits.md)) |
| 13 | Settori startup | Nucleare, data center AI, farmaceutico e biotech, robotica, AI, materiali innovativi, food |
| 14 | Firma dell'installer | Nessun certificato per ora; istruzioni SmartScreen nel README ([ADR 0007](adr/0007-first-tester-zero-config-no-nuc.md)) |
| 15 | NUC | Non si usa ([ADR 0007](adr/0007-first-tester-zero-config-no-nuc.md)) |
| 3 | Broker e regime | Conto da aprire, **regime dichiarativo**. Area Conti con inserimento manuale, import CSV e connettori: IBKR, DEGIRO, Scalable Capital ([ADR 0008](adr/0008-accounts-brokers-and-tax-ledger.md)) |
| — | Exchange crypto | Coinbase, Binance, Bitfinex con avviso MiCA dove manca l'autorizzazione; Kraken e Bitpanda come alternative autorizzate ([ADR 0008](adr/0008-accounts-brokers-and-tax-ledger.md)) |
| 2 | Fiscalità | Nessuna minusvalenza pregressa. Tab Fiscale con registro plus/minus; regole datate in `config/tax.it.example.yaml`; backtest anche al netto delle imposte |
| 1 | Universo | Proposto da zero: 8 strumenti UCITS/ETC su Borsa Italiana (`config/universe.example.yaml`), da verificare |

## Ancora aperte

1. **Universo:** verificare ticker, TER e disponibilità presso il broker scelto; valutare
   l'aggiunta di un ETF su materie prime diversificate e di obbligazioni a breve termine.
2. **Fiscalità:** far confermare a un commercialista le regole di `config/tax.it.example.yaml`
   (in particolare ETF = redditi di capitale, compensazioni, quadri della dichiarazione).
4. **Frequenza dei dati:** solo fine giornata (proposta) o anche intraday?
5. **Budget dati:** solo fonti gratuite per M1–M2 (proposta), oppure una fonte a pagamento?
6. **Betting:** fuori da DTH, in un repo a parte (proposta).
7. **Lingua UI:** italiano, con i termini tecnici standard in inglese (proposta).
10. **Design:** confermare la direzione "Sala controllo" di [`DESIGN.md`](DESIGN.md), tema chiaro
    come principale.
11. **Script esistente:** `backtest_trend_refined.py` mai eseguito su dati reali; il proprietario
    lo cerca (forse sul NUC). Se non si trova, si riscrive da zero in M2.
12. **Capitale e limiti:** confermare i default di [`RISK_POLICY.md`](RISK_POLICY.md) in base al
    capitale iniziale.
16. **Canale di feedback:** a quale indirizzo email arriva il feedback del tester?
