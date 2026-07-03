import { KPI_COLORS } from '../utils/colors';
import type { LucideIcon } from 'lucide-react';

interface KpiCardProps {
  title: string;
  value: string | number;
  subtitle: string;
  icon: LucideIcon;
  color: 'orange' | 'red' | 'green' | 'blue' | 'cyan';
}

export default function KpiCard({ title, value, subtitle, icon: Icon, color }: KpiCardProps) {
  const c = KPI_COLORS[color];

  return (
    <div className="glass-card p-5 flex flex-col gap-3" style={{ borderColor: c.border }}>
      <div className="flex items-center justify-between">
        <div className="w-10 h-10 rounded-xl flex items-center justify-center"
             style={{ background: c.bg, border: `1px solid ${c.border}` }}>
          <Icon className="w-5 h-5" style={{ color: c.text }} />
        </div>
      </div>
      <div>
        <div className="text-2xl font-bold text-white tracking-tight">{value}</div>
        <div className="text-[10px] font-bold text-slate-500 mt-0.5 uppercase tracking-wider">{title}</div>
      </div>
      <div className="text-xs text-slate-600 leading-relaxed">{subtitle}</div>
    </div>
  );
}
