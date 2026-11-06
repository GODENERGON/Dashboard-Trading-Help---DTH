# Strumenti open source valutati (2026-11-06)

Strumenti trovati su GitHub che possono migliorare DTH. Prima di adottarne uno: verificare
licenza, manutenzione recente e termini d'uso dei dati, poi registrarlo qui come *adottato*.

| Strumento | A cosa serve in DTH | Stato | Note |
|---|---|---|---|
| [FinanceDatabase](https://github.com/JerBouma/FinanceDatabase) | Anagrafica di oltre 300.000 strumenti (azioni, ETF, fondi, indici, crypto) per ampliare il catalogo prodotti e la ricerca nella tab Temi | **Da adottare (M3)** | Licenza MIT; solo metadati, nessun prezzo; mantenuta dalla comunità, quindi va validata |
| [justetf-scraping](https://github.com/druzsan/justetf-scraping) | Aggiornare TER, patrimonio e storico degli ETF UCITS nel catalogo prodotti | Da valutare | Raccoglie dati dal sito justETF: verificare i termini d'uso prima di automatizzare; in alternativa link manuali |
| [skfolio](https://skfolio.org) | Ottimizzazione e stress test dei portafogli modello con validazione incrociata | Da valutare (M3) | API in stile scikit-learn; utile per confrontare i portafogli modello con varianti a rischio controllato |
| [OpenBB](https://github.com/OpenBB-finance/OpenBB) | Piattaforma dati con molti connettori (macro, prezzi, notizie) | Da valutare | Potrebbe sostituire alcuni adattatori del registro fonti; valutare peso e licenza |
| [ccxt](https://github.com/ccxt/ccxt) | Connettori in sola lettura per Coinbase, Binance, Bitfinex, Kraken | **Previsto (M4)** | Già nel registro fonti |
| [TimesFM](https://github.com/google-research/timesfm), [Chronos](https://github.com/amazon-science/chronos-forecasting), Kronos | Modelli per serie storiche come plug-in (volatilità, quantili) | Previsto (M3) | Attivi solo se battono le baseline (ADR 0002) |
| [Tauri](https://tauri.app) | Shell desktop Windows | **Adottato** (ADR 0003) | |
| [lightweight-charts](https://github.com/tradingview/lightweight-charts) | Grafici di prezzo | **Adottato** (frontend) | |
| [Paper Shaders](https://shaders.paper.design/liquid-metal) — `@paper-design/shaders-react` | Effetto "metallo liquido" in WebGL per la banda di regime e il logo | **Da adottare (M1)** | Componente React `LiquidMetal`; verificare la licenza del pacchetto prima dell'uso |

## Cosa cambia subito

- La tab **Prodotti** usa per ora il catalogo curato a mano (`config/products.example.yaml`);
  FinanceDatabase e justETF servono per ampliarlo e aggiornarlo.
- I **portafogli modello** sono calcolati con regole semplici; skfolio è il candidato per
  confrontarli con varianti ottimizzate, sempre validate fuori campione.
