# Questioni aperte (da chiudere prima di M1/M2)

Ogni decisione presa qui diventa un ADR in [`adr/`](adr/).

## Mercato e fiscalità (impattano la strategia, non solo il software)

1. **Universo solo UCITS.** Un retail residente in UE in pratica non può comprare ETF domiciliati
   negli USA (SPY, QQQ…) per l'obbligo del KID previsto dal regolamento PRIIPs. Il backtest può
   usare la storia lunga degli ETF USA come proxy, ma segnali ed esecuzione devono girare sugli
   equivalenti UCITS (es. CSPX/SXR8, SWDA, EIMI). Decidere: quotazione su Borsa Italiana
   (ETFplus) o su Xetra? In EUR o in valuta?
2. **Trattamento fiscale degli ETF in Italia.** Le plusvalenze su ETF sono di norma *redditi di
   capitale*, quindi non compensabili con le minusvalenze, che invece sono *redditi diversi*. Per
   una strategia trend con turnover, questa asimmetria può erodere molto il rendimento netto.
   Da verificare con un commercialista; poi modellarla nell'harness (aliquota 26%, con l'aliquota
   ridotta per la quota in titoli di Stato dove si applica) e valutare ETC/ETN o un turnover più
   basso.
3. **Broker e regime fiscale.** IBKR ha ottime API ma impone il regime dichiarativo (tasse e
   quadro RW a carico dell'utente). I broker italiani in regime amministrato semplificano le tasse
   ma raramente offrono API utilizzabili. Quale priorità: automazione o semplicità fiscale?

## Prodotto

4. **Frequenza:** solo dati di fine giornata (proposta) o anche intraday? L'EOD basta per il
   trend-following e riduce costi e complessità dei dati.
5. **Budget dati:** si resta su fonti gratuite (yfinance + Stooq + FRED) per M1–M2, oppure si
   prevede una fonte a pagamento (es. EODHD) per gli UCITS europei?
6. **Betting:** il progetto TRADING include anche il betting. Sta dentro DTH (un modulo separato)
   o in un repo a parte? Proposta: repo a parte, perché i dati, la validazione e il rischio sono
   diversi.
7. **Lingua UI:** italiano (proposta), con termini tecnici in inglese dove sono lo standard
   (Sharpe, drawdown).
8. **Utenti:** uno solo? Serve un'autenticazione se l'accesso è solo da LAN o Tailscale?

## Tecnica

9. **Frontend:** Vite + React + TypeScript (proposta: ecosistema dei grafici più ricco e tipi
   generati da OpenAPI) oppure server-rendered (FastAPI + HTMX, più semplice da mantenere)?
10. **Design:** confermare la direzione "Sala controllo" di [`DESIGN.md`](DESIGN.md), tema chiaro
    come principale.
11. **Script esistente:** `backtest_trend_refined.py` va copiato nel repo (in `research/legacy/`)
    per essere portato nel contratto `Signal`. Dove si trova l'ultima versione e quali risultati
    ha dato sui dati reali del NUC?
12. **Capitale e limiti:** confermare i default di [`RISK_POLICY.md`](RISK_POLICY.md) in base al
    capitale iniziale.
