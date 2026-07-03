import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts';
import { RISK_CONFIGS, scoreToRiskLevel, type RiskLevel } from '../utils/colors';

interface Ward {
  risk_score: number;
}

interface Props {
  wards: Ward[];
}

const levels: RiskLevel[] = ['low', 'moderate', 'high', 'severe', 'extreme'];

const CustomTooltip = ({ active, payload, label }: any) => {
  if (!active || !payload?.length) return null;
  return (
    <div className="glass-card-static p-3 text-xs">
      <p className="text-white font-bold mb-1">{label} Risk</p>
      <p className="text-slate-400">{payload[0].value} wards</p>
    </div>
  );
};

export default function RiskDistributionChart({ wards }: Props) {
  const counts: Record<RiskLevel, number> = { low: 0, moderate: 0, high: 0, severe: 0, extreme: 0 };
  wards.forEach(w => { counts[scoreToRiskLevel(w.risk_score)]++; });

  const data = levels.map(level => ({
    level: RISK_CONFIGS[level].label,
    count: counts[level],
    color: RISK_CONFIGS[level].mapColor,
  }));

  return (
    <div className="h-52">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={data} barCategoryGap="20%">
          <CartesianGrid strokeDasharray="3 3" stroke="#1a2332" vertical={false} />
          <XAxis dataKey="level" tick={{ fill: '#94a3b8', fontSize: 11 }} axisLine={{ stroke: '#1a2332' }} tickLine={false} />
          <YAxis tick={{ fill: '#94a3b8', fontSize: 11 }} axisLine={false} tickLine={false} allowDecimals={false} />
          <Tooltip content={<CustomTooltip />} cursor={{ fill: 'rgba(148,163,184,0.05)' }} />
          <Bar dataKey="count" radius={[6, 6, 0, 0]} maxBarSize={48}>
            {data.map((entry, i) => <Cell key={i} fill={entry.color} fillOpacity={0.85} />)}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
