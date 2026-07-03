import type { ProviderMode, RiskCategory } from "@/types/api";

export const RISK_COLORS: Record<RiskCategory, string> = {
  Low: "#3FC7B0",
  Moderate: "#E8C547",
  High: "#E8934A",
  Severe: "#E0602F",
  Extreme: "#C81E3A",
};

export const RISK_TEXT_CLASS: Record<RiskCategory, string> = {
  Low: "text-risk-low",
  Moderate: "text-risk-moderate",
  High: "text-risk-high",
  Severe: "text-risk-severe",
  Extreme: "text-risk-extreme",
};

export const RISK_ORDER: RiskCategory[] = ["Low", "Moderate", "High", "Severe", "Extreme"];

/** Interpolates a hex color along the 0-100 thermal gradient — used for the map
 * fill so wards render on a true continuous scale, not five flat swatches,
 * matching how real land-surface-temperature imagery is visualized. */
export function thermalColorForScore(score: number | null | undefined): string {
  if (score === null || score === undefined) return "#3A4570";
  const stops: [number, string][] = [
    [0, "#3FC7B0"],
    [35, "#E8C547"],
    [60, "#E8934A"],
    [80, "#E0602F"],
    [100, "#C81E3A"],
  ];
  const clamped = Math.max(0, Math.min(100, score));
  for (let i = 0; i < stops.length - 1; i++) {
    const [p0, c0] = stops[i];
    const [p1, c1] = stops[i + 1];
    if (clamped >= p0 && clamped <= p1) {
      const t = (clamped - p0) / (p1 - p0);
      return mixHex(c0, c1, t);
    }
  }
  return stops[stops.length - 1][1];
}

function mixHex(a: string, b: string, t: number): string {
  const parse = (hex: string) => [1, 3, 5].map((i) => parseInt(hex.slice(i, i + 2), 16));
  const [ar, ag, ab] = parse(a);
  const [br, bg, bb] = parse(b);
  const round = (v: number) => Math.round(v).toString(16).padStart(2, "0");
  return `#${round(ar + (br - ar) * t)}${round(ag + (bg - ag) * t)}${round(ab + (bb - ab) * t)}`;
}

export const PROVIDER_MODE_LABEL: Record<ProviderMode, string> = {
  demo: "Demo data",
  live: "Live",
  cached_fallback: "Cached (stale)",
  not_configured: "Not configured",
  error: "Unavailable",
};

export const PROVIDER_MODE_DOT: Record<ProviderMode, string> = {
  demo: "bg-ink-faint",
  live: "bg-green",
  cached_fallback: "bg-risk-moderate",
  not_configured: "bg-ink-faint",
  error: "bg-risk-extreme",
};
