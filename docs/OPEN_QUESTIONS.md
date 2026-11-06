# Questioni aperte

Ogni decisione presa qui diventa un ADR in [`adr/`](adr/).

## Decise

| # | Questione | Decisione |
|---|---|---|
| — | Piattaforma | App desktop Windows, Tauri + sidecar Python ([ADR 0003](adr/0003-windows-desktop-app-with-tauri.md)) |
| 9 | Frontend | Vite + React + TypeScript dentro Tauri |
| — | Quando si colora la dashboard | Solo da regole esplicite; informazione separata dai segnali ([ADR 0004](adr/0004-information-vs-signals-and-highlight-rules.md)) |
| — | Connettori e LLM | Sola lettura; segreti nel portachiavi di Windows; LLM opzionale con la chiave dell'utente ([ADR 0005](adr/0005-read-only-connectors-and-secrets.md)) |

## Ancora aperte

### Mercato e fiscalità (impattano la strategia)

1. **Universo solo UCITS.** Un retail residente in UE in pratica non può comprare ETF domiciliati
   negli USA per l'obbligo del KID (PRIIPs). Il backtest può usare gli ETF USA come proxy di
   storia lunga; segnali ed esecuzione girano sugli UCITS. Quotazione su Borsa Italiana o Xetra?
2. **Fiscalità degli ETF in Italia.** Le plusvalenze su ETF sono di norma redditi di capitale (non
   compensabili), le minusvalenze redditi diversi. Da verificare con un commercialista e poi
   modellare nell'harness e nella vista fiscale.
3. **Broker e regime fiscale.** IBKR (ottime API, regime dichiarativo) o broker italiano (regime
   amministrato, API rare)? Influisce su quale connettore costruire per primo.

### Prodotto

4. **Frequenza dei dati:** solo fine giornata (proposta) o anche intraday?
5. **Budget dati:** solo fonti gratuite per M1–M2, oppure una fonte a pagamento (es. EODHD per
   gli UCITS, Dealroom per le startup)?
6. **Betting:** fuori da DTH, in un repo a parte (proposta).
7. **Lingua UI:** italiano, con i termini tecnici standard in inglese (proposta).
8. **Limiti per crypto e startup:** confermare i default proposti in [`RISK_POLICY.md`](RISK_POLICY.md)
   (crypto ≤ 10%, startup e crowdfunding ≤ 5% del patrimonio monitorato).
10. **Design:** confermare la direzione "Sala controllo" di [`DESIGN.md`](DESIGN.md), tema chiaro
    come principale.
13. **Watchlist iniziale startup:** oltre a Newcleo, quali settori e aziende seguire da subito?
14. **Firma dell'installer:** certificato di code signing (costo annuo) o avviso SmartScreen
    accettato in una prima fase?
15. **NUC:** si usa come backend remoto per i job notturni (download dati, ricalcolo modelli)
    oppure l'app resta solo locale?

### Tecnica

11. **Script esistente:** `backtest_trend_refined.py` va copiato in `research/legacy/` per il
    porting. Dove si trova l'ultima versione e quali risultati ha dato sui dati reali?
12. **Capitale e limiti:** confermare i default di [`RISK_POLICY.md`](RISK_POLICY.md) in base al
    capitale iniziale.
