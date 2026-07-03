import React from 'react';
import { Wifi, WifiOff, AlertCircle, Clock, Database } from 'lucide-react';
import { formatRelativeTime } from '../utils/format';

interface DataSourceCardProps {
  provider: string;
  status: 'connected' | 'disconnected' | 'error';
  lastRefresh: string;
  mode: 'live' | 'demo';
  description: string;
  recordsCount?: number;
}

const STATUS_CONFIG = {
  connected: {
    icon: Wifi,
    label: 'Connected',
    bg: 'rgba(34, 197, 94, 0.1)',
    border: 'rgba(34, 197, 94, 0.3)',
    text: '#4ade80',
    dot: '#22c55e',
  },
  disconnected: {
    icon: WifiOff,
    label: 'Disconnected',
    bg: 'rgba(148, 163, 184, 0.1)',
    border: 'rgba(148, 163, 184, 0.2)',
    text: '#94a3b8',
    dot: '#64748b',
  },
  error: {
    icon: AlertCircle,
    label: 'Error',
    bg: 'rgba(239, 68, 68, 0.1)',
    border: 'rgba(239, 68, 68, 0.3)',
    text: '#f87171',
    dot: '#ef4444',
  },
};

export const DataSourceCard: React.FC<DataSourceCardProps> = ({
  provider,
  status,
  lastRefresh,
  mode,
  description,
  recordsCount,
}) => {
  const config = STATUS_CONFIG[status];
  const StatusIcon = config.icon;

  return (
    <div className="glass-card p-5">
      {/* Header */}
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center gap-3">
          <div
            className="w-10 h-10 rounded-xl flex items-center justify-center"
            style={{ backgroundColor: config.bg, border: `1px solid ${config.border}` }}
          >
            <StatusIcon className="w-5 h-5" style={{ color: config.text }} />
          </div>
          <div>
            <h3 className="text-sm font-semibold text-[#f1f5f9]">{provider}</h3>
            <div className="flex items-center gap-2 mt-0.5">
              <span
                className="w-1.5 h-1.5 rounded-full"
                style={{ backgroundColor: config.dot }}
              />
              <span className="text-xs" style={{ color: config.text }}>{config.label}</span>
            </div>
          </div>
        </div>
        <span
          className={`text-[10px] font-semibold px-2 py-0.5 rounded-full uppercase tracking-wider ${
            mode === 'live'
              ? 'bg-[rgba(34,197,94,0.1)] border border-[rgba(34,197,94,0.3)] text-[#4ade80]'
              : 'bg-[rgba(251,191,36,0.1)] border border-[rgba(251,191,36,0.3)] text-[#fbbf24]'
          }`}
        >
          {mode}
        </span>
      </div>

      {/* Description */}
      <p className="text-xs text-[#94a3b8] mb-4">{description}</p>

      {/* Footer */}
      <div className="flex items-center justify-between text-xs text-[#64748b]">
        <div className="flex items-center gap-1.5">
          <Clock className="w-3 h-3" />
          <span>{formatRelativeTime(lastRefresh)}</span>
        </div>
        {recordsCount !== undefined && (
          <div className="flex items-center gap-1.5">
            <Database className="w-3 h-3" />
            <span>{recordsCount.toLocaleString()} records</span>
          </div>
        )}
      </div>
    </div>
  );
};
