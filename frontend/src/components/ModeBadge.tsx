import { AlertTriangle, Radio } from 'lucide-react';

interface Props {
  mode: 'demo' | 'live';
}

export default function ModeBadge({ mode }: Props) {
  if (mode === 'live') {
    return (
      <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full text-xs font-bold bg-emerald-500/10 border border-emerald-500/30 text-emerald-400">
        <Radio className="w-3 h-3" />
        <span className="relative flex h-2 w-2">
          <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-500 opacity-75" />
          <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500" />
        </span>
        LIVE DATA
      </div>
    );
  }

  return (
    <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full text-xs font-bold bg-amber-500/10 border border-amber-500/30 text-amber-400">
      <AlertTriangle className="w-3 h-3" />
      ⚠ DEMO DATA — Not real-time
    </div>
  );
}
