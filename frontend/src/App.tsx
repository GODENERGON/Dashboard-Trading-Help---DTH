import { useCallback, useEffect, useState } from "react";
import { api, inDesktop, prefs, waitForEngine, type DataStatus } from "./api";
import { Brand } from "./components/Brand";
import { FeedbackDialog } from "./components/FeedbackDialog";
import { Onboarding } from "./components/Onboarding";
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

type Overview = Omit<View, "key" | "label"> & { data_status: DataStatus };
type Products = typeof products;
type Models = typeof models;

// Bundled data: shown while the engine starts and if it cannot be reached.
const BUNDLED_TODAY: Omit<View, "key" | "label"> = { ...regimeToday, risk: riskToday, highlights: [] };
const EXAMPLE: View = {
  ...(scenario as unknown as Omit<View, "key" | "label">),
  key: "esempio",
  label: "Esempio: crollo di marzo 2020",
};

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

function ModelsPanel({ models }: { models: Models }) {
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

function ProductsPanel({ products }: { products: Products }) {
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

function DataStatusLine({ st, onRefresh }: { st: DataStatus | null; onRefresh?: () => void }) {
  if (!st) return <p className="empty">Dati inclusi nell'app. Il motore di calcolo non è collegato.</p>;
  const when = st.fetched_at ? new Date(st.fetched_at).toLocaleString("it-IT", { dateStyle: "short", timeStyle: "short" }) : null;
  return (
    <p className="empty">
      Prezzi al {itDate(st.as_of)}, fonte {st.source}{when ? `, scaricati il ${when}` : ""}.{" "}
      {onRefresh && (
        <button className="link" disabled={st.refreshing} onClick={onRefresh}>
          {st.refreshing ? "Aggiornamento in corso…" : "Aggiorna ora"}
        </button>
      )}
    </p>
  );
}

function AlertsPanel({ v, st, onRefresh }: { v: View; st: DataStatus | null; onRefresh?: () => void }) {
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
      <DataStatusLine st={st} onRefresh={onRefresh} />
    </section>
  );
}

const SOON: Record<string, string> = {
  Temi: "Immobiliare, ETF, indici, crypto e materie prime raccolti per tema, con i prodotti di ogni tema.",
  Startup: "Le startup seguite, divise per settore (nucleare, data center per l'AI, farmaceutica, robotica, AI, materiali innovativi, food) e per area geografica.",
  IPO: "Le prossime quotazioni in borsa, con data, mercato e una scheda in parole semplici.",
  "Materie prime": "Oro, argento, petrolio e le altre materie prime, con i prodotti per investirci.",
  Confronti: "Grafici che mettono a confronto due o più strumenti sullo stesso periodo.",
  Portafoglio: "Le tue posizioni, lette in sola lettura dal broker o inserite a mano. Dabitur non può mai comprare o vendere.",
  Fiscale: "Il registro di plusvalenze e minusvalenze, con le scadenze del regime dichiarativo.",
  Strategie: "Gli studi fatti finora, con i risultati onesti: anche quelli che non hanno funzionato.",
  Modelli: "Previsioni dei modelli per serie storiche (come TimesFM), mostrate come ventagli di possibilità e mai come ordini.",
  Fonti: "L'elenco delle fonti autorevoli usate, con data dell'ultimo aggiornamento di ciascuna.",
  Impostazioni: "Connettori ai broker, assistente AI facoltativo con il tuo account, aggiornamenti.",
};

function ComingSoon({ tab }: { tab: string }) {
  return (
    <section className="panel placeholder" aria-labelledby="soon-h">
      <h2 id="soon-h">{tab}</h2>
      <p>{SOON[tab]}</p>
      <p>Questa sezione arriva nelle prossime versioni. Se hai idee su cosa vorresti trovarci, usa «Invia feedback».</p>
    </section>
  );
}

function ProductsTab({ products }: { products: Products }) {
  const cats = products.categories as Record<string, { label: string; featured: Ranked[]; others: Ranked[] }>;
  return (
    <section className="panel" aria-labelledby="ptab-h">
      <h2 id="ptab-h">Prodotti</h2>
      <p className="sub">Per ogni categoria: prima i migliori per caratteristiche (costo, fiscalità, dimensione, storia), poi tutti gli altri. Non è una raccomandazione.</p>
      <table>
        <thead><tr><th>Categoria</th><th>Prodotto</th><th className="num"><Term hint="Costo annuo del fondo.">TER</Term></th><th className="num">Punteggio</th><th>Da sapere</th></tr></thead>
        <tbody>
          {Object.values(cats).flatMap((c) =>
            [...c.featured, ...c.others].map((p, i) => (
              <tr key={c.label + p.product.ticker}>
                <td className="muted">{i === 0 ? c.label : ""}</td>
                <td><span className="ticker">{p.product.ticker}</span> <span className="muted">{p.product.name}</span>{i < c.featured.length && <span className="chip" data-on="true" style={{ marginLeft: 8 }}>In evidenza</span>}</td>
                <td className="num">{p.product.ter_pct.toFixed(2).replace(".", ",")}%</td>
                <td className="num"><span className="score">{Math.round(p.total)}</span></td>
                <td className="warn">{p.warnings[0] ?? (p.product.income === "accumulating" ? "Ad accumulazione" : "A distribuzione")}</td>
              </tr>
            )),
          )}
        </tbody>
      </table>
    </section>
  );
}

type Engine = "starting" | "live" | "offline";

function useEngine() {
  const [engine, setEngine] = useState<Engine>("starting");
  const [today, setToday] = useState<Overview | null>(null);
  const [prod, setProd] = useState<Products>(products);
  const [mod, setMod] = useState<Models>(models);

  const load = useCallback(async () => {
    const [o, p, m] = await Promise.all([
      api<Overview>("/overview"), api<Products>("/products"), api<Models>("/portfolios/models"),
    ]);
    setToday(o); setProd(p); setMod(m);
    return o.data_status;
  }, []);

  useEffect(() => {
    let alive = true;
    (async () => {
      const ok = await waitForEngine(inDesktop ? 60_000 : 2_500);
      if (!alive) return;
      if (!ok) { setEngine("offline"); return; }
      try { await load(); setEngine("live"); } catch { setEngine("offline"); }
    })();
    return () => { alive = false; };
  }, [load]);

  // While prices are being downloaded, poll and reload when the refresh is over.
  const refreshing = today?.data_status.refreshing ?? false;
  useEffect(() => {
    if (engine !== "live") return;
    const id = setInterval(async () => {
      try {
        const st = await api<DataStatus>("/status");
        const prev = today?.data_status;
        if (prev && (st.fetched_at !== prev.fetched_at || st.refreshing !== prev.refreshing || st.failures !== prev.failures)) {
          await load();
        }
      } catch { /* engine busy: try again at the next tick */ }
    }, refreshing ? 3_000 : 60_000);
    return () => clearInterval(id);
  }, [engine, refreshing, today, load]);

  const refresh = useCallback(async () => {
    await api("/refresh", { method: "POST" });
    setToday((o) => (o ? { ...o, data_status: { ...o.data_status, refreshing: true } } : o));
  }, []);

  return { engine, today, prod, mod, refresh };
}

export function App() {
  const { engine, today, prod, mod, refresh } = useEngine();
  const [tab, setTab] = useState("Panoramica");
  const [viewKey, setViewKey] = useState("oggi");
  const [onboarding, setOnboarding] = useState(() => prefs.get("onboarded") !== "1");
  const [feedback, setFeedback] = useState(false);

  if (engine === "starting") {
    return (
      <div className="starting" aria-live="polite">
        <Brand heat="none" />
        <p>Avvio del motore di calcolo…</p>
      </div>
    );
  }

  const views: View[] = [{ key: "oggi", label: "Oggi", ...(today ?? BUNDLED_TODAY) }, EXAMPLE];
  const v = views.find((x) => x.key === viewKey)!;
  const heat = heatOf(v.highlights);
  const st = engine === "live" ? today?.data_status ?? null : null;
  return (
    <div className="shell" data-heat={heat}>
      <aside className="sidebar">
        <Brand heat={heat} />
        <nav className="nav" aria-label="Sezioni">
          {TABS.map((t) => (
            <button key={t} aria-current={t === tab ? "page" : undefined} onClick={() => setTab(t)}>{t}</button>
          ))}
        </nav>
        <button className="feedback" onClick={() => setFeedback(true)}>Invia feedback</button>
      </aside>
      <main className="main">
        {engine === "offline" && (
          <p className="notice" role="status">
            Anteprima con i dati inclusi nell'app: il motore di calcolo non risponde.
            {inDesktop ? " Prova a chiudere e riaprire Dabitur." : ""}
          </p>
        )}
        {tab === "Panoramica" ? (
          <>
            <div className="scenario" role="radiogroup" aria-label="Situazione mostrata">
              {views.map((x) => (
                <button key={x.key} role="radio" aria-checked={x.key === viewKey} onClick={() => setViewKey(x.key)}>{x.label}</button>
              ))}
            </div>
            <RegimeBand weeks={v.weekly} heat={heat} />
            <Headline v={v} />
            <div className="grid">
              <RiskPanel v={v} />
              <ModelsPanel models={mod} />
              <ProductsPanel products={prod} />
              <AlertsPanel v={v} st={st} onRefresh={engine === "live" ? refresh : undefined} />
            </div>
          </>
        ) : tab === "Prodotti" ? (
          <ProductsTab products={prod} />
        ) : (
          <ComingSoon tab={tab} />
        )}
        <p className="disclaimer">
          Dabitur è uno strumento di informazione: non è consulenza finanziaria. Effetto metallo liquido
          realizzato con Paper Shaders, copyright Lost Coast Labs, Inc. (paper.design).
        </p>
      </main>
      {onboarding && <Onboarding onDone={() => { prefs.set("onboarded", "1"); setOnboarding(false); }} />}
      {feedback && <FeedbackDialog view={tab} live={engine === "live"} onClose={() => setFeedback(false)} />}
    </div>
  );
}
