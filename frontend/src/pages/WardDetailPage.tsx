import { useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { ArrowLeft, Download, MapPinned, SlidersHorizontal } from "lucide-react";
import { useWardDetail, useWardReport } from "@/hooks/useApi";
import { RiskPill } from "@/components/ui/RiskPill";
import { DataBadgeChip } from "@/components/ui/DataBadgeChip";
import { Button, ErrorState, Skeleton } from "@/components/ui/Primitives";
import { FactorContributionChart } from "@/components/charts/FactorContributionChart";
import { formatDateTime, formatFriendlyFeature, formatNumber, formatRange } from "@/lib/format";
import { FEATURE_DEFINITIONS } from "@/lib/featureDefinitions";

export function WardDetailPage() {
  const { wardId } = useParams();
  const id = Number(wardId);
  const navigate = useNavigate();
  const { data: ward, isLoading, isError, refetch } = useWardDetail(id);
  const [showReport, setShowReport] = useState(false);
  const { data: report, isLoading: reportLoading } = useWardReport(showReport ? id : undefined);

  if (isLoading || !ward) {
    return (
      <div className="space-y-4">
        <Skeleton className="h-8 w-48" />
        <Skeleton className="h-40" />
        <Skeleton className="h-64" />
      </div>
    );
  }
  if (isError) return <ErrorState title="Couldn't load this ward" onRetry={() => refetch()} />;

  const wardData = ward; // narrowed non-null below this point (early returns above guard it)

  function downloadReport() {
    if (!report) {
      setShowReport(true);
      return;
    }
    const blob = new Blob([JSON.stringify(report, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `heatshield-ward-${wardData.id}-report.json`;
    a.click();
    URL.revokeObjectURL(url);
  }

  return (
    <div className="animate-fade-up space-y-6">
      <button onClick={() => navigate(-1)} className="flex items-center gap-1.5 text-sm text-ink-muted hover:text-ink">
        <ArrowLeft size={15} /> Back
      </button>

      <header className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <p className="mono-tag mb-1">{ward.city} · Ward</p>
          <h1 className="font-display text-3xl font-semibold text-ink">{ward.name}</h1>
          <div className="mt-2 flex items-center gap-3">
            <RiskPill category={ward.category} size="lg" />
            <span className="font-mono text-sm text-ink-muted">{ward.score?.toFixed(1) ?? "—"}/100 · confidence {ward.confidence !== null ? Math.round(ward.confidence * 100) : "—"}%</span>
          </div>
        </div>
        <div className="flex gap-2">
          <Button variant="secondary" icon={SlidersHorizontal} onClick={() => navigate(`/simulator/${ward.id}`)}>
            Run What-If
          </Button>
          <Button variant="secondary" icon={Download} onClick={downloadReport} disabled={showReport && reportLoading}>
            {showReport && reportLoading ? "Preparing…" : "Download report"}
          </Button>
        </div>
      </header>

      {ward.is_demo_geometry && (
        <div className="flex items-center gap-2 rounded-lg border border-risk-moderate/30 bg-risk-moderate/[0.06] px-3 py-2 text-xs text-ink-muted">
          <MapPinned size={14} className="text-risk-moderate" />
          This ward boundary is a simplified placeholder, not an official municipal boundary. Upload real GeoJSON on the Data Sources page to replace it.
        </div>
      )}

      <div className="grid grid-cols-1 gap-5 lg:grid-cols-[1fr_1.1fr]">
        {/* Explanation */}
        <div className="glass-card p-5">
          <div className="mb-3 flex items-center justify-between">
            <p className="font-display text-base font-medium text-ink">Why this score</p>
            <DataBadgeChip badge={{ source: ward.feature_source, mode: "demo", observed_at: ward.feature_observed_at, fetched_at: null, confidence: ward.feature_confidence, message: `Feature data confidence: ${Math.round(ward.feature_confidence * 100)}%` }} />
          </div>
          <p className="mb-4 text-sm leading-relaxed text-ink-muted">{ward.explanation}</p>
          <FactorContributionChart factors={ward.top_factors} />
          {ward.missing_data_warnings.length > 0 && (
            <div className="mt-4 space-y-1 rounded-lg border border-risk-moderate/30 bg-risk-moderate/[0.06] p-3 text-xs text-ink-muted">
              {ward.missing_data_warnings.map((w, i) => (
                <p key={i}>⚠ {w}</p>
              ))}
            </div>
          )}
        </div>

        {/* Features + recommendations */}
        <div className="flex flex-col gap-5">
          <div className="glass-card p-5">
            <p className="mb-3 font-display text-base font-medium text-ink">Ward conditions</p>
            <dl className="grid grid-cols-2 gap-x-4 gap-y-3 text-sm">
              {Object.entries(ward.features)
                .filter(([, v]) => v !== null)
                .map(([key, value]) => (
                  <div key={key} title={FEATURE_DEFINITIONS[key] ?? ""}>
                    <dt className="mono-tag cursor-help">{formatFriendlyFeature(key)}</dt>
                    <dd className="text-ink">{formatNumber(value as number, key.includes("pct") || key === "vulnerability_index" ? 0 : 1)}</dd>
                  </div>
                ))}
            </dl>
          </div>

          <div className="glass-card p-5">
            <div className="mb-3 flex items-center justify-between">
              <p className="font-display text-base font-medium text-ink">Recommended interventions</p>
              {!showReport && (
                <button onClick={() => setShowReport(true)} className="text-xs text-brand hover:underline">
                  Load ranked list →
                </button>
              )}
            </div>
            {!showReport && <p className="text-sm text-ink-muted">Quick suggestions: {ward.recommendations.join(" · ")}</p>}
            {showReport && reportLoading && <Skeleton className="h-32" />}
            {showReport && report && (
              <div className="space-y-3">
                {report.recommended_interventions.slice(0, 4).map((rec) => (
                  <div key={rec.key} className="rounded-lg border border-border p-3">
                    <div className="flex items-center justify-between">
                      <p className="text-sm font-medium text-ink">
                        #{rec.priority_rank} {rec.name}
                      </p>
                      <span className="mono-tag">{rec.confidence} confidence</span>
                    </div>
                    <p className="mt-1 text-xs text-ink-muted">{rec.why_selected}</p>
                    <div className="mt-2 flex flex-wrap gap-x-4 gap-y-1 font-mono text-[11px] text-ink-faint">
                      <span>Risk −{formatRange(rec.risk_reduction_range)} pts</span>
                      <span>₹{formatRange(rec.cost_range_inr_lakh)}L</span>
                      <span>{formatRange(rec.timeline_weeks)} wks</span>
                    </div>
                  </div>
                ))}
                <p className="text-[11px] text-ink-faint">{report.disclaimer}</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
