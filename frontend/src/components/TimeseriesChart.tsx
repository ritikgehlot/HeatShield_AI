import React from 'react';
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from 'recharts';

interface TimeseriesDataPoint {
  time: string;
  [key: string]: string | number;
}

interface SeriesConfig {
  dataKey: string;
  label: string;
  color: string;
}

interface TimeseriesChartProps {
  data: TimeseriesDataPoint[];
  series: SeriesConfig[];
  title: string;
  subtitle?: string;
  className?: string;
}

const CustomTooltip = ({ active, payload, label }: any) => {
  if (!active || !payload?.length) return null;
  return (
    <div className="glass-card-static p-3 text-xs min-w-[150px]">
      <p className="text-[#94a3b8] mb-2">{label}</p>
      {payload.map((entry: any, i: number) => (
        <div key={i} className="flex items-center justify-between gap-4 mb-1">
          <div className="flex items-center gap-1.5">
            <span
              className="w-2 h-2 rounded-full"
              style={{ backgroundColor: entry.color }}
            />
            <span className="text-[#f1f5f9]">{entry.name}</span>
          </div>
          <span className="font-medium text-[#f1f5f9]">
            {typeof entry.value === 'number' ? entry.value.toFixed(2) : entry.value}
          </span>
        </div>
      ))}
    </div>
  );
};

export const TimeseriesChart: React.FC<TimeseriesChartProps> = ({
  data,
  series,
  title,
  subtitle,
  className = '',
}) => {
  return (
    <div className={`glass-card p-5 ${className}`}>
      <h3 className="text-sm font-semibold text-[#f1f5f9] mb-0.5">{title}</h3>
      {subtitle && <p className="text-xs text-[#64748b] mb-4">{subtitle}</p>}
      <div className="h-64">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={data}>
            <defs>
              {series.map((s) => (
                <linearGradient
                  key={s.dataKey}
                  id={`gradient-${s.dataKey}`}
                  x1="0"
                  y1="0"
                  x2="0"
                  y2="1"
                >
                  <stop offset="5%" stopColor={s.color} stopOpacity={0.3} />
                  <stop offset="95%" stopColor={s.color} stopOpacity={0} />
                </linearGradient>
              ))}
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#1a2332" vertical={false} />
            <XAxis
              dataKey="time"
              tick={{ fill: '#94a3b8', fontSize: 11 }}
              axisLine={{ stroke: '#1a2332' }}
              tickLine={false}
            />
            <YAxis
              tick={{ fill: '#94a3b8', fontSize: 11 }}
              axisLine={false}
              tickLine={false}
            />
            <Tooltip content={<CustomTooltip />} />
            <Legend
              wrapperStyle={{ fontSize: 11, color: '#94a3b8' }}
              iconType="circle"
              iconSize={8}
            />
            {series.map((s) => (
              <Area
                key={s.dataKey}
                type="monotone"
                dataKey={s.dataKey}
                name={s.label}
                stroke={s.color}
                fill={`url(#gradient-${s.dataKey})`}
                strokeWidth={2}
                dot={false}
                activeDot={{ r: 4, fill: s.color }}
              />
            ))}
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};
