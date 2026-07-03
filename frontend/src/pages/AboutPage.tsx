import { AlertTriangle, GitBranch, Scale, ShieldCheck } from "lucide-react";

const FLOW_STEPS = [
  { label: "Ingest", detail: "Weather (Open-Meteo/OWM), satellite scenes (GEE/Copernicus), ward features (CSV), boundaries (GeoJSON), OSM urban features." },
  { label: "Snapshot", detail: "Each import writes a timestamped ward feature snapshot — no value is overwritten, so freshness and history are always recoverable." },
  { label: "Score", detail: "A transparent weighted formula converts the 9 features into a 0–100 heat-risk score with exact per-feature attribution." },
  { label: "Explain", detail: "Top drivers, confidence, and missing-data warnings are produced alongside every score — never a bare number." },
  { label: "Recommend", detail: "Interventions are ranked by how directly they address that ward's actual top risk drivers, with cost/impact ranges." },
];

const WEIGHTS = [
  ["Land surface temperature", "22%"],
  ["Low green cover (NDVI)", "15%"],
  ["Population vulnerability", "15%"],
  ["Built-up index (NDBI)", "10%"],
  ["Built-up area share", "10%"],
  ["Air temperature", "8%"],
  ["Road density", "8%"],
  ["Population density", "7%"],
  ["Apparent temperature", "5%"],
];

export function AboutPage() {
  return (
    <div className="animate-fade-up space-y-8">
      <header>
        <p className="mono-tag mb-1">Model card & method</p>
        <h1 className="font-display text-2xl font-semibold text-ink">How HeatShield AI works</h1>
        <p className="mt-2 max-w-2xl text-sm leading-relaxed text-ink-muted">
          This platform is decision support, not an automated decision-maker. Every output is a transparent estimate meant to help municipal teams prioritise — not a validated physical measurement or a final policy verdict.
        </p>
      </header>

      {/* Data flow */}
      <section className="glass-card p-6">
        <div className="mb-4 flex items-center gap-2">
          <GitBranch size={18} className="text-brand" />
          <h2 className="font-display text-lg font-medium text-ink">Data flow</h2>
        </div>
        <div className="grid grid-cols-1 gap-3 md:grid-cols-5">
          {FLOW_STEPS.map((step, i) => (
            <div key={step.label} className="rounded-lg border border-border bg-canvas-raised/50 p-3">
              <p className="mono-tag mb-1">
                {String(i + 1).padStart(2, "0")} · {step.label}
              </p>
              <p className="text-xs leading-relaxed text-ink-muted">{step.detail}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Scoring model */}
      <section className="grid grid-cols-1 gap-5 lg:grid-cols-2">
        <div className="glass-card p-6">
          <div className="mb-4 flex items-center gap-2">
            <Scale size={18} className="text-brand" />
            <h2 className="font-display text-lg font-medium text-ink">The scoring model</h2>
          </div>
          <p className="mb-4 text-sm leading-relaxed text-ink-muted">
            A weighted, min-max-normalized hybrid formula — not a black-box ML model trained on synthetic data. Because the score is a weighted sum, each feature's contribution is exact, so the explanation you see <em>is</em> the math, not a post-hoc approximation. Missing features are excluded and their weight redistributed, never treated as zero-risk.
          </p>
          <div className="space-y-1.5">
            {WEIGHTS.map(([label, weight]) => (
              <div key={label} className="flex items-center justify-between text-sm">
                <span className="text-ink-muted">{label}</span>
                <span className="font-mono text-brand">{weight}</span>
              </div>
            ))}
          </div>
        </div>

        <div className="space-y-5">
          <div className="glass-card p-6">
            <div className="mb-3 flex items-center gap-2">
              <AlertTriangle size={18} className="text-risk-severe" />
              <h2 className="font-display text-lg font-medium text-ink">Limitations</h2>
            </div>
            <ul className="space-y-2 text-sm text-ink-muted">
              <li>· Demo data is seeded and clearly labelled — it is not measured observation.</li>
              <li>· Seeded ward boundaries are simplified placeholders, not official municipal boundaries.</li>
              <li>· Feature weights are informed judgment, not calibrated against local heat-morbidity outcomes.</li>
              <li>· Simulator outputs are planning comparisons, not physical (CFD) simulations.</li>
            </ul>
          </div>

          <div className="glass-card p-6">
            <div className="mb-3 flex items-center gap-2">
              <ShieldCheck size={18} className="text-green" />
              <h2 className="font-display text-lg font-medium text-ink">Ethical commitments</h2>
            </div>
            <ul className="space-y-2 text-sm text-ink-muted">
              <li>· Never presents demo, cached, or simulated data as live.</li>
              <li>· Shows source, timestamp, freshness, and confidence on every important value.</li>
              <li>· Outputs are decision support for humans, never automated policy.</li>
            </ul>
          </div>
        </div>
      </section>

      <p className="text-center text-xs text-ink-faint">
        HeatShield AI · Team ARS · Full model card and assumptions in <span className="font-mono">docs/MODEL_CARD.md</span>
      </p>
    </div>
  );
}
