# Pre-registrazione — Core-satellite e indicatore di regime (2026-11-06)

Questo documento è pubblicato nel repository **prima** di eseguire i test. Parametri, varianti e
criteri di successo non si cambiano dopo aver visto i risultati; ogni deviazione va dichiarata
nel documento di esito.

Contesto: lo [studio sul trend multi-asset](2026-11-06-ucits-trend.md) ha mostrato buona
protezione nei crolli ma un rendimento netto inferiore al 60/40 a causa delle tasse sul turnover.

## Test 1 — Core-satellite

**Ipotesi.** Un nucleo comprato e tenuto (poche vendite, poche tasse) più una quota trend come
protezione ottiene, al netto delle tasse, un rendimento vicino al 60/40 con un drawdown più basso.

**Configurazione primaria (unica usata per il verdetto):**
- Nucleo 70% del portafoglio: 60% azioni mondo (SWDA; prima della sua quotazione CSSPX) e 40%
  titoli di Stato (IBGL).
- Satellite 30%: `MultiAssetTrend` con i parametri di default, invariati rispetto allo studio
  precedente (momentum 3/6/12 mesi, media 200 giorni, top 4, volatilità inversa, tetto 25%,
  resto in XEON).
- Pesi combinati, decisione mensile, banda di non-ribilanciamento di 5 punti (entrate e uscite
  complete si eseguono sempre), costi 10 bps per lato, tasse come nello studio precedente.
- Stesse finestre e stessi benchmark: periodo completo (dal 2005) e dalla quotazione di SWDA.

**Varianti di sensibilità** (riportate tutte, non usate per scegliere): satellite al 20% e al
50%; configurazione primaria senza banda.

**Criteri di successo** (tutti, su entrambe le finestre, contro il 60/40 della stessa finestra):
1. CAGR netto ≥ CAGR netto del 60/40 − 0,25 punti;
2. Sharpe netto ≥ Sharpe netto del 60/40;
3. max drawdown inferiore di almeno il 20% (in termini relativi) a quello del 60/40, sul periodo
   completo.

Se anche un solo criterio fallisce, la strategia resta `research`.

## Test 3 — Indicatore di regime per la dashboard

**Definizione** (calcolata solo con dati fino alla chiusura del giorno):
- uno strumento è *in trend* se il prezzo è sopra la media a 200 giorni **e** il momentum medio
  3/6/12 mesi è positivo;
- **positivo**: azioni mondo in trend e almeno il 50% degli strumenti rischiosi in trend;
- **difensivo**: azioni mondo non in trend e meno del 50% degli strumenti rischiosi in trend;
- **misto**: tutti gli altri casi.

Nella dashboard: *misto* accende un'evidenza di livello `attention`, *difensivo* di livello
`critical`; *positivo* non colora nulla.

**Valutazione** sul 60/40 (azioni mondo / titoli di Stato) a partire dal giorno successivo:
- rendimento medio a 21 giorni per stato;
- frequenza di un calo di almeno il 10% del 60/40 nei 63 giorni successivi, per stato;
- quota di tempo trascorsa in ciascuno stato.

**Criterio di utilità:** lo stato *difensivo* ha un rendimento medio a 21 giorni più basso e una
frequenza di cali ≥ 10% più alta dello stato *positivo*. Se non lo è, l'indicatore resta visibile
solo come informazione, senza colorare la dashboard.
