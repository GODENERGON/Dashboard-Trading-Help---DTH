import { LiquidMetal } from "@paper-design/shaders-react";

/** Wordmark in brushed chrome with a thin strip of liquid gold underneath. */
import type { Heat } from "./RegimeBand";

const STRIP: Record<Heat, [string, string]> = {
  none: ["#c9a55c", "#fff4dc"],
  attention: ["#e59b3a", "#ffe2b8"],
  critical: ["#f2735a", "#ffd0c2"],
};

export function Brand({ heat = "none" }: { heat?: Heat }) {
  return (
    <div className="brand" aria-label="Dabitur">
      <span>Dabitur</span>
      <div className="brand-strip" aria-hidden="true">
        <LiquidMetal
          style={{ width: "100%", height: "100%" }}
          colorBack={STRIP[heat][0]}
          colorTint={STRIP[heat][1]}
          shape="none"
          repetition={1}
          softness={0.9}
          distortion={0.03}
          contour={0.05}
          angle={0}
          speed={0.2}
          scale={2}
        />
      </div>
    </div>
  );
}
