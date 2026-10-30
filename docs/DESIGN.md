# Design direction — "Sala controllo"

> Stato: **proposta**, da confermare prima della costruzione (vedi [`OPEN_QUESTIONS.md`](OPEN_QUESTIONS.md)).

## Il concetto

DTH non si ispira alle app di trading retail (sfondo nero, verde acido, candele ovunque) né ai
template SaaS. Si ispira alle **sale controllo industriali**: le interfacce HMI di un impianto
siderurgico progettate secondo la filosofia *High-Performance HMI* (ISA-101).

Il principio centrale di quelle interfacce è anche la disciplina che vogliamo nel trading:

> **Lo stato normale è grigio e calmo. Il colore compare solo quando qualcosa è fuori norma.**

Un operatore di impianto non guarda cento numeri colorati: guarda un processo neutro e nota
subito l'unico valore ambra. In DTH un mercato "normale" appare quieto; un regime di stress, un
drawdown vicino al limite, un dato vecchio *accendono* l'interfaccia. Il colore diventa
informazione, non decorazione, e l'UI scoraggia l'iperattività.

## Palette

| Nome | Hex | Ruolo |
|---|---|---|
| Calcestruzzo | `#D5D9DC` | Sfondo dell'applicazione (grigio freddo chiaro, non crema e non nero) |
| Lamiera | `#E8EBED` | Superfici di primo piano, pannelli attivi |
| Grafite | `#1D2730` | Testo principale, linee dei grafici |
| Acciaio | `#6B7782` | Testo secondario, assi, griglie, serie di confronto |
| Petrolio | `#1F5C70` | L'unico colore "neutro": le *tue* posizioni e la *tua* strategia |
| Ambra | `#D9932B` | Allerta: avvicinamento a un limite, regime che cambia, dato non fresco |
| Colata | `#C4402F` | Critico: limite violato, stop di drawdown, dato rotto |

Regole:
- Ambra e Colata **non si usano mai** per decorare o per indicare semplicemente "prezzo in
  calo". I rendimenti negativi sono grafite con segno meno; il colore è riservato agli stati.
- Il verde non esiste nella palette: "va tutto bene" è l'assenza di segnali.
- Tema scuro (P2) costruito sulle stesse regole: sfondo antracite bluastro `#262E35`, mai
  `#0B0B0B`.

## Tipografia

Una sola famiglia, **Archivo** (grotesk industriale con asse di larghezza variabile), usata in
modo attivo:
- **Archivo Expanded**, peso 600: il titolo di regime ("Mercato in tendenza, volatilità
  bassa"). È l'unico testo grande dello schermo.
- **Archivo Condensed**, 400–500: tabelle dense, etichette degli assi, ticker.
- **Archivo** normale, 400: testo corrente, note, schede di validazione.
- Cifre sempre `font-variant-numeric: tabular-nums` (le colonne di numeri si allineano). Niente
  monospace per i dati.
- Scala modulare 1.25: 12 / 15 / 19 / 23 / 29 / 36 / 45 px. Etichette in sentence case, mai
  tutto maiuscolo.

## L'elemento memorabile: la "Banda di regime"

In cima a ogni schermata, a tutta larghezza, una striscia alta circa 56 px che rappresenta
**vent'anni di mercato come una linea di processo**: ogni giorno è una colonna sottile colorata
in scala di grigi secondo il regime stimato (trend, laterale, stress). Il 2008, il 2020 e il 2022
emergono come bande scure; un cursore Petrolio segna "oggi". Se il regime corrente è di stress,
il cursore e la sua etichetta passano ad Ambra.

È l'unico punto in cui il design osa. Tutto il resto è disciplinato e silenzioso.

## Layout

Allineamento a sinistra, griglia a 12 colonne, densità alta ma respirabile. I pannelli **non
sono card identiche**: la gerarchia si esprime con dimensione, tono di fondo (Calcestruzzo vs
Lamiera) e posizione, non con bordi arrotondati e ombre.

```
┌────────────────────────────────────────────────────────────────────────────┐
│ ▓▓░░░░▓▓▓▓░░░░░░░░░███░░░░░░░░░░▓▓░░░░░░░░░░░██░░░░░░░░▓▓░░░░░░░░░░░│▲oggi │  Banda di regime
├────────────────────────────────────────────────────────────────────────────┤
│ Mercato in tendenza,                       │ Rischio                        │
│ volatilità bassa                           │ Drawdown  −3,1%  ▕████░░░░░░▏  │
│ (Archivo Expanded, l'unico titolo grande)  │ Esposizione 72%  Vol 9,4%      │
├───────────────────────────────┬────────────┴───────────┬───────────────────┤
│ Segnali validati              │ Prossimi eventi        │ Salute dei dati   │
│ tabella densa (Condensed)     │ timeline 14 giorni     │ ● ● ● ◐ ●         │
│ ticker · peso target · Δ      │ FOMC, CPI, trimestrali │                   │
├───────────────────────────────┴────────────────────────┴───────────────────┤
│ Grafico principale (lightweight-charts): prezzo + banda di quantili TSFM   │
└────────────────────────────────────────────────────────────────────────────┘
```

Mobile: la banda di regime resta in cima (scroll orizzontale), poi titolo di regime, rischio,
alert; il resto va in sezioni espandibili.

## Movimento

- Un solo momento orchestrato: al caricamento la banda di regime "scorre" da sinistra fino a
  oggi (600 ms), poi tutto è statico.
- Il resto del movimento risponde solo ad azioni dell'utente (espandere una scheda di
  validazione, cambiare orizzonte). `prefers-reduced-motion` disattiva tutto.

## Anti-pattern da evitare

- Sfondo nero con accento verde o rosso acido "da terminale".
- Griglia di card arrotondate tutte uguali con la stessa ombra.
- Etichette tutte maiuscole sopra ogni sezione, separatori " · ", frecce "→" nei bottoni.
- Rosso e verde per ogni variazione di prezzo (crea ansia e iperattività).
- Grandi numeri decorativi ("+12,4%") senza contesto né orizzonte.

## Qualità minima

Contrasto WCAG AA su tutti i testi; focus da tastiera visibile (anello Petrolio 2 px);
responsive fino a 360 px; i grafici hanno sempre una tabella dati alternativa accessibile.
