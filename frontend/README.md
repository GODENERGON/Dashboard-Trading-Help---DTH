# Frontend — app desktop Tauri (da costruire in M2)

Prima di iniziare:
1. Leggere [ADR 0003](../docs/adr/0003-windows-desktop-app-with-tauri.md) (Tauri + sidecar
   Python) e [ADR 0004](../docs/adr/0004-information-vs-signals-and-highlight-rules.md)
   (il colore nasce solo dalle regole di evidenza).
2. Leggere [`../docs/DESIGN.md`](../docs/DESIGN.md): direzione "Sala controllo in metallo liquido".
3. Tab e pannelli: [`../docs/MODULES.md`](../docs/MODULES.md).

Stack: Tauri 2 + Vite + React + TypeScript, `lightweight-charts` per i prezzi, D3 per la banda di
regime e i confronti, tipi generati con `openapi-typescript` dallo schema OpenAPI del sidecar.

Shape di riferimento dei dati: `GET /validation/demo` (scheda di validazione su dati sintetici).
