import { Link } from "react-router-dom";
import { ArrowRight, Boxes, Eye, Gauge, Layers, Leaf, Satellite, Sparkles } from "lucide-react";

export function LandingPage() {
  return (
    <div className="min-h-screen bg-canvas text-ink">
      {/* Nav */}
      <header className="mx-auto flex max-w-6xl items-center justify-between px-6 py-5">
        <div className="flex items-center gap-2.5">
          <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-brand-soft text-brand">
            <Satellite size={18} />
          </div>
          <div>
            <p className="font-display text-sm font-semibold leading-tight">HeatShield AI</p>
            <p className="mono-tag leading-tight">Team ARS</p>
          </div>
        </div>
        <Link to="/dashboard" className="inline-flex items-center gap-1.5 rounded-lg bg-brand px-4 py-2 text-sm font-medium text-white shadow-glow-brand transition-colors hover:bg-brand-strong">
          Launch Dashboard <ArrowRight size={15} />
        </Link>
      </header>

      {/* Hero */}
      <section className="relative overflow-hidden">
        <div className="mx-auto grid max-w-6xl grid-cols-1 items-center gap-10 px-6 py-16 lg:grid-cols-[1.1fr_1fr] lg:py-24">
          <div className="animate-fade-up">
            <div className="mb-5 inline-flex items-center gap-2 rounded-full border border-border bg-surface/50 px-3 py-1 text-xs text-ink-muted">
              <Sparkles size={13} className="text-brand" />
              Live urban heat intelligence · Jodhpur first
            </div>
            <h1 className="font-display text-4xl font-bold leading-[1.05] tracking-tight sm:text-5xl lg:text-6xl">
              Turn urban heat data into <span className="text-risk-high">cooling action</span>.
            </h1>
            <p className="mt-5 max-w-lg text-base leading-relaxed text-ink-muted">
              Jodhpur earned its name — the Blue City — from indigo-limewashed walls that keep homes cool. HeatShield AI brings that instinct into the satellite era: ward-by-ward heat risk, explained transparently, with costed interventions municipal teams can act on.
            </p>
            <div className="mt-8 flex flex-wrap gap-3">
              <Link to="/dashboard" className="inline-flex items-center gap-2 rounded-lg bg-brand px-5 py-3 text-sm font-medium text-white shadow-glow-brand transition-colors hover:bg-brand-strong">
                Launch Dashboard <ArrowRight size={16} />
              </Link>
              <Link to="/about" className="inline-flex items-center gap-2 rounded-lg border border-border-strong px-5 py-3 text-sm font-medium text-ink transition-colors hover:bg-surface-hi">
                How it works
              </Link>
            </div>
            <p className="mt-6 text-xs text-ink-faint">
              Works in demo mode with zero API keys · Every value shows its source, freshness & confidence
            </p>
          </div>

          {/* Signature: thermal scan panel */}
          <ThermalScanHero />
        </div>
      </section>

      {/* Features */}
      <section className="mx-auto max-w-6xl px-6 py-14">
        <p className="mono-tag mb-2">What it does</p>
        <h2 className="mb-8 font-display text-2xl font-semibold">Built for real municipal decisions</h2>
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {[
            { icon: Gauge, title: "Explainable risk scores", body: "0–100 heat risk per ward with exact per-factor attribution — Low to Extreme, never a black box." },
            { icon: Layers, title: "Map-first intelligence", body: "Interactive heat-risk map on a true thermal gradient, with satellite scene metadata and observation dates." },
            { icon: Leaf, title: "Costed interventions", body: "Cool roofs, tree canopy, shade, reflective pavement — ranked by what each ward actually needs, with budget ranges." },
            { icon: Eye, title: "Radical transparency", body: "Source, timestamp, freshness and confidence on every value. Demo data is always labelled as demo." },
            { icon: Boxes, title: "What-If simulator", body: "Test budgets and intervention mixes; see baseline vs projected risk as ranges, never over-promised single numbers." },
            { icon: Satellite, title: "Live-ready architecture", body: "Weather, satellite and OSM adapters plug in with your own keys — the platform never fakes live data." },
          ].map((f) => (
            <div key={f.title} className="glass-card p-5">
              <f.icon size={20} className="mb-3 text-brand" />
              <p className="font-display text-base font-medium">{f.title}</p>
              <p className="mt-1.5 text-sm leading-relaxed text-ink-muted">{f.body}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Workflow */}
      <section className="mx-auto max-w-6xl px-6 py-14">
        <p className="mono-tag mb-2">Workflow</p>
        <h2 className="mb-8 font-display text-2xl font-semibold">From pixels to policy</h2>
        <div className="grid grid-cols-1 gap-3 md:grid-cols-4">
          {[
            ["Ingest", "Satellite scenes, weather, ward features and boundaries."],
            ["Score", "Transparent hybrid formula turns features into explained risk."],
            ["Prioritise", "Rank wards and match interventions to real drivers."],
            ["Simulate", "Test budgets and see projected impact before spending."],
          ].map(([title, body], i) => (
            <div key={title} className="rounded-xl2 border border-border bg-surface/40 p-5">
              <p className="font-display text-3xl font-bold text-brand/40">{String(i + 1).padStart(2, "0")}</p>
              <p className="mt-2 font-display text-base font-medium">{title}</p>
              <p className="mt-1 text-sm text-ink-muted">{body}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Architecture preview + transparency note */}
      <section className="mx-auto max-w-6xl px-6 py-14">
        <div className="glass-card grid grid-cols-1 gap-6 p-8 lg:grid-cols-[1fr_1fr]">
          <div>
            <p className="mono-tag mb-2">Architecture</p>
            <h2 className="mb-4 font-display text-xl font-semibold">Transparent by construction</h2>
            <div className="space-y-2 font-mono text-xs text-ink-muted">
              <p>React + TypeScript + Vite + MapLibre + TanStack Query</p>
              <p>↕ typed REST API</p>
              <p>FastAPI + Pydantic v2 + SQLAlchemy 2</p>
              <p>↕ provider adapters (demo / live)</p>
              <p>Open-Meteo · Earth Engine · Copernicus · OSM</p>
              <p>↕ persisted with provenance</p>
              <p>SQLite (demo) / PostgreSQL + PostGIS (prod)</p>
            </div>
          </div>
          <div className="rounded-xl2 border border-border bg-canvas-raised/50 p-6">
            <p className="font-display text-base font-medium text-ink">A note on honesty</p>
            <p className="mt-2 text-sm leading-relaxed text-ink-muted">
              Satellite imagery is never "live" in the second-by-second sense — we label it <em>latest available scene</em> with its true observation date. When a live provider isn't configured, you see a clear "not configured" message, never invented values. This is a decision-support tool; its outputs inform human judgment, they don't replace it.
            </p>
          </div>
        </div>
      </section>

      <footer className="mx-auto max-w-6xl border-t border-border px-6 py-8 text-center">
        <p className="text-sm text-ink-muted">HeatShield AI — Live Urban Heat Intelligence Platform</p>
        <p className="mono-tag mt-1">Team ARS · Primary demo city: Jodhpur, Rajasthan</p>
      </footer>
    </div>
  );
}

function ThermalScanHero() {
  // Signature element: a stylized ward grid under a sweeping thermal scan line —
  // evokes satellite land-surface-temperature acquisition, the core of the product.
  const cells = Array.from({ length: 36 });
  const heats = [
    0.9, 0.3, 0.7, 0.5, 0.95, 0.4, 0.2, 0.6, 0.85, 0.5, 0.3, 0.7, 0.55, 0.9, 0.35, 0.6, 0.8, 0.25,
    0.7, 0.45, 0.9, 0.3, 0.65, 0.5, 0.4, 0.85, 0.3, 0.6, 0.95, 0.5, 0.2, 0.75, 0.55, 0.4, 0.8, 0.6,
  ];
  const color = (h: number) => {
    if (h < 0.35) return "#3FC7B0";
    if (h < 0.55) return "#E8C547";
    if (h < 0.75) return "#E8934A";
    if (h < 0.9) return "#E0602F";
    return "#C81E3A";
  };
  return (
    <div className="relative animate-fade-up">
      <div className="glass-card grid-texture relative overflow-hidden p-6">
        <div className="mb-4 flex items-center justify-between">
          <p className="mono-tag">Jodhpur · land surface temperature</p>
          <span className="inline-flex items-center gap-1.5 rounded-full border border-border px-2 py-0.5 text-[10px] font-mono text-ink-faint">
            <span className="h-1.5 w-1.5 rounded-full bg-ink-faint" /> Demo scene
          </span>
        </div>
        <div className="relative grid grid-cols-6 gap-1.5">
          {cells.map((_, i) => (
            <div
              key={i}
              className="aspect-square rounded-sm transition-all"
              style={{ backgroundColor: color(heats[i]), opacity: 0.35 + heats[i] * 0.55 }}
            />
          ))}
          {/* sweeping scan line */}
          <div className="pointer-events-none absolute inset-0 overflow-hidden rounded-sm">
            <div
              className="absolute inset-x-0 h-16 bg-gradient-to-b from-transparent via-brand/25 to-transparent motion-reduce:hidden"
              style={{ animation: "scan-sweep 3.5s ease-in-out infinite" }}
            />
          </div>
        </div>
        <div className="mt-4 flex items-center justify-between text-[10px] text-ink-faint">
          <span>Cooler wards</span>
          <div className="h-1.5 w-28 rounded-full bg-thermal-gradient" />
          <span>Hotter wards</span>
        </div>
      </div>
    </div>
  );
}
