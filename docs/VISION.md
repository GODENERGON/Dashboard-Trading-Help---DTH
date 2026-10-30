# Vision

## Il problema

Le informazioni utili per decidere un trade sono sparse: grafici su una piattaforma, macro su
FRED, calendario su un sito, sentiment su un altro, il rischio del portafoglio in un foglio
Excel. Il risultato: decisioni prese su un frammento del quadro e, peggio, guidate dall'emotività
del momento.

## La risposta

DTH è **un solo schermo** che risponde, ogni giorno, a cinque domande in quest'ordine:

1. **Che regime di mercato c'è?** Trend, volatilità, condizioni finanziarie, breadth.
2. **Cosa dicono le strategie validate?** Segnali del sistema (es. trend-following multi-ETF),
   solo se hanno passato la validazione fuori campione.
3. **Quanto rischio sto portando e quanto posso portarne?** Esposizione, drawdown, sizing.
4. **Cosa sta per succedere?** Eventi macro, banche centrali, trimestrali, scadenze.
5. **C'è qualcosa di anomalo?** Alert su dati, volatilità, correlazioni, sentiment estremo.

## Per chi

Un trader retail sistematico (inizialmente un solo utente) che opera su ETF UCITS dall'Italia,
con capitale iniziale ridotto, orizzonte da giorni a mesi, e che vuole disciplina più che
"segnali caldi".

## Cosa NON è

- Non è un sistema di previsione dei prezzi. I forecast compaiono solo come **bande di
  incertezza** e input per il rischio, mai come "il prezzo andrà a X".
- Non è una piattaforma di day-trading o scalping.
- Non è un prodotto per forex/CFD (esclusi per i tassi di perdita documentati dei retail).
- Non è un consulente: niente "compra/vendi" senza contesto, metriche e storico della strategia.

## Criteri di successo

- Il tempo per una decisione informata scende da "giro di 6 siti" a < 5 minuti.
- Ogni numero in UI ha fonte, timestamp e stato di freschezza visibili.
- Ogni segnale mostrato ha una scheda di validazione (walk-forward, costi, drawdown).
- Zero ordini live finché i gate di [`RISK_POLICY.md`](RISK_POLICY.md) non sono superati.
