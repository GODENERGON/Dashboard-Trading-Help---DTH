# Questioni aperte

Ogni decisione presa qui diventa un ADR in [`adr/`](adr/).

## Decise

| # | Questione | Decisione |
|---|---|---|
| — | Piattaforma | App desktop Windows, Tauri + sidecar Python ([ADR 0003](adr/0003-windows-desktop-app-with-tauri.md)) |
| 9 | Frontend | Vite + React + TypeScript dentro Tauri |
| — | Quando si colora la dashboard | Solo da regole esplicite; informazione separata dai segnali ([ADR 0004](adr/0004-information-vs-signals-and-highlight-rules.md)) |
| — | Connettori e LLM | Sola lettura; segreti nel portachiavi di Windows; LLM opzionale con la chiave dell'utente ([ADR 0005](adr/0005-read-only-connectors-and-secrets.md)) |
| 8 | Limiti crypto e startup | Crypto ≤ 10%, startup e crowdfunding ≤ 15% ([ADR 0006](adr/0006-crypto-and-startup-allocation-limits.md)) |
| 13 | Settori startup | Nucleare, data center AI, farmaceutico e biotech (oncologia, longevità, ringiovanimento), robotica, AI, materiali innovativi, food (`config/watchlist.startups.example.yaml`) |
| 14 | Firma dell'installer | Nessun certificato per ora; istruzioni SmartScreen nel README ([ADR 0007](adr/0007-first-tester-zero-config-no-nuc.md)) |
| 15 | NUC | Non si usa; tutto gira sul PC ([ADR 0007](adr/0007-first-tester-zero-config-no-nuc.md)) |
| — | Primo utente esterno | Un tester non tecnico su Windows, per raccogliere feedback ([ADR 0007](adr/0007-first-tester-zero-config-no-nuc.md)) |

## Ancora aperte

### Broker, fiscalità, strategia (domande inviate al proprietario il 2026-11-06)

1. **Universo solo UCITS.** Il backtest può usare gli ETF USA come proxy di storia lunga; segnali
   ed esecuzione girano sugli UCITS. Quotazione su Borsa Italiana o Xetra?
2. **Fiscalità degli ETF in Italia.** Plusvalenze su ETF = redditi di capitale (non compensabili),
   minusvalenze = redditi diversi. C'è un commercialista che può confermarlo? Ci sono
   minusvalenze pregresse da recuperare (scadono dopo 4 anni)?
3. **Broker e regime fiscale.** Conto titoli già esistente? Amministrato (tasse gestite dal
   broker, API rare) o dichiarativo (es. IBKR, ottime API)? Exchange crypto già in uso?
11. **Script esistente:** dove si trova l'ultima versione di `backtest_trend_refined.py`, su quali
    ETF è stato eseguito e con quali risultati (CAGR, max drawdown, Sharpe)?

### Prodotto

4. **Frequenza dei dati:** solo fine giornata (proposta) o anche intraday?
5. **Budget dati:** solo fonti gratuite per M1–M2 (proposta), oppure una fonte a pagamento?
6. **Betting:** fuori da DTH, in un repo a parte (proposta).
7. **Lingua UI:** italiano, con i termini tecnici standard in inglese (proposta).
10. **Design:** confermare la direzione "Sala controllo" di [`DESIGN.md`](DESIGN.md), tema chiaro
    come principale.
16. **Canale di feedback:** a quale indirizzo email arriva il feedback del tester?

### Tecnica

12. **Capitale e limiti:** confermare i default di [`RISK_POLICY.md`](RISK_POLICY.md) in base al
    capitale iniziale.
