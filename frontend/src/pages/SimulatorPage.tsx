import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import * as Slider from "@radix-ui/react-slider";
import { ArrowRight, IndianRupee, TreePine, Umbrella } from "lucide-react";
import { useSelectedCity } from "@/lib/CityContext";
import { useDashboard, useCreateSimulation } from "@/hooks/useApi";
import { RiskPill } from "@/components/ui/RiskPill";
import { Button, EmptyState, Skeleton } from "@/components/ui/Primitives";
import { thermalColorForScore } from "@/lib/risk";

function SliderRow({ label, value, onChange, min, max, step, unit, icon: Icon }: { label: string; value: number; onChange: (v: number) => void; min: number; max: number; step: number; unit: string; icon: typeof TreePine }) {
  return (
    <div>
      <div className="mb-2 flex items-center justify-between">
        <label className="flex items-center gap-1.5 text-sm text-ink">
          <Icon size={15} className="text-ink-faint" />
          {label}
        </label>
        <span className="font-mono text-sm text-brand">
          {value}
          {unit}
        </span>
      </div>
      <Slider.Root
        className="relative flex h-5 w-full touch-none items-center"
        value={[value]}
        onValueChange={([v]) => onChange(v)}
        min={min}
        max={max}
        step={step}
      >
        <Slider.Track className="relative h-1.5 grow rounded-full bg-surface-hi">
          <Slider.Range className="absolute h-full rounded-full bg-brand" />
        </Slider.Track>
        <Slider.Thumb className="block h-4 w-4 rounded-full border-2 border-brand bg-canvas shadow-glow-brand focus-visible:outline-none" aria-label={label} />
      </Slider.Root>
    </div>
  );
}

export function SimulatorPage() {
  const { wardId } = useParams();
  const { cityId } = useSelectedCity();
  const { data: dashboard, isLoading: dashboardLoading } = useDashboard(cityId);
  const [selectedWardId, setSelectedWardId] = useState<number | undefined>(wardId ? Number(wardId) : undefined);
  const [budget, setBudget] = useState(20);
  const [roofPct, setRoofPct] = useState(25);
  const [treePct, setTreePct] = useState(8);
  const [shadeUnits, setShadeUnits] = useState(10);
  const simulate = useCreateSimulation();

  useEffect(() => {
    if (!selectedWardId && dashboard?.wards.length) {
      setSelectedWardId([...dashboard.wards].sort((a, b) => (b.score ?? 0) - (a.score ?? 0))[0].id);
    }
  }, [dashboard, selectedWardId]);

  function runSimulation() {
    if (!selectedWardId) return;
    simulate.mutate({ ward_id: selectedWardId, budget_inr_lakh: budget, roof_treatment_pct: roofPct, tree_canopy_target_pct: treePct, shade_structures: shadeUnits });
  }

  if (dashboardLoading || !dashboard) return <Skeleton className="h-96" />;

  const wardOptions = [...dashboard.wards].sort((a, b) => (b.score ?? 0) - (a.score ?? 0));
  const result = simulate.data;

  return (
    <div className="animate-fade-up space-y-6">
      <header>
        <p className="mono-tag mb-1">Decision support · not a final policy recommendation</p>
        <h1 className="font-display text-2xl font-semibold text-ink">What-If Intervention Simulator</h1>
      </header>

      <div className="grid grid-cols-1 gap-5 lg:grid-cols-[1fr_1.1fr]">
        <div className="glass-card space-y-6 p-5">
          <div>
            <label className="mono-tag mb-2 block">Ward</label>
            <select
              value={selectedWardId ?? ""}
              onChange={(e) => setSelectedWardId(Number(e.target.value))}
              className="w-full rounded-lg border border-border-strong bg-canvas-raised px-3 py-2 text-sm text-ink outline-none focus-visible:border-brand"
            >
              {wardOptions.map((w) => (
                <option key={w.id} value={w.id}>
                  {w.name} — {w.score?.toFixed(0) ?? "—"}/100 ({w.category ?? "no data"})
                </option>
              ))}
            </select>
          </div>

          <SliderRow label="Budget" value={budget} onChange={setBudget} min={1} max={200} step={1} unit=" L" icon={IndianRupee} />
          <SliderRow label="Cool-roof treatment coverage" value={roofPct} onChange={setRoofPct} min={0} max={100} step={5} unit="%" icon={Umbrella} />
          <SliderRow label="Tree canopy gain target" value={treePct} onChange={setTreePct} min={0} max={30} step={1} unit="%" icon={TreePine} />
          <SliderRow label="Shade structures" value={shadeUnits} onChange={setShadeUnits} min={0} max={100} step={5} unit=" units" icon={Umbrella} />

          <Button onClick={runSimulation} disabled={!selectedWardId || simulate.isPending} className="w-full">
            {simulate.isPending ? "Simulating…" : "Run simulation"}
          </Button>
          {simulate.isError && <p className="text-xs text-risk-extreme">{(simulate.error as Error).message}</p>}
        </div>

        <div className="glass-card p-5">
          {!result && !simulate.isPending && (
            <EmptyState title="No simulation run yet" description="Adjust the controls and press Run simulation to see a baseline-vs-projected comparison." />
          )}
          {simulate.isPending && <Skeleton className="h-72" />}
          {result && (
            <div className="space-y-5">
              <p className="font-display text-base font-medium text-ink">{result.ward_name}: baseline vs. projected</p>
              <div className="flex items-center justify-center gap-4">
                <div className="text-center">
                  <p className="mono-tag mb-1">Baseline</p>
                  <p className="font-display text-4xl font-semibold" style={{ color: thermalColorForScore(result.baseline_score) }}>
                    {result.baseline_score.toFixed(0)}
                  </p>
                  <RiskPill category={result.baseline_category} size="sm" />
                </div>
                <ArrowRight className="text-ink-faint" />
                <div className="text-center">
                  <p className="mono-tag mb-1">Projected</p>
                  <p className="font-display text-4xl font-semibold" style={{ color: thermalColorForScore(result.projected_score) }}>
                    {result.projected_score.toFixed(0)}
                  </p>
                  <RiskPill category={result.projected_category} size="sm" />
                </div>
              </div>

              <div className="rounded-lg border border-green/30 bg-green-soft p-3 text-center">
                <p className="font-display text-2xl font-semibold text-green">−{result.risk_reduction_pts.toFixed(1)} pts</p>
                <p className="text-xs text-ink-muted">
                  Estimated range: −{result.risk_reduction_range_pts[0]} to −{result.risk_reduction_range_pts[1]} pts
                </p>
              </div>

              {result.allocations.length > 0 && (
                <div>
                  <p className="mb-2 text-sm font-medium text-ink">Indicative budget allocation</p>
                  <div className="space-y-1.5">
                    {result.allocations.map((a) => (
                      <div key={a.key} className="flex items-center justify-between text-sm">
                        <span className="text-ink-muted">{a.label}</span>
                        <span className="font-mono text-ink">₹{a.estimated_cost_inr_lakh.toFixed(1)}L</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              <div className="space-y-1 border-t border-border pt-3">
                {result.assumptions.map((a, i) => (
                  <p key={i} className="text-[11px] text-ink-faint">
                    · {a}
                  </p>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
