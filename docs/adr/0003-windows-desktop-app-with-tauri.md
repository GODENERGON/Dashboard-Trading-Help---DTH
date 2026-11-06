# ADR 0003 — App desktop Windows con Tauri e backend Python incluso

- Stato: accettato
- Data: 2026-11-06

## Contesto
L'obiettivo iniziale era un'app web self-hosted sul NUC. Il requisito ora è un'applicazione
**installabile su Windows**, usabile anche senza il NUC. L'ecosistema di analisi (pandas,
modelli per serie storiche, backtest) è in Python e va mantenuto.

## Decisione
- Shell desktop: **Tauri 2** (finestra nativa WebView2, installer `.msi`/NSIS, aggiornamento
  automatico firmato).
- Interfaccia: Vite + React + TypeScript dentro Tauri.
- Backend: il pacchetto Python `dth` impacchettato come eseguibile (PyInstaller) e avviato da
  Tauri come **sidecar** su `127.0.0.1` con porta casuale e token di sessione.
- Dati utente in `%LOCALAPPDATA%\DTH\` (lake Parquet, DuckDB, configurazioni, log).
- Il NUC diventa **opzionale**: può eseguire lo stesso backend in Docker per i job notturni, e
  l'app desktop può puntare a quel backend invece che al sidecar locale.
- I modelli pesanti (TimesFM, Chronos, Kronos) sono **plug-in scaricabili** dall'app, non inclusi
  nell'installer, per tenerlo leggero.

## Alternative considerate
- **Electron**: più maturo, ma installer da 100+ MB e consumo di memoria maggiore.
- **App Python nativa (PySide/Qt)**: un solo linguaggio, ma un ecosistema di grafici finanziari
  web molto più povero e il design "sala controllo" più difficile da realizzare.
- **Solo web app sul NUC**: non soddisfa il requisito "installabile su Windows".

## Conseguenze
- Serve una pipeline di build Windows in CI (runner `windows-latest`).
- Il contratto tra UI e backend è l'API HTTP locale: i tipi TypeScript si generano dall'OpenAPI.
- La firma del codice dell'installer va gestita (certificato o, inizialmente, avviso SmartScreen).
