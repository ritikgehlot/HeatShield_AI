import { Bar, BarChart, CartesianGrid, Cell, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import type { FeatureContribution } from "@/types/api";

const chartTooltipStyle = {
  background: "#131F42",
  border: "1px solid rgba(139,158,219,0.28)",
  borderRadius: 8,
  fontSize: 12,
  fontFamily: "'IBM Plex Sans', sans-serif",
  color: "#EDF1FA",
};

/** Bar length here is the EXACT points each feature contributed to the 0-100
 * score — not a stylized approximation. For this additive model that exact
 * attribution doubles as the Shapley value, so what's drawn is literally the
 * math, not a decorative summary of it. */
export function FactorContributionChart({ factors }: { factors: FeatureContribution[] }) {
  const present = factors.filter((f) => f.value !== null).sort((a, b) => b.contribution_pts - a.contribution_pts);
  return (
    <ResponsiveContainer width="100%" height={Math.max(180, present.length * 34)}>
      <BarChart data={present} layout="vertical" margin={{ top: 4, right: 32, left: 8, bottom: 0 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="rgba(139,158,219,0.1)" horizontal={false} />
        <XAxis type="number" tick={{ fill: "#9FAAC9", fontSize: 11 }} axisLine={{ stroke: "rgba(139,158,219,0.2)" }} tickLine={false} unit=" pts" />
        <YAxis type="category" dataKey="label" width={150} tick={{ fill: "#EDF1FA", fontSize: 11.5 }} axisLine={false} tickLine={false} />
        <Tooltip
          contentStyle={chartTooltipStyle}
          formatter={(v: number, _n, entry) => [`${v.toFixed(1)} pts (value: ${entry.payload.value})`, "Contribution"]}
        />
        <Bar dataKey="contribution_pts" radius={[0, 6, 6, 0]} maxBarSize={18}>
          {present.map((f, i) => (
            <Cell key={f.key} fill={i === 0 ? "#E0602F" : i === 1 ? "#E8934A" : "#5B7FDE"} />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  );
}
