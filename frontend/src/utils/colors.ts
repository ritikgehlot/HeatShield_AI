/**
 * HeatShield AI — Risk Color Scales & Utilities
 * Scores are 0–100 from the backend.
 */

export type RiskLevel = 'low' | 'moderate' | 'high' | 'severe' | 'extreme';

export interface RiskConfig {
  label: string;
  color: string;
  bgColor: string;
  borderColor: string;
  mapColor: string;
  cssClass: string;
}

export const RISK_CONFIGS: Record<RiskLevel, RiskConfig> = {
  low: {
    label: 'Low',
    color: '#4ade80',
    bgColor: 'rgba(34, 197, 94, 0.15)',
    borderColor: 'rgba(34, 197, 94, 0.3)',
    mapColor: '#22c55e',
    cssClass: 'risk-low',
  },
  moderate: {
    label: 'Moderate',
    color: '#fbbf24',
    bgColor: 'rgba(251, 191, 36, 0.15)',
    borderColor: 'rgba(251, 191, 36, 0.3)',
    mapColor: '#fbbf24',
    cssClass: 'risk-moderate',
  },
  high: {
    label: 'High',
    color: '#fb923c',
    bgColor: 'rgba(249, 115, 22, 0.15)',
    borderColor: 'rgba(249, 115, 22, 0.3)',
    mapColor: '#f97316',
    cssClass: 'risk-high',
  },
  severe: {
    label: 'Severe',
    color: '#f87171',
    bgColor: 'rgba(239, 68, 68, 0.15)',
    borderColor: 'rgba(239, 68, 68, 0.3)',
    mapColor: '#ef4444',
    cssClass: 'risk-severe',
  },
  extreme: {
    label: 'Extreme',
    color: '#fca5a5',
    bgColor: 'rgba(168, 34, 34, 0.2)',
    borderColor: 'rgba(239, 68, 68, 0.4)',
    mapColor: '#dc2626',
    cssClass: 'risk-extreme',
  },
};

/** Map a 0–100 score to a risk level. */
export function scoreToRiskLevel(score: number): RiskLevel {
  if (score >= 80) return 'extreme';
  if (score >= 60) return 'severe';
  if (score >= 40) return 'high';
  if (score >= 20) return 'moderate';
  return 'low';
}

/** Map a risk level string from backend to our key. */
export function labelToRiskLevel(label: string): RiskLevel {
  const l = label.toLowerCase();
  if (l === 'extreme') return 'extreme';
  if (l === 'severe') return 'severe';
  if (l === 'high') return 'high';
  if (l === 'moderate') return 'moderate';
  return 'low';
}

export function getRiskConfig(score: number): RiskConfig {
  return RISK_CONFIGS[scoreToRiskLevel(score)];
}

export function getRiskColor(score: number): string {
  return getRiskConfig(score).mapColor;
}

export const CHART_COLORS = {
  orange: '#f97316',
  amber: '#fbbf24',
  green: '#22c55e',
  cyan: '#06b6d4',
  red: '#ef4444',
  blue: '#3b82f6',
  purple: '#a855f7',
  pink: '#ec4899',
};

export const KPI_COLORS = {
  orange: { text: '#f97316', bg: 'rgba(249, 115, 22, 0.1)', border: 'rgba(249, 115, 22, 0.2)' },
  red: { text: '#ef4444', bg: 'rgba(239, 68, 68, 0.1)', border: 'rgba(239, 68, 68, 0.2)' },
  green: { text: '#22c55e', bg: 'rgba(34, 197, 94, 0.1)', border: 'rgba(34, 197, 94, 0.2)' },
  blue: { text: '#3b82f6', bg: 'rgba(59, 130, 246, 0.1)', border: 'rgba(59, 130, 246, 0.2)' },
  cyan: { text: '#06b6d4', bg: 'rgba(6, 182, 212, 0.1)', border: 'rgba(6, 182, 212, 0.2)' },
};
