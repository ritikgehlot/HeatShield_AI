import { Bar, BarChart, CartesianGrid, Cell, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import type { WardSummary } from "@/types/api";
import { RISK_COLORS, RISK_ORDER, thermalColorForScore } from "@/lib/risk";

const chartTooltipStyle = {
  background: "#131F42",
  border: "1px solid rgba(139,158,219,0.28)",
  borderRadius: 8,
  fontSize: 12,
  fontFamily: "'IBM Plex Sans', sans-serif",
  color: "#EDF1FA",
};

export function RiskDistributionChart({ wards }: { wards: WardSummary[] }) {
  const counts = RISK_ORDER.map((category) => ({
    category,
    count: wards.filter((w) => w.category === category).length,
  }));
  return (
    <ResponsiveContainer width="100%" height={220}>
      <BarChart data={counts} margin={{ top: 4, right: 8, left: -20, bottom: 0 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="rgba(139,158,219,0.1)" vertical={false} />
        <XAxis dataKey="category" tick={{ fill: "#9FAAC9", fontSize: 11 }} axisLine={{ stroke: "rgba(139,158,219,0.2)" }} tickLine={false} />
        <YAxis allowDecimals={false} tick={{ fill: "#9FAAC9", fontSize: 11 }} axisLine={false} tickLine={false} />
        <Tooltip contentStyle={chartTooltipStyle} cursor={{ fill: "rgba(139,158,219,0.06)" }} formatter={(v: number) => [`${v} ward${v === 1 ? "" : "s"}`, "Count"]} />
        <Bar dataKey="count" radius={[6, 6, 0, 0]} maxBarSize={48}>
          {counts.map((c) => (
            <Cell key={c.category} fill={RISK_COLORS[c.category]} />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  );
}

export function WardComparisonChart({ wards, onSelectWard }: { wards: WardSummary[]; onSelectWard?: (id: number) => void }) {
  const sorted = [...wards]
    .filter((w) => w.score !== null)
    .sort((a, b) => (b.score ?? 0) - (a.score ?? 0))
    .slice(0, 10)
    .map((w) => ({ id: w.id, name: w.name, score: w.score ?? 0 }));

  return (
    <ResponsiveContainer width="100%" height={Math.max(220, sorted.length * 30)}>
      <BarChart data={sorted} layout="vertical" margin={{ top: 4, right: 24, left: 8, bottom: 0 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="rgba(139,158,219,0.1)" horizontal={false} />
        <XAxis type="number" domain={[0, 100]} tick={{ fill: "#9FAAC9", fontSize: 11 }} axisLine={{ stroke: "rgba(139,158,219,0.2)" }} tickLine={false} />
        <YAxis type="category" dataKey="name" width={104} tick={{ fill: "#EDF1FA", fontSize: 11.5 }} axisLine={false} tickLine={false} />
        <Tooltip contentStyle={chartTooltipStyle} cursor={{ fill: "rgba(139,158,219,0.06)" }} formatter={(v: number) => [v.toFixed(1), "Risk score"]} />
        <Bar
          dataKey="score"
          radius={[0, 6, 6, 0]}
          maxBarSize={16}
          onClick={(entry) => onSelectWard?.((entry as unknown as { id: number }).id)}
          cursor={onSelectWard ? "pointer" : undefined}
        >
          {sorted.map((w) => (
            <Cell key={w.id} fill={thermalColorForScore(w.score)} />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  );
}
