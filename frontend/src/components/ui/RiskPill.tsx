import type { RiskCategory } from "@/types/api";
import { RISK_COLORS } from "@/lib/risk";

export function RiskPill({ category, size = "md" }: { category: RiskCategory | null; size?: "sm" | "md" | "lg" }) {
  if (!category) {
    return <span className="inline-flex items-center rounded-full border border-border px-2.5 py-0.5 text-xs text-ink-faint">No data</span>;
  }
  const color = RISK_COLORS[category];
  const sizeClass = size === "sm" ? "text-[11px] px-2 py-0.5" : size === "lg" ? "text-sm px-3.5 py-1.5" : "text-xs px-2.5 py-1";
  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded-full font-semibold ${sizeClass}`}
      style={{ backgroundColor: `${color}1F`, color, border: `1px solid ${color}55` }}
    >
      <span className="h-1.5 w-1.5 rounded-full" style={{ backgroundColor: color }} />
      {category}
    </span>
  );
}
