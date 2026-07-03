import React from 'react';

interface InterventionCardProps {
  name: string;
  description: string;
  impact: number;
  priority: 'high' | 'medium' | 'low';
}

const PRIORITY_STYLES = {
  high: { bg: 'rgba(239, 68, 68, 0.1)', border: 'rgba(239, 68, 68, 0.3)', text: '#f87171', label: 'High Priority' },
  medium: { bg: 'rgba(251, 191, 36, 0.1)', border: 'rgba(251, 191, 36, 0.3)', text: '#fbbf24', label: 'Medium Priority' },
  low: { bg: 'rgba(34, 197, 94, 0.1)', border: 'rgba(34, 197, 94, 0.3)', text: '#4ade80', label: 'Low Priority' },
};

export const InterventionCard: React.FC<InterventionCardProps> = ({
  name,
  description,
  impact,
  priority,
}) => {
  const style = PRIORITY_STYLES[priority];

  return (
    <div className="glass-card p-4">
      <div className="flex items-start justify-between mb-2">
        <h4 className="text-sm font-semibold text-[#f1f5f9]">{name}</h4>
        <span
          className="text-[10px] font-semibold px-2 py-0.5 rounded-full uppercase tracking-wider"
          style={{ backgroundColor: style.bg, border: `1px solid ${style.border}`, color: style.text }}
        >
          {style.label}
        </span>
      </div>
      <p className="text-xs text-[#94a3b8] mb-3">{description}</p>
      <div className="flex items-center gap-2">
        <span className="text-xs text-[#64748b]">Impact:</span>
        <div className="flex-1 h-1.5 bg-[#1a2332] rounded-full overflow-hidden">
          <div
            className="h-full rounded-full transition-all duration-500"
            style={{
              width: `${impact * 100}%`,
              backgroundColor: style.text,
            }}
          />
        </div>
        <span className="text-xs font-medium" style={{ color: style.text }}>
          {(impact * 100).toFixed(0)}%
        </span>
      </div>
    </div>
  );
};
