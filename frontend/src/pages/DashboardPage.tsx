import { useNavigate } from "react-router-dom";
import { AlertTriangle, CloudSun, Leaf, Satellite, ThermometerSun, Users } from "lucide-react";
import { useSelectedCity } from "@/lib/CityContext";
import { useDashboard } from "@/hooks/useApi";
import { HeatMap } from "@/components/map/HeatMap";
import { RiskDistributionChart, WardComparisonChart } from "@/components/charts/DashboardCharts";
import { StatCard, Skeleton, ErrorState } from "@/components/ui/Primitives";
import { RiskPill } from "@/components/ui/RiskPill";
import { DataBadgeChip } from "@/components/ui/DataBadgeChip";
import { formatCompactPeople, formatDateTime, formatPct } from "@/lib/format";

export function DashboardPage() {
  const { cityId } = useSelectedCity();
  const navigate = useNavigate();
  const { data, isLoading, isError, refetch } = useDashboard(cityId);

  if (isLoading || !data) {
    return (
      <div className="space-y-6">
        <Skeleton className="h-8 w-64" />
        <div className="grid grid-cols-2 gap-4 lg:grid-cols-6">
          {Array.from({ length: 6 }).map((_, i) => (
            <Skeleton key={i} className="h-28" />
          ))}
        </div>
        <Skeleton className="h-[480px]" />
      </div>
    );
  }

  if (isError) {
    return <ErrorState title="Couldn't load the dashboard" description="The backend may still be starting up." onRetry={() => refetch()} />;
  }

  const priorityWards = [...data.wards].sort((a, b) => (b.score ?? 0) - (a.score ?? 0)).slice(0, 8);

  return (
    <div className="animate-fade-up space-y-6">
      <header className="flex flex-wrap items-end justify-between gap-3">
        <div>
          <p className="mono-tag mb-1">{data.city.name}, {data.city.state} · generated {formatDateTime(data.generated_at)}</p>
          <h1 className="font-display text-2xl font-semibold text-ink">Urban Heat Dashboard</h1>
        </div>
        <RiskPill category={data.kpis.city_heat_category} size="lg" />
      </header>

      {/* KPI row */}
      <div className="grid grid-cols-2 gap-4 lg:grid-cols-6">
        <StatCard label="City heat risk" value={data.kpis.city_heat_risk?.toFixed(0) ?? "—"} unit="/100" tone="risk" icon={ThermometerSun} />
        <StatCard label="Severe + extreme wards" value={data.kpis.severe_or_extreme_wards} unit={`/ ${data.kpis.total_wards}`} tone="risk" icon={AlertTriangle} />
        <StatCard label="Population exposed" value={formatCompactPeople(data.kpis.estimated_population_exposed)} tone="risk" icon={Users} footnote="In severe/extreme wards" />
        <StatCard label="Green cover deficit" value={formatPct(data.kpis.green_cover_deficit_pct)} tone="green" icon={Leaf} footnote="vs. 0.5 NDVI reference" />
        <StatCard
          label="Latest weather"
          value={data.weather.air_temp_c !== null ? `${data.weather.air_temp_c.toFixed(0)}°` : "—"}
          unit="C"
          icon={CloudSun}
          footnote={<DataBadgeChip badge={data.weather.badge} compact />}
        />
        <StatCard
          label="Satellite scene"
          value={data.satellite.lst_c !== null ? `${data.satellite.lst_c.toFixed(0)}°` : "—"}
          unit="C LST"
          icon={Satellite}
          footnote={<DataBadgeChip badge={data.satellite.badge} compact />}
        />
      </div>

      {/* Map + charts */}
      <div className="grid grid-cols-1 gap-4 xl:grid-cols-[1.6fr_1fr]">
        <div className="h-[480px]">
          <HeatMap wards={data.wards} centerLat={data.city.center_lat} centerLon={data.city.center_lon} onSelectWard={(id) => navigate(`/wards/${id}`)} />
        </div>
        <div className="glass-card flex flex-col gap-5 p-5">
          <div>
            <p className="mb-2 text-sm font-medium text-ink">Risk distribution</p>
            <RiskDistributionChart wards={data.wards} />
          </div>
          <div className="border-t border-border pt-4">
            <p className="mb-2 text-sm font-medium text-ink">Top 10 wards by risk</p>
            <WardComparisonChart wards={data.wards} onSelectWard={(id) => navigate(`/wards/${id}`)} />
          </div>
        </div>
      </div>

      {/* Priority wards table */}
      <div className="glass-card overflow-hidden">
        <div className="flex items-center justify-between border-b border-border px-5 py-4">
          <p className="font-display text-base font-medium text-ink">Priority wards</p>
          <p className="mono-tag">{priorityWards.length} shown</p>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead>
              <tr className="border-b border-border text-xs uppercase tracking-wide text-ink-faint">
                <th className="px-5 py-2.5 font-medium">Ward</th>
                <th className="px-5 py-2.5 font-medium">Score</th>
                <th className="px-5 py-2.5 font-medium">Category</th>
                <th className="px-5 py-2.5 font-medium">Population</th>
                <th className="px-5 py-2.5 font-medium">Updated</th>
                <th className="px-5 py-2.5 font-medium"></th>
              </tr>
            </thead>
            <tbody>
              {priorityWards.map((ward) => (
                <tr
                  key={ward.id}
                  className="cursor-pointer border-b border-border/60 last:border-0 hover:bg-surface-hi/40"
                  onClick={() => navigate(`/wards/${ward.id}`)}
                >
                  <td className="px-5 py-3 font-medium text-ink">{ward.name}</td>
                  <td className="px-5 py-3 font-mono text-ink-muted">{ward.score?.toFixed(1) ?? "—"}</td>
                  <td className="px-5 py-3">
                    <RiskPill category={ward.category} size="sm" />
                  </td>
                  <td className="px-5 py-3 text-ink-muted">{formatCompactPeople(ward.population)}</td>
                  <td className="px-5 py-3 text-ink-faint">{formatDateTime(ward.last_updated)}</td>
                  <td className="px-5 py-3 text-right text-brand">View →</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
