import { labelToRiskLevel, RISK_CONFIGS } from '../utils/colors';

interface RiskBadgeProps {
  level: string;
  score: number;
}

export default function RiskBadge({ level, score }: RiskBadgeProps) {
  const riskLevel = labelToRiskLevel(level);
  const config = RISK_CONFIGS[riskLevel];

  return (
    <span className={`inline-flex items-center gap-1.5 px-2 py-0.5 text-[10px] font-bold rounded-full ${config.cssClass}`}>
      <span className="w-1.5 h-1.5 rounded-full" style={{ backgroundColor: config.color }} />
      {config.label}
      <span className="opacity-70">{score.toFixed(0)}</span>
    </span>
  );
}
