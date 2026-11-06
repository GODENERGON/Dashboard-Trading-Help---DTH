# ADR 0009 — Classifica prodotti per caratteristiche e portafogli modello

- Stato: accettato
- Data: 2026-11-06

## Contesto
Gli studi del 2026-11-06 mostrano che, con la fiscalità italiana, la scelta del **prodotto**
(costi, accumulazione, replica, tipo di strumento) e un turnover basso pesano più di qualsiasi
segnale. Il proprietario vuole che l'app mostri, oltre a come comporre il portafoglio,
**prima i prodotti migliori per caratteristiche e poi tutti gli altri**.

## Decisione
1. **Catalogo prodotti** in `config/products.example.yaml`: ogni prodotto ha categoria, ISIN,
   TER, dimensione, politica dei proventi, replica, domicilio, tipo (ETF/ETC), data di avvio,
   tracking difference se nota, fonte e data di verifica.
2. **Punteggio oggettivo e trasparente** (0-100) calcolato *dentro ogni categoria*, con pesi
   dichiarati in `dth.products.scorecard.WEIGHTS`:
   - **Costo effettivo (35%)**: TER meno il vantaggio fiscale sui dividendi (es. la replica
     sintetica sull'S&P 500 evita la ritenuta USA del 15%). Il più economico della categoria
     prende 100; si perdono 25 punti per ogni 0,10% di costo in più;
   - **Fiscalità per un residente in Italia (25%)**: accumulazione (nessuna tassazione dei
     proventi anno per anno), ETC (plusvalenze in redditi diversi, compensabili), distribuzione
     penalizzata;
   - **Dimensione e liquidità (20%)**: patrimonio in scala logaritmica (100 mln → 0, 10 mld → 100);
   - **Fedeltà all'indice (10%)**: tracking difference, se disponibile;
   - **Storicità (10%)**: anni dalla quotazione (3 → 0, 10 → 100).
3. **Requisito di accesso**: solo strumenti UCITS o ETC con documentazione per l'UE; gli altri
   finiscono in una sezione "Non acquistabili da un retail italiano".
4. **Presentazione**: in ogni categoria prima **"In evidenza per caratteristiche"** (i primi due
   con punteggio ≥ 60), poi **"Tutti gli altri"**, sempre con il dettaglio voce per voce del
   punteggio ("Perché è qui?").
5. **Portafogli modello** (prudente, bilanciato, dinamico): allocazioni semplici a basso
   turnover, ribilanciamento annuale, composte con il prodotto meglio classificato di ogni
   categoria. Sono **esempi educativi non personalizzati**: non tengono conto della situazione
   dell'utente e non sono raccomandazioni d'investimento. L'avviso è sempre visibile.
6. Le valutazioni sono **informazione** ai sensi dell'[ADR 0004](0004-information-vs-signals-and-highlight-rules.md):
   non colorano la dashboard e non generano ordini.

## Alternative considerate
- Classifica per rendimento passato: scartata, perché premia il caso e cambia continuamente.
- Pesi decisi dall'utente: rimandati; per ora pesi fissi e documentati, così la classifica è
  confrontabile nel tempo.

## Conseguenze
- I dati del catalogo invecchiano: ogni prodotto ha `verified_on`; oltre 6 mesi la scheda lo
  segnala. In futuro il catalogo si potrà aggiornare dal registro fonti (es. justETF o
  FinanceDatabase, verificando i termini d'uso).
