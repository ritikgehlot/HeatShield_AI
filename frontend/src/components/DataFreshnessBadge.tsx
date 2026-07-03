import React from 'react';
import { Clock } from 'lucide-react';
import { formatRelativeTime, getFreshnessColor } from '../utils/format';

interface DataFreshnessBadgeProps {
  timestamp: string;
  source?: string;
}

const FRESHNESS_STYLES = {
  green: { bg: 'rgba(34, 197, 94, 0.1)', border: 'rgba(34, 197, 94, 0.3)', text: '#4ade80' },
  amber: { bg: 'rgba(251, 191, 36, 0.1)', border: 'rgba(251, 191, 36, 0.3)', text: '#fbbf24' },
  red: { bg: 'rgba(239, 68, 68, 0.1)', border: 'rgba(239, 68, 68, 0.3)', text: '#f87171' },
};

export const DataFreshnessBadge: React.FC<DataFreshnessBadgeProps> = ({
  timestamp,
  source,
}) => {
  const freshness = getFreshnessColor(timestamp);
  const style = FRESHNESS_STYLES[freshness];
  const relTime = formatRelativeTime(timestamp);

  return (
    <div
      className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-medium"
      style={{
        backgroundColor: style.bg,
        border: `1px solid ${style.border}`,
        color: style.text,
      }}
      title={`Last updated: ${new Date(timestamp).toLocaleString()}${source ? ` • Source: ${source}` : ''}`}
    >
      <Clock className="w-3 h-3" />
      <span>Updated {relTime}</span>
    </div>
  );
};
