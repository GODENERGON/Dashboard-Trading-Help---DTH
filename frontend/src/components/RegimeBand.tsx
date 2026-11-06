import { LiquidMetal } from "@paper-design/shaders-react";
import { useMemo } from "react";

type Week = { d: string; s: string };

const MARKS = ["2008", "2011", "2015", "2018", "2020", "2022"];

const reduceMotion =
  typeof window !== "undefined" && window.matchMedia("(prefers-reduced-motion: reduce)").matches;

/** Twenty years of market as a liquid-metal process line. Dark segments = defensive regime.
 *  Neutral shades only: the trend_regime rule is informational (pre-registered test failed). */
export type Heat = "none" | "attention" | "critical";

const METAL: Record<Heat, { back: string; tint: string; mark: string }> = {
  none: { back: "#1a2638", tint: "#dfe6ee", mark: "#c9a55c" },
  attention: { back: "#3a2a17", tint: "#ffd9a3", mark: "#e59b3a" },
  critical: { back: "#3d1b14", tint: "#ffb79f", mark: "#f2735a" },
};

export function RegimeBand({ weeks, heat = "none" }: { weeks: Week[]; heat?: Heat }) {
  const metal = METAL[heat];
  const shades = useMemo(
    () =>
      weeks.map((w, i) => ({
        i,
        fill:
          w.s === "difensivo" ? "rgba(13,21,34,0.92)" : w.s === "misto" ? "rgba(13,21,34,0.55)" : "none",
      })),
    [weeks],
  );
  const n = weeks.length;
  const first = weeks[0]?.d.slice(0, 4);
  return (
    <figure style={{ margin: 0 }}>
      <div className="band" data-heat={heat} role="img" aria-label={`Regime di mercato settimanale dal ${first} a oggi`}>
        <LiquidMetal
          style={{ width: "100%", height: "100%" }}
          colorBack={metal.back}
          colorTint={metal.tint}
          shape="none"
          repetition={1.2}
          softness={0.9}
          shiftRed={0.05}
          shiftBlue={0.08}
          distortion={0.03}
          contour={0.08}
          angle={90}
          speed={reduceMotion ? 0 : 0.18}
          scale={2.4}
        />
        <svg viewBox={`0 0 ${n} 100`} preserveAspectRatio="none" aria-hidden="true">
          {shades.map((s) => (s.fill === "none" ? null : <rect key={s.i} x={s.i} y={0} width={1.05} height={100} fill={s.fill} />))}
          <rect x={n - 3} y={0} width={3} height={100} fill={metal.mark} />
        </svg>
      </div>
      <div className="band-legend" aria-hidden="true">
        <span className="start">{first}</span>
        {MARKS.map((y) => {
          const i = weeks.findIndex((w) => w.d.startsWith(y));
          if (i < 0 || i / n > 0.93) return null; // keep clear of the end-date label
          return <span key={y} style={{ left: `${(i / n) * 100}%` }}>{y}</span>;
        })}
        <span className="end" style={{ color: metal.mark }}>{weeks[n - 1]?.d.split("-").reverse().join("/")}</span>
      </div>
      <figcaption className="band-note">
        Ogni linea verticale è una settimana. Le fasce scure sono i periodi in cui il mercato era in
        fase difensiva.
      </figcaption>
    </figure>
  );
}
