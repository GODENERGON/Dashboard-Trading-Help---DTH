# Frontend (da costruire in M2)

Prima di iniziare:
1. Chiudere le questioni 9 (stack) e 10 (design) di [`../docs/OPEN_QUESTIONS.md`](../docs/OPEN_QUESTIONS.md).
2. Leggere [`../docs/DESIGN.md`](../docs/DESIGN.md): direzione "Sala controllo", colore solo per
   gli stati fuori norma.

Stack proposto: Vite + React + TypeScript, `lightweight-charts` per i prezzi, D3 per la banda di
regime e le viste custom, tipi generati con `openapi-typescript` da `http://localhost:8000/openapi.json`.

Shape di riferimento dei dati: `GET /validation/demo` (scheda di validazione su dati sintetici).
