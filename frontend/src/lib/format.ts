export function formatRelativeTime(iso: string | null): string {
  if (!iso) return "No timestamp";
  const then = new Date(iso).getTime();
  if (Number.isNaN(then)) return "Unknown";
  const diffSec = Math.max(0, (Date.now() - then) / 1000);
  if (diffSec < 60) return "Just now";
  if (diffSec < 3600) return `${Math.floor(diffSec / 60)}m ago`;
  if (diffSec < 86400) return `${Math.floor(diffSec / 3600)}h ago`;
  const days = Math.floor(diffSec / 86400);
  if (days < 30) return `${days}d ago`;
  return new Date(iso).toLocaleDateString("en-IN", { day: "numeric", month: "short", year: "numeric" });
}

export function formatDateTime(iso: string | null): string {
  if (!iso) return "—";
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return "—";
  return d.toLocaleString("en-IN", { day: "numeric", month: "short", year: "numeric", hour: "2-digit", minute: "2-digit" });
}

export function formatNumber(value: number | null | undefined, decimals = 0): string {
  if (value === null || value === undefined || Number.isNaN(value)) return "—";
  return value.toLocaleString("en-IN", { minimumFractionDigits: decimals, maximumFractionDigits: decimals });
}

export function formatCompactPeople(value: number | null | undefined): string {
  if (value === null || value === undefined) return "—";
  if (value >= 100000) return `${(value / 100000).toFixed(1)}L`;
  if (value >= 1000) return `${(value / 1000).toFixed(1)}k`;
  return `${value}`;
}

export function formatPct(value: number | null | undefined, decimals = 0): string {
  if (value === null || value === undefined) return "—";
  return `${value.toFixed(decimals)}%`;
}

export function formatRange(range: [number, number], suffix = ""): string {
  return `${range[0]}${suffix}–${range[1]}${suffix}`;
}

const FEATURE_LABELS: Record<string, string> = {
  lst_c: "Land surface temp",
  air_temp_c: "Air temperature",
  humidity_pct: "Humidity",
  wind_speed_mps: "Wind speed",
  ndvi: "NDVI (green cover)",
  ndbi: "NDBI (built-up)",
  built_up_pct: "Built-up share",
  road_density_km_km2: "Road density",
  population_density: "Population density",
  vulnerability_index: "Vulnerability index",
};

export function formatFriendlyFeature(key: string): string {
  return FEATURE_LABELS[key] ?? key;
}
