# Catalogo moduli (tab e pannelli)

Priorità: **P0** = MVP (M2), **P1** = subito dopo (M3), **P2** = quando il resto è stabile.
Ogni pannello dichiara: fonti (dal registro), aggiornamento, regole di evidenza collegate.
Legenda del tipo: 🅸 informazione, 🆂 segnale ([ADR 0004](adr/0004-information-vs-signals-and-highlight-rules.md)).

## Struttura delle tab

```
Panoramica │ Prodotti │ Temi │ Startup │ IPO │ Materie prime │ Confronti │ Portafoglio │ Fiscale │ Strategie │ Modelli │ Fonti │ Impostazioni
```

---

## 0. Primo avvio e feedback — P0 ([ADR 0007](adr/0007-first-tester-zero-config-no-nuc.md))
- **Primo avvio in 3 passi:** cosa fa l'app (e cosa non fa) → scelta dei temi di interesse →
  avviso "non è consulenza finanziaria". Poi la Panoramica è già popolata con fonti gratuite.
- **Glossario contestuale:** ogni termine tecnico ha una spiegazione in una riga al passaggio del
  mouse (drawdown, Sharpe, VIX, ETF UCITS, lock-up…).
- **Stati vuoti che guidano:** se una sezione non ha dati, dice cosa fare per riempirla.
- **Invia feedback:** pulsante sempre visibile; breve scheda (cosa stavi facendo, cosa ti
  aspettavi, voto 1-5) + email precompilata con pacchetto diagnostico allegato.

## 1. Panoramica — P0
La sala controllo: in alto la **banda di regime**, sotto il titolo di regime, poi le evidenze
attive (al massimo 5, ordinate per gravità), il rischio aggregato, i prossimi eventi e lo stato
delle fonti.

| Pannello | Contenuto | Tipo |
|---|---|---|
| Banda di regime | 20 anni di mercato colorati per regime (HMM su rendimenti e volatilità) | 🅸 |
| Regime corrente | Trend, regime di volatilità, struttura a termine VIX/VIX3M, spread HY, curva 10y-2y, breadth | 🅸 |
| Regime di trend | Stato positivo / misto / difensivo e strumenti in trend (`/regime/trend`). **Solo informativo**: il test pre-registrato non ne giustifica la colorazione ([esito](research/2026-11-06-core-satellite-results.md)) | 🅸 |
| Evidenze attive | Elenco delle regole accese, ciascuna con "perché?" | 🅸 |
| Segnali validati | Pesi target delle strategie `validated`+ e variazioni | 🆂 |
| Rischio | Drawdown, esposizione, volatilità, valuta, concentrazione (tutte le piattaforme) | 🅸 |
| Prossimi 14 giorni | Banche centrali, macro, trimestrali della watchlist, IPO, stacchi dividendo | 🅸 |
| Salute delle fonti | Aggiornamento per fonte (verde, ambra, rosso) | 🅸 |

## 1b. Prodotti e portafogli modello — P0 ([ADR 0009](adr/0009-product-scorecard-and-model-portfolios.md))
- **Classifica per caratteristiche** in ogni categoria (azionario mondo, USA, Europa, emergenti,
  titoli di Stato, oro, immobiliare, liquidità): prima **"In evidenza per caratteristiche"**,
  poi **"Tutti gli altri"**, poi i prodotti **non acquistabili** da un retail italiano.
- Punteggio 0-100 con dettaglio voce per voce: costo effettivo, fiscalità italiana, dimensione,
  fedeltà all'indice, storicità; avvisi (fondo piccolo, replica sintetica). Endpoint `/products`.
- **Portafogli modello** prudente / bilanciato / dinamico composti con i prodotti meglio
  classificati, ribilanciamento annuale, TER medio ponderato; esempi educativi non personalizzati.
  Endpoint `/portfolios/models`.
- Classifica attuale: [`PRODUCTS.md`](PRODUCTS.md).

## 2. Temi — P0 (struttura) / P1 (contenuti completi)
Un tema è una vista configurabile con quattro sezioni fisse: **Notizie · Dati · Prodotti ·
Piattaforme**. L'utente può creare temi nuovi; quelli di partenza sono:

| Tema | Dati | Prodotti | Piattaforme |
|---|---|---|---|
| Immobiliare | Prezzi abitazioni ISTAT, quotazioni OMI, mutui e tassi BCE, Euribor; ponte con lo scraper annunci personale | ETF REIT UCITS, azioni immobiliari quotate | Crowdfunding immobiliare (es. Walliance, Recrowd), portali annunci |
| ETF | Flussi, TER, tracking difference, premio/sconto sul NAV | ETF UCITS dell'universo | Broker |
| Indici | Livelli, breadth, valutazioni (P/E, CAPE dove disponibile) | ETF che li replicano | Broker |
| Crypto | Prezzi, dominance, volumi, flussi degli ETP | ETP/ETN crypto quotati in UE, spot | Exchange regolamentati MiCA |
| Obbligazioni | Curve dei tassi, spread BTP-Bund, inflazione attesa | ETF obbligazionari, titoli di Stato | Broker, aste MEF |
| Energia e nucleare | Prezzi energia, uranio, policy | ETF tematici, azioni | Broker |

Ogni tema ha una **watchlist** e le sue regole di evidenza (es. "notizia ad alta rilevanza su un
elemento della watchlist", "spread BTP-Bund sopra soglia").

## 3. Startup — P1
Watchlist informativa di aziende non quotate, per **area** (Italia, Europa, mondo) e **settore**.
Settori di partenza: nucleare (compatto, SMR, fusione), data center per l'AI, farmaceutico e
biotech (oncologia, longevità, ringiovanimento), robotica, AI, materiali innovativi, food e
agritech. Seme: Newcleo; gli altri nomi in
[`config/watchlist.startups.example.yaml`](../config/watchlist.startups.example.yaml) sono
candidati da verificare. L'utente aggiunge settori e aziende dall'app.

Scheda azienda:
- descrizione, settore, paese, anno di fondazione;
- round di finanziamento noti, investitori, ultima valutazione dichiarata (con fonte);
- notizie collegate e milestone (licenze, contratti, prototipi);
- **"Come si investe"**: non investibile / equity crowdfunding / mercato secondario / round per
  investitori qualificati / attesa di IPO, con il link alla piattaforma;
- rischi chiave (illiquidità, diluizione, perdita totale possibile).

Evidenze: nuovo round, campagna di crowdfunding aperta, annuncio di IPO, notizia rilevante.
Un LLM, se configurato, può compilare una bozza della scheda **con le fonti citate**; la scheda
resta in stato "bozza" finché l'utente non la conferma.

## 4. IPO — P1
- Calendario delle prossime quotazioni: Euronext Milan, altre borse europee, USA.
- Scheda IPO: settore, range di prezzo, valutazione implicita, crescita e margini dal prospetto,
  uso dei proventi, quota venduta dai soci esistenti, lock-up, coordinatori dell'offerta.
- **Statistiche storiche** sulle IPO comparabili: rendimento al primo giorno, a 6 e a 12 mesi,
  performance dopo la scadenza del lock-up.
- Checklist "ha senso comprarla?": valutazione rispetto ai concorrenti quotati, qualità dei
  conti, quanto vendono i soci, comportamento delle IPO dello stesso settore. È un aiuto alla
  decisione, non una raccomandazione.
- Evidenze: IPO di un'azienda della watchlist startup, apertura del periodo di offerta,
  scadenza del lock-up di un titolo seguito.

## 5. Materie prime e oro — P0 (oro) / P1 (resto)
- Oro: prezzo in USD ed EUR, rapporto oro/argento, oro vs tassi reali (TIPS 10y), riserve delle
  banche centrali, flussi degli ETC.
- Energia (Brent, WTI, gas TTF), metalli industriali (rame, alluminio, nichel), agricole
  (grano, mais, caffè, cacao), uranio.
- Curva dei futures (contango o backwardation) dove disponibile.
- Rapporto rame/oro come indicatore del ciclo economico.

## 6. Confronti — P0
Strumenti di grafico per mettere le informazioni in relazione tra loro:
- **Base 100**: più serie normalizzate dalla stessa data (es. oro vs MSCI World vs BTC vs
  immobiliare ISTAT).
- **Rapporto**: serie A / serie B (es. rame/oro, azioni/obbligazioni, small/large cap).
- **Correlazione rolling** tra due serie, con finestra regolabile.
- **Spread** (es. BTP-Bund) e differenze di rendimento.
- **Dispersione** rendimento/rischio di un insieme di strumenti.
- **Eventi sovrapposti**: notizie, decisioni delle banche centrali e regimi come marcatori sul
  grafico.
- **Stagionalità** e distribuzione dei rendimenti (code, skew).
Le viste si salvano come preferite.

## 7. Portafoglio — P1 (manuale e CSV) / P2 (connettori) ([ADR 0008](adr/0008-accounts-brokers-and-tax-ledger.md))

### Conti
Un elenco di conti, ciascuno collegato a una piattaforma del registro fonti. Tre modi per
alimentarlo, dal più semplice:
1. **Inserimento manuale** di posizioni e operazioni (sempre disponibile, anche per startup,
   crowdfunding e immobili).
2. **Import CSV** dell'estratto conto, con mappatura guidata delle colonne (DEGIRO, Scalable
   Capital, generico).
3. **Connettore in sola lettura** ([ADR 0005](adr/0005-read-only-connectors-and-secrets.md)).

| Piattaforma | Tipo | Collegamento |
|---|---|---|
| Interactive Brokers | Broker, dichiarativo | Flex Web Service (token di sola lettura) |
| DEGIRO | Broker, dichiarativo | Import CSV |
| Scalable Capital | Broker | Import CSV |
| Coinbase | Exchange crypto, autorizzato MiCA | API via ccxt |
| Binance | Exchange crypto, **senza licenza MiCA** | API via ccxt, con avviso |
| Bitfinex | Exchange crypto, **nessuna autorizzazione MiCA risultante** | API via ccxt, con avviso |
| Kraken, Bitpanda | Alternative autorizzate MiCA | API via ccxt / CSV |

Ogni piattaforma con un `warning` nel registro mostra l'avviso nella scheda del conto e, se ci
sono fondi, accende la regola critica `platform_warning`.

### Analisi
- Patrimonio aggregato per asset class, valuta, area geografica, piattaforma.
- Quota **non liquidabile a breve** (startup, crowdfunding, immobili) separata dal resto.
- Limiti di peso: crypto ≤ 10%, startup ≤ 15% ([ADR 0006](adr/0006-crypto-and-startup-allocation-limits.md)).
- **Look-through degli ETF**: lo stesso titolo presente in più ETF (rischio di concentrazione
  nascosto).
- Esposizione valutaria (quota in USD, effetto EUR/USD).
- **Stress test**: impatto sul portafoglio di scenari storici (2008, 2020, 2022) e ipotetici.
- **Journal e checklist pre-trade**: regime, sizing, motivazione, scritti prima dell'acquisto.

## 7b. Fiscale — P1 ([ADR 0008](adr/0008-accounts-brokers-and-tax-ledger.md))
Registro di plusvalenze e minusvalenze per il regime dichiarativo. Regole in
[`config/tax.it.example.yaml`](../config/tax.it.example.yaml), datate e con fonte.
- **Registro operazioni realizzate**: data, strumento, categoria fiscale, plus o minus, aliquota.
  Si alimenta da solo con le vendite registrate nei conti; si può correggere a mano.
- **Due colonne separate**: redditi di capitale (es. plusvalenze da ETF, non compensabili) e
  redditi diversi (azioni, ETC, crypto, minusvalenze compensabili).
- **Minusvalenze da recuperare** con la data di scadenza (fine del quarto anno successivo) e la
  regola `loss_expiry` quando una sta per scadere.
- **Imposte stimate dell'anno**: sostitutive (26%, 12,5% sui titoli di Stato, 33% sulle crypto)
  e patrimoniali (IVAFE 0,2% sulle attività estere, IVCA 0,2% sulle crypto).
- **Simulatore "se vendo oggi"**: imposta stimata e minusvalenze che verrebbero usate.
- **Export CSV per il commercialista.**
- Avviso fisso: stima indicativa, non consulenza fiscale.

## 8. Strategie — P0
- Strategie sistematiche (trend-following multi-ETF, dual momentum top-K…), stato `research` →
  `validated` → `paper` → `live`.
- Scheda di validazione: equity curve fuori campione, Sharpe, max drawdown, turnover, costi,
  heatmap della sweep dei parametri, confronto con il benchmark.

## 9. Modelli — P1
- Modelli per serie storiche installabili come plug-in: TimesFM 2.5, Chronos-2, Moirai-2,
  Kronos (specifico per i dati di mercato a candele).
- Per ciascuno: compito (volatilità, quantili), skill score vs baseline in walk-forward,
  ultimo aggiornamento. Skill ≤ 0 → nascosto ([ADR 0002](adr/0002-models-are-not-oracles.md)).
- Nei grafici compaiono come **bande di incertezza**, mai come target di prezzo.

## 10. Fonti — P0
- Il registro fonti, modificabile: aggiungi, disattiva, verifica.
- Per ogni fonte: tipo, categorie, costo, affidabilità, ultimo aggiornamento, errori, permessi.
- Pulsante "verifica": prova la connessione e mostra un campione dei dati.

## 11. Impostazioni — P0
- Account LLM (opzionale): Anthropic, OpenAI o Ollama locale; chiave nel portachiavi di Windows.
- Regole di evidenza e notifiche di Windows (Telegram facoltativo per l'utente principale).
- Limiti di rischio: solo più restrittivi dei default di policy.

## 12. Assistente LLM — P2 (trasversale)
- "Perché si è mosso X oggi?", "Riassumi le notizie del tema immobiliare della settimana",
  "Confronta le ultime due IPO del settore", sempre con fonti citate.
- Proposte di regole di evidenza o di ipotesi da testare nell'harness, mai segnali diretti.

## 13. Esecuzione — P2 (dietro gate)
- Paper trading su IBKR, poi live con limiti hard e conferma umana. Richiede un ADR.
