import { useState } from "react";
import { Brand } from "./components/Brand";
import { RegimeBand, type Heat } from "./components/RegimeBand";
import regimeToday from "./data/regime.json";
import riskToday from "./data/risk.json";
import scenario from "./data/scenario.json";
import products from "./data/products.json";
import models from "./data/models.json";

type Highlight = {
  rule_id: string; level: "attention" | "critical"; title: string; explanation: string;
  as_of: string; data: Record<string, unknown>;
};
type Risk = { label: string; value: number; drawdown_now: number; drawdown_max: number; vol_3m: number; equity_monthly: { d: string; v: number }[] };
type View = {
  key: string; label: string; as_of: string; current: string; in_trend: Record<string, boolean>;
  weekly: { d: string; s: string }[]; risk: Risk; highlights: Highlight[];
};

const VIEWS: View[] = [
  { key: "oggi", label: "Oggi", ...regimeToday, risk: riskToday, highlights: [] },
  {
    ...(scenario as unknown as Omit<View, "key" | "label">),
    key: "esempio",
    label: "Esempio: crollo di marzo 2020",
  },
];

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
const LEVEL_LABEL = { critical: "Critico", attention: "Attenzione" } as const;
const DATA_LABEL: Record<string, string> = {
  drawdown: "Drawdown", limit: "Limite della policy", peak: "Massimo raggiunto il", source: "Fonte",
};

const pct = (x: number, d = 1) => `${(x * 100).toFixed(d).replace(".", ",")}%`;
const eur = (x: number) => `${Math.round(x).toLocaleString("it-IT")} €`;
const itDate = (iso: string) => iso.split("-").reverse().join("/");

function heatOf(hs: Highlight[]): Heat {
  if (hs.some((h) => h.level === "critical")) return "critical";
  return hs.length ? "attention" : "none";
}

function Term({ children, hint }: { children: string; hint: string }) {
  return <span className="term" title={hint}>{children}</span>;
}

function Headline({ v }: { v: View }) {
  const on = Object.entries(v.in_trend);
  const count = on.filter(([, x]) => x).length;
  const titles: Record<string, string> = {
    positivo: "Mercato in tendenza positiva",
    misto: "Mercato senza una direzione",
    difensivo: "Mercato in fase difensiva",
  };
  const crit = v.highlights.filter((h) => h.level === "critical").length;
  const att = v.highlights.length - crit;
  return (
    <section className="headline" aria-label="Regime di mercato">
      <div>
        <h1>{titles[v.current] ?? "Regime non disponibile"}</h1>
        <p>
          {count} {count === 1 ? "strumento" : "strumenti"} su {on.length} {count === 1 ? "è" : "sono"} <Term hint="Prezzo sopra la media degli ultimi 200 giorni e rendimento medio di 3, 6 e 12 mesi positivo.">in trend</Term>.
          Il regime è un'informazione di contesto: da solo non colora l'app. Dati al {itDate(v.as_of)}.
        </p>
        {v.highlights.length > 0 && (
          <p className="alert-count">
            {crit > 0 && <span data-level="critical">{crit} {crit === 1 ? "evidenza critica" : "evidenze critiche"}</span>}
            {att > 0 && <span data-level="attention">{att} {att === 1 ? "evidenza di attenzione" : "evidenze di attenzione"}</span>}
          </p>
        )}
      </div>
      <div className="trend-list" aria-label="Strumenti in trend">
        {on.map(([sym, x]) => (
          <span key={sym} className="chip" data-on={x}>{NAMES[sym] ?? sym}{x ? "" : " (non in trend)"}</span>
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

function RiskPanel({ v }: { v: View }) {
  const r = v.risk;
  const hit = v.highlights.find((h) => h.rule_id.startsWith("drawdown"));
  const scale = 0.25; // meter spans 0 … -25%
  return (
    <section className="panel span-7" data-level={hit?.level} aria-labelledby="risk-h">
      <h2 id="risk-h">Rischio {hit && <span className="badge" data-level={hit.level}>{LEVEL_LABEL[hit.level]}</span>}</h2>
      <p className="sub">{r.label}. {hit ? hit.title + "." : "Nessun limite di rischio superato."}</p>
      <div className="kpis">
        <div className="kpi"><div className="v money">{eur(r.value)}</div><div className="l">Valore al {itDate(v.as_of)} (dal 2016)</div></div>
        <div className="kpi" data-level={hit?.level}>
          <div className="v">{pct(r.drawdown_now)}</div>
          <div className="l"><Term hint="Quanto si è sotto il valore massimo raggiunto in passato.">Drawdown</Term> attuale</div>
          <div className="meter" aria-hidden="true">
            <i style={{ width: `${Math.min(1, Math.abs(r.drawdown_now) / scale) * 100}%` }} />
            <b title="Allerta -10%" style={{ left: `${(0.1 / scale) * 100}%` }} />
            <b className="stop" title="Stop -20%" style={{ left: `${(0.2 / scale) * 100}%` }} />
          </div>
        </div>
        <div className="kpi"><div className="v">{pct(r.drawdown_max)}</div><div className="l">Calo massimo dal 2016</div></div>
        <div className="kpi"><div className="v">{pct(r.vol_3m)}</div><div className="l"><Term hint="Quanto oscilla il valore, su base annua, negli ultimi 3 mesi.">Volatilità</Term> 3 mesi</div></div>
      </div>
      <Sparkline points={r.equity_monthly} />
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

function HighlightItem({ h }: { h: Highlight }) {
  const [open, setOpen] = useState(false);
  return (
    <li className="hl" data-level={h.level}>
      <div className="hl-head">
        <span className="badge" data-level={h.level}>{LEVEL_LABEL[h.level]}</span>
        <strong>{h.title}</strong>
      </div>
      <button className="why" aria-expanded={open} onClick={() => setOpen(!open)}>{open ? "Chiudi" : "Perché?"}</button>
      {open && (
        <div className="hl-body">
          <p>{h.explanation}</p>
          <dl>
            <dt>Regola</dt><dd><code>{h.rule_id}</code></dd>
            <dt>Dati al</dt><dd>{itDate(h.as_of)}</dd>
            {Object.entries(h.data).map(([k, val]) => (
              <span key={k} style={{ display: "contents" }}>
                <dt>{DATA_LABEL[k] ?? k}</dt>
                <dd>{typeof val === "number" ? pct(val) : /^\d{4}-\d{2}-\d{2}$/.test(String(val)) ? itDate(String(val)) : String(val)}</dd>
              </span>
            ))}
          </dl>
        </div>
      )}
    </li>
  );
}

function AlertsPanel({ v }: { v: View }) {
  const hs = [...v.highlights].sort((a, b) => (a.level === b.level ? 0 : a.level === "critical" ? -1 : 1));
  return (
    <section className={`panel span-4${hs.length ? "" : " quiet"}`} aria-labelledby="alerts-h">
      <h2 id="alerts-h">Evidenze attive</h2>
      {hs.length === 0 ? (
        <p className="empty">Nessuna. Quando una regola trova qualcosa da guardare, qui il metallo si scalda e trovi il perché.</p>
      ) : (
        <ul className="hl-list">{hs.map((h) => <HighlightItem key={h.rule_id} h={h} />)}</ul>
      )}
      <h2 style={{ marginTop: "1.4rem" }}>Fonti</h2>
      <p className="empty">Prezzi, regime e classifica aggiornati al {itDate(v.as_of)}.</p>
    </section>
  );
}

export function App() {
  const [tab, setTab] = useState("Panoramica");
  const [viewKey, setViewKey] = useState("oggi");
  const v = VIEWS.find((x) => x.key === viewKey)!;
  const heat = heatOf(v.highlights);
  return (
    <div className="shell" data-heat={heat}>
      <aside className="sidebar">
        <Brand heat={heat} />
        <nav className="nav" aria-label="Sezioni">
          {TABS.map((t) => (
            <button key={t} aria-current={t === tab ? "page" : undefined} onClick={() => setTab(t)}>{t}</button>
          ))}
        </nav>
        <button className="feedback">Invia feedback</button>
      </aside>
      <main className="main">
        <div className="scenario" role="radiogroup" aria-label="Situazione mostrata">
          {VIEWS.map((x) => (
            <button key={x.key} role="radio" aria-checked={x.key === viewKey} onClick={() => setViewKey(x.key)}>{x.label}</button>
          ))}
        </div>
        <RegimeBand weeks={v.weekly} heat={heat} />
        <Headline v={v} />
        <div className="grid">
          <RiskPanel v={v} />
          <ModelsPanel />
          <ProductsPanel />
          <AlertsPanel v={v} />
        </div>
        <p className="disclaimer">
          Dabitur è uno strumento di informazione: non è consulenza finanziaria. Effetto metallo liquido
          realizzato con Paper Shaders, copyright Lost Coast Labs, Inc. (paper.design).
        </p>
      </main>
    </div>
  );
}
