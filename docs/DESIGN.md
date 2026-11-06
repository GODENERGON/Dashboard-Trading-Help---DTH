# Design direction — "Sala controllo in metallo liquido"

> Stato: **proposta aggiornata il 2026-11-06** su richiesta del proprietario: stile *liquid metal*
> declinato con i colori della finanza. La logica "sala controllo" resta; cambiano materiale e
> palette (sezione [Metallo liquido](#metallo-liquido-revisione-2026-11-06)). La palette chiara
> qui sotto diventa il tema secondario.

## Il concetto

Dabitur non si ispira alle app di trading retail (sfondo nero, verde acido, candele ovunque) né ai
template SaaS. Si ispira alle **sale controllo industriali**: le interfacce HMI di un impianto
siderurgico progettate secondo la filosofia *High-Performance HMI* (ISA-101).

Il principio centrale di quelle interfacce è anche la disciplina che vogliamo nel trading:

> **Lo stato normale è grigio e calmo. Il colore compare solo quando qualcosa è fuori norma.**

Un operatore di impianto non guarda cento numeri colorati: guarda un processo neutro e nota
subito l'unico valore ambra. In Dabitur un mercato "normale" appare quieto; un regime di stress, un
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

App desktop: finestra minima 1280×800, layout pensato per 1920×1080. Le tab
(Panoramica, Temi, Startup, IPO, Materie prime, Confronti, Portafoglio, Strategie, Modelli,
Fonti, Impostazioni) stanno in una barra laterale stretta; la banda di regime resta sempre in
cima, in ogni tab. A finestra stretta, i pannelli si impilano e il resto va in sezioni espandibili.

Ogni elemento colorato ha un'azione "Perché?" che apre la regola di evidenza che l'ha acceso,
con i dati usati e l'ora ([ADR 0004](adr/0004-information-vs-signals-and-highlight-rules.md)).

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
scorciatoie da tastiera per cambiare tab; i grafici hanno sempre una tabella dati alternativa accessibile.


## Metallo liquido (revisione 2026-11-06)

### L'idea
Il metallo liquido unisce due mondi del progetto: l'**acciaio** (la sala controllo di un
impianto siderurgico) e il **denaro** (oro, metalli preziosi, lingotti). La superficie dell'app è
metallo freddo e lucido, calmo; quando una regola di evidenza scatta, il metallo **si scalda**:
diventa ambra fusa per l'attenzione e rosso di colata per il critico. Il colore resta
informazione (ADR 0004), ma ora ha anche un significato fisico: *metallo freddo = tutto normale,
metallo incandescente = guarda qui*.

### Palette (tema principale, scuro)

| Nome | Hex | Ruolo |
|---|---|---|
| Inchiostro blu | `#101A2A` | Sfondo: blu notte da carta valori, non nero |
| Titanio | `#243042` | Pannelli e superfici, con gradiente spazzolato appena percettibile |
| Cromo | `#D3DAE2` | Testo principale, linee dei grafici, riflessi del metallo |
| Argento brunito | `#9AA5B2` | Testo secondario, assi, griglie, serie di confronto |
| Oro brunito | `#C9A55C` | Il tuo denaro: posizioni, strategia, portafoglio modello scelto |
| Ambra fusa | `#E59B3A` | Attenzione (`attention`) |
| Colata | `#F2735A` | Critico (`critical`); per superfici piene si usa la tonalità più scura `#A8321F` con testo Cromo (4,7:1) |

Regole invariate: niente verde, rendimenti negativi in cromo con il segno meno, ambra e colata
solo dalle regole di evidenza. Contrasto verificato (WCAG AA, ≥ 4,5:1) per tutti i colori di testo sia su Inchiostro blu sia su Titanio.

### Dove si usa l'effetto metallo liquido (e dove no)
- **Banda di regime**: un nastro di metallo liquido che scorre (componente `LiquidMetal` di
  Paper Shaders, vedi [`TOOLS.md`](TOOLS.md)). In regime normale è cromo freddo; in regime
  misto si scalda verso l'ambra; in regime difensivo il colore resta neutro finché la regola
  `trend_regime` è disattivata (test pre-registrato fallito).
- **Logo e schermata di avvio**: il nome dell'app in metallo liquido.
- **Pulsante "Invia feedback" e stato vuoto della Panoramica**: piccoli riflessi metallici statici.
- **Non** su tabelle, grafici e testi: lì il metallo è solo un gradiente spazzolato statico in
  CSS, per non affaticare la lettura né la scheda video.

### Movimento e prestazioni
- Lo shader gira solo nella banda di regime e nell'avvio, a 30 fps massimo, e si ferma quando
  la finestra non è in primo piano.
- `prefers-reduced-motion`: lo shader mostra un fotogramma fisso.
- PC poco potenti: se WebGL non è disponibile, si usa un gradiente CSS equivalente.

### Tipografia
Invariata (Archivo); i titoli grandi in Archivo Expanded prendono un riempimento metallico
(gradiente cromo → argento) solo nel titolo di regime.
