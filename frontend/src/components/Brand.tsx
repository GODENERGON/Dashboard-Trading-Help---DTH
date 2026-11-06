import { LiquidMetal } from "@paper-design/shaders-react";

/** Wordmark in brushed chrome with a thin strip of liquid gold underneath. */
export function Brand() {
  return (
    <div className="brand" aria-label="Dabitur">
      <span>Dabitur</span>
      <div className="brand-strip" aria-hidden="true">
        <LiquidMetal
          style={{ width: "100%", height: "100%" }}
          colorBack="#c9a55c"
          colorTint="#fff4dc"
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
