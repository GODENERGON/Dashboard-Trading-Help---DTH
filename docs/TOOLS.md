# Strumenti open source valutati (2026-11-06)

Strumenti trovati su GitHub che possono migliorare DTH. Prima di adottarne uno: verificare
licenza, manutenzione recente e termini d'uso dei dati, poi registrarlo qui come *adottato*.

| Strumento | A cosa serve in DTH | Stato | Note |
|---|---|---|---|
| [FinanceDatabase](https://github.com/JerBouma/FinanceDatabase) | Anagrafica di oltre 300.000 strumenti (azioni, ETF, fondi, indici, crypto) per ampliare il catalogo prodotti e la ricerca nella tab Temi | **Integrato** (`dth.integrations.financedatabase_adapter`, extra `[catalog]`) | Licenza MIT; solo metadati, nessun prezzo; mantenuta dalla comunità, quindi va validata |
| [justetf-scraping](https://github.com/druzsan/justetf-scraping) | Aggiornare TER, patrimonio e storico degli ETF UCITS nel catalogo prodotti | **Integrato, solo su richiesta** (`dth.integrations.justetf_adapter`, extra `[justetf]`): produce un elenco di differenze da rivedere | Raccoglie dati dal sito justETF: verificare i termini d'uso prima di automatizzare; in alternativa link manuali |
| [skfolio](https://skfolio.org) | Ottimizzazione e stress test dei portafogli modello con validazione incrociata | **Integrato** (studio pre-registrato, extra `[portfolio]`): [esito](research/2026-11-06-skfolio-allocation-results.md), non adottato per i portafogli modello | API in stile scikit-learn; utile per confrontare i portafogli modello con varianti a rischio controllato |
| [OpenBB](https://github.com/OpenBB-finance/OpenBB) | Piattaforma dati con molti connettori (macro, prezzi, notizie) | Da valutare | Potrebbe sostituire alcuni adattatori del registro fonti; valutare peso e licenza |
| [ccxt](https://github.com/ccxt/ccxt) | Connettori in sola lettura per Coinbase, Binance, Bitfinex, Kraken, Bitpanda | **Integrato** (`dth.connectors.CcxtConnector`, extra `[portals]`): solo saldi, ordini e prelievi bloccati | Già nel registro fonti |
| [TimesFM](https://github.com/google-research/timesfm), [Chronos](https://github.com/amazon-science/chronos-forecasting), Kronos | Modelli per serie storiche come plug-in (volatilità, quantili) | Previsto (M3) | Attivi solo se battono le baseline (ADR 0002) |
| [Tauri](https://tauri.app) | Shell desktop Windows | **Adottato** (ADR 0003) | |
| [lightweight-charts](https://github.com/tradingview/lightweight-charts) | Grafici di prezzo | **Adottato** (frontend) | |
| [Paper Shaders](https://shaders.paper.design/liquid-metal) — `@paper-design/shaders-react` | Effetto "metallo liquido" in WebGL per la banda di regime e il logo | **Adottato** (frontend) | Licenza PolyForm Shield: uso consentito per app non concorrenti di Paper; nota di copyright in [`NOTICE.md`](../NOTICE.md) |

Installazione degli extra: `pip install -e "backend[catalog,justetf,portfolio,portals]"`.

## Cosa cambia subito

- La tab **Prodotti** usa per ora il catalogo curato a mano (`config/products.example.yaml`);
  FinanceDatabase e justETF servono per ampliarlo e aggiornarlo.
- I **portafogli modello** sono calcolati con regole semplici; skfolio è il candidato per
  confrontarli con varianti ottimizzate, sempre validate fuori campione.
