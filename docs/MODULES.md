# Catalogo moduli (tab e pannelli)

Priorità: **P0** = MVP (M2), **P1** = subito dopo (M3), **P2** = quando il resto è stabile.
Ogni pannello dichiara: fonti (dal registro), aggiornamento, regole di evidenza collegate.
Legenda del tipo: 🅸 informazione, 🆂 segnale ([ADR 0004](adr/0004-information-vs-signals-and-highlight-rules.md)).

## Struttura delle tab

```
Panoramica │ Temi │ Startup │ IPO │ Materie prime │ Confronti │ Portafoglio │ Strategie │ Modelli │ Fonti │ Impostazioni
```

---

## 1. Panoramica — P0
La sala controllo: in alto la **banda di regime**, sotto il titolo di regime, poi le evidenze
attive (al massimo 5, ordinate per gravità), il rischio aggregato, i prossimi eventi e lo stato
delle fonti.

| Pannello | Contenuto | Tipo |
|---|---|---|
| Banda di regime | 20 anni di mercato colorati per regime (HMM su rendimenti e volatilità) | 🅸 |
| Regime corrente | Trend, regime di volatilità, struttura a termine VIX/VIX3M, spread HY, curva 10y-2y, breadth | 🅸 |
| Evidenze attive | Elenco delle regole accese, ciascuna con "perché?" | 🅸 |
| Segnali validati | Pesi target delle strategie `validated`+ e variazioni | 🆂 |
| Rischio | Drawdown, esposizione, volatilità, valuta, concentrazione (tutte le piattaforme) | 🅸 |
| Prossimi 14 giorni | Banche centrali, macro, trimestrali della watchlist, IPO, stacchi dividendo | 🅸 |
| Salute delle fonti | Aggiornamento per fonte (verde, ambra, rosso) | 🅸 |

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
Watchlist informativa di aziende non quotate, per **area** (Italia, Europa, mondo) e **settore**
(nucleare compatto, difesa, AI, biotech, energia, spazio, fintech…). Esempio di partenza:
Newcleo (nucleare compatto, reattori raffreddati a piombo).

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

## 7. Portafoglio — P1 (manuale) / P2 (connettori)
- Posizioni e saldi da broker, exchange e piattaforme di crowdfunding (sola lettura,
  [ADR 0005](adr/0005-read-only-connectors-and-secrets.md)) o inserimento manuale.
- Patrimonio aggregato per asset class, valuta, area geografica, piattaforma.
- **Look-through degli ETF**: lo stesso titolo presente in più ETF (rischio di concentrazione
  nascosto).
- Esposizione valutaria (quota in USD, effetto EUR/USD).
- **Vista fiscale italiana**: plusvalenze e minusvalenze realizzate, minus da recuperare e loro
  scadenze, distinzione tra redditi di capitale e redditi diversi (da validare con un
  commercialista).
- **Stress test**: impatto sul portafoglio di scenari storici (2008, 2020, 2022) e ipotetici.
- **Journal e checklist pre-trade**: regime, sizing, motivazione, scritti prima dell'acquisto.

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
- Regole di evidenza e alert (Telegram, notifiche di Windows).
- Backend locale o remoto (NUC).
- Limiti di rischio: solo più restrittivi dei default di policy.

## 12. Assistente LLM — P2 (trasversale)
- "Perché si è mosso X oggi?", "Riassumi le notizie del tema immobiliare della settimana",
  "Confronta le ultime due IPO del settore", sempre con fonti citate.
- Proposte di regole di evidenza o di ipotesi da testare nell'harness, mai segnali diretti.

## 13. Esecuzione — P2 (dietro gate)
- Paper trading su IBKR, poi live con limiti hard e conferma umana. Richiede un ADR.
