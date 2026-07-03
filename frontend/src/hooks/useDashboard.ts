/**
 * HeatShield AI — Dashboard State Hook
 */
import { useState, useMemo, useCallback } from 'react';
import { useDashboardData } from './useApi';
import type { WardRisk, DashboardData } from '../api/client';
import { scoreToRiskLevel } from '../utils/colors';

export interface DashboardState {
  data: DashboardData | undefined;
  isLoading: boolean;
  isError: boolean;
  error: Error | null;
  refetch: () => void;
  selectedWardId: string | null;
  setSelectedWardId: (id: string | null) => void;
  selectedWard: WardRisk | null;
  topPriorityWards: WardRisk[];
  riskDistribution: { level: string; count: number; color: string }[];
  cityName: string;
  isDemo: boolean;
}

const RISK_CHART_COLORS: Record<string, string> = {
  low: '#22c55e',
  moderate: '#fbbf24',
  high: '#f97316',
  severe: '#ef4444',
  extreme: '#dc2626',
};

export function useDashboard(city?: string): DashboardState {
  const { data, isLoading, isError, error, refetch } = useDashboardData(city);
  const [selectedWardId, setSelectedWardId] = useState<string | null>(null);

  const selectedWard = useMemo(() => {
    if (!data || !selectedWardId) return null;
    return data.wards.find((w) => w.ward_id === selectedWardId) ?? null;
  }, [data, selectedWardId]);

  const topPriorityWards = useMemo(() => {
    if (!data) return [];
    return [...data.wards]
      .sort((a, b) => b.risk_score - a.risk_score)
      .slice(0, 5);
  }, [data]);

  const riskDistribution = useMemo(() => {
    if (!data) return [];
    // Either use backend distribution or compute from wards
    if (data.risk_distribution && Object.keys(data.risk_distribution).length > 0) {
      return Object.entries(data.risk_distribution).map(([level, count]) => ({
        level: level.charAt(0).toUpperCase() + level.slice(1),
        count,
        color: RISK_CHART_COLORS[level] || '#94a3b8',
      }));
    }
    // Compute from wards
    const dist: Record<string, number> = { low: 0, moderate: 0, high: 0, severe: 0, extreme: 0 };
    data.wards.forEach((w) => {
      const level = scoreToRiskLevel(w.risk_score);
      dist[level]++;
    });
    return Object.entries(dist).map(([level, count]) => ({
      level: level.charAt(0).toUpperCase() + level.slice(1),
      count,
      color: RISK_CHART_COLORS[level] || '#94a3b8',
    }));
  }, [data]);

  const handleSetSelectedWardId = useCallback((id: string | null) => {
    setSelectedWardId(id);
  }, []);

  return {
    data,
    isLoading,
    isError,
    error: error as Error | null,
    refetch,
    selectedWardId,
    setSelectedWardId: handleSetSelectedWardId,
    selectedWard,
    topPriorityWards,
    riskDistribution,
    cityName: data?.city ?? 'Jodhpur',
    isDemo: data?.mode === 'demo',
  };
}
