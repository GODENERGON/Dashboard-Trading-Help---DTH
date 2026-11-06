import { useState } from "react";
import { Brand } from "./components/Brand";
import { RegimeBand } from "./components/RegimeBand";
import regime from "./data/regime.json";
import products from "./data/products.json";
import models from "./data/models.json";
import risk from "./data/risk.json";

const TABS = [
  "Panoramica", "Prodotti", "Temi", "Startup", "IPO", "Materie prime", "Confronti",
  "Portafoglio", "Fiscale", "Strategie", "Modelli", "Fonti", "Impostazioni",
];
const NAMES: Record<string, string> = {
  "SWDA.MI": "Azioni mondo", "CSSPX.MI": "Azioni USA", "MEUD.MI": "Azioni Europa",
  "EIMI.MI": "Emergenti", "IWDP.MI": "Immobiliare", "IBGL.MI": "Titoli di Stato", "SGLD.MI": "Oro",
};
// Metal tones only: gold is reserved for the user's own money (DESIGN.md).
const SHADES = ["#e3e8ee", "#a7b2bf", "#6f7c8c", "#465366"];

const pct = (x: number, d = 1) => `${(x * 100).toFixed(d).replace(".", ",")}%`;
const eur = (x: number) => `${Math.round(x).toLocaleString("it-IT")} €`;

function Term({ children, hint }: { children: string; hint: string }) {
  return <span className="term" title={hint}>{children}</span>;
}

function Headline() {
  const on = Object.entries(regime.in_trend as Record<string, boolean>);
  const count = on.filter(([, v]) => v).length;
  const titles: Record<string, string> = {
    positivo: "Mercato in tendenza positiva",
    misto: "Mercato senza una direzione",
    difensivo: "Mercato in fase difensiva",
  };
  return (
    <section className="headline" aria-label="Regime di mercato">
      <div>
        <h1>{titles[regime.current] ?? "Regime non disponibile"}</h1>
        <p>
          {count} strumenti su {on.length} sono <Term hint="Prezzo sopra la media degli ultimi 200 giorni e rendimento medio di 3, 6 e 12 mesi positivo.">in trend</Term>.
          È un'informazione di contesto: secondo il test pubblicato nel progetto non basta da sola
          per decidere quando comprare o vendere. Dati al {regime.as_of.split("-").reverse().join("/")}.
        </p>
      </div>
      <div className="trend-list" aria-label="Strumenti in trend">
        {on.map(([sym, v]) => (
          <span key={sym} className="chip" data-on={v}>{NAMES[sym] ?? sym}{v ? "" : " (non in trend)"}</span>
        ))}
      </div>
    </section>
  );
}

function Sparkline({ points }: { points: { v: number }[] }) {
  const vals = points.map((p) => p.v);
  const lo = Math.min(...vals), hi = Math.max(...vals);
  const path = vals.map((v, i) => `${(i / (vals.length - 1)) * 100},${40 - ((v - lo) / (hi - lo)) * 38}`).join(" ");
  return (
    <svg viewBox="0 0 100 42" preserveAspectRatio="none" style={{ width: "100%", height: 96 }} aria-hidden="true">
      <polyline points={path} fill="none" stroke="#c9a55c" strokeWidth={0.6} vectorEffect="non-scaling-stroke" />
    </svg>
  );
}

function RiskPanel() {
  const ddShare = Math.min(1, Math.abs(risk.drawdown_now) / 0.2);
  return (
    <section className="panel span-7" aria-labelledby="risk-h">
      <h2 id="risk-h">Rischio</h2>
      <p className="sub">{risk.label}. Nessun limite di rischio superato: nessuna evidenza attiva.</p>
      <div className="kpis">
        <div className="kpi"><div className="v money">{eur(risk.value)}</div><div className="l">Valore oggi (dal 2016)</div></div>
        <div className="kpi">
          <div className="v">{pct(risk.drawdown_now)}</div>
          <div className="l"><Term hint="Quanto si è sotto il valore massimo raggiunto in passato.">Drawdown</Term> attuale</div>
          <div className="meter" aria-hidden="true"><i style={{ width: `${ddShare * 100}%` }} /><b style={{ left: "50%" }} /></div>
        </div>
        <div className="kpi"><div className="v">{pct(risk.drawdown_max)}</div><div className="l">Calo massimo dal 2016</div></div>
        <div className="kpi"><div className="v">{pct(risk.vol_3m)}</div><div className="l"><Term hint="Quanto oscilla il valore, su base annua, negli ultimi 3 mesi.">Volatilità</Term> 3 mesi</div></div>
      </div>
      <Sparkline points={risk.equity_monthly} />
    </section>
  );
}

function ModelsPanel() {
  return (
    <section className="panel span-5" aria-labelledby="models-h">
      <h2 id="models-h">Portafogli modello</h2>
      <p className="sub">Esempi educativi, ribilanciati una volta l'anno. Non sono una raccomandazione.</p>
      {Object.values(models.models).map((m) => (
        <div key={m.label} className="model">
          <div className="model-head"><strong>{m.label}</strong><span className="muted">costo medio {pct(m.weighted_ter_pct / 100, 2)} l'anno</span></div>
          <div className="bar" role="img" aria-label={m.lines.map((l) => `${pct(l.weight, 0)} ${l.ticker}`).join(", ")}>
            {m.lines.map((l, i) => <span key={l.ticker} style={{ width: `${l.weight * 100}%`, background: SHADES[i % SHADES.length] }} />)}
          </div>
          <div className="legend">
            {m.lines.map((l, i) => <span key={l.ticker}><i style={{ background: SHADES[i % SHADES.length] }} />{pct(l.weight, 0)} {l.ticker}</span>)}
          </div>
        </div>
      ))}
    </section>
  );
}

type Ranked = { rank: number; total: number; warnings: string[]; product: { ticker: string; name: string; ter_pct: number; income: string } };

function ProductsPanel() {
  const cats = products.categories as Record<string, { label: string; featured: Ranked[]; others: Ranked[] }>;
  return (
    <section className="panel span-8" aria-labelledby="prod-h">
      <h2 id="prod-h">Prodotti in evidenza per caratteristiche</h2>
      <p className="sub">I migliori di ogni categoria per costo, fiscalità italiana, dimensione e storia. Gli altri sono nella scheda Prodotti.</p>
      <table>
        <thead><tr><th>Categoria</th><th>Prodotto</th><th className="num"><Term hint="Costo annuo del fondo.">TER</Term></th><th className="num">Punteggio</th><th>Da sapere</th></tr></thead>
        <tbody>
          {Object.values(cats).map((c) => {
            const p = c.featured[0] ?? c.others[0];
            if (!p) return null;
            return (
              <tr key={c.label}>
                <td className="muted">{c.label}</td>
                <td><span className="ticker">{p.product.ticker}</span> <span className="muted">{p.product.name}</span></td>
                <td className="num">{p.product.ter_pct.toFixed(2).replace(".", ",")}%</td>
                <td className="num"><span className="score">{Math.round(p.total)}</span></td>
                <td className="warn">{p.warnings[0] ?? (p.product.income === "accumulating" ? "Ad accumulazione" : "A distribuzione")}</td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </section>
  );
}

function AlertsPanel() {
  return (
    <section className="panel span-4 quiet" aria-labelledby="alerts-h">
      <h2 id="alerts-h">Evidenze attive</h2>
      <p className="empty">Nessuna. Quando una regola trova qualcosa da guardare, qui il metallo si scalda e trovi il perché.</p>
      <h2 style={{ marginTop: "1.4rem" }}>Fonti</h2>
      <p className="empty">Prezzi, regime e classifica aggiornati al {regime.as_of.split("-").reverse().join("/")}.</p>
    </section>
  );
}

export function App() {
  const [tab, setTab] = useState("Panoramica");
  return (
    <div className="shell">
      <aside className="sidebar">
        <Brand />
        <nav className="nav" aria-label="Sezioni">
          {TABS.map((t) => (
            <button key={t} aria-current={t === tab ? "page" : undefined} onClick={() => setTab(t)}>{t}</button>
          ))}
        </nav>
        <button className="feedback">Invia feedback</button>
      </aside>
      <main className="main">
        <RegimeBand weeks={regime.weekly} />
        <Headline />
        <div className="grid">
          <RiskPanel />
          <ModelsPanel />
          <ProductsPanel />
          <AlertsPanel />
        </div>
        <p className="disclaimer">
          Dabitur è uno strumento di informazione: non è consulenza finanziaria. Effetto metallo liquido
          realizzato con Paper Shaders, copyright Lost Coast Labs, Inc. (paper.design).
        </p>
      </main>
    </div>
  );
}
