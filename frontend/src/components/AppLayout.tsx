import { NavLink, Outlet } from "react-router-dom";
import { LayoutDashboard, Database, SlidersHorizontal, Info, Satellite, Menu, X } from "lucide-react";
import { useState } from "react";
import { CityProvider, useSelectedCity } from "@/lib/CityContext";
import { useCities } from "@/hooks/useApi";

const NAV_ITEMS = [
  { to: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { to: "/simulator", label: "What-If Simulator", icon: SlidersHorizontal },
  { to: "/data-sources", label: "Data Sources", icon: Database },
  { to: "/about", label: "Model & Method", icon: Info },
];

function CitySelector() {
  const { data: cities } = useCities();
  const { cityId, setCityId } = useSelectedCity();
  if (!cities || cities.length === 0) return null;
  return (
    <select
      value={cityId ?? ""}
      onChange={(e) => setCityId(Number(e.target.value))}
      className="w-full rounded-lg border border-border-strong bg-canvas-raised px-3 py-2 text-sm text-ink outline-none focus-visible:border-brand"
      aria-label="Select city"
    >
      {cities.map((c) => (
        <option key={c.id} value={c.id}>
          {c.name}, {c.state}
        </option>
      ))}
    </select>
  );
}

function SidebarContent({ onNavigate }: { onNavigate?: () => void }) {
  return (
    <>
      <div className="flex items-center gap-2.5 px-1 pb-6">
        <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-brand-soft text-brand">
          <Satellite size={18} />
        </div>
        <div>
          <p className="font-display text-sm font-semibold leading-tight text-ink">HeatShield AI</p>
          <p className="mono-tag leading-tight">Team ARS</p>
        </div>
      </div>

      <div className="mb-6">
        <p className="mono-tag mb-2 px-1">City</p>
        <CitySelector />
      </div>

      <nav className="flex flex-col gap-1">
        {NAV_ITEMS.map(({ to, label, icon: Icon }) => (
          <NavLink
            key={to}
            to={to}
            onClick={onNavigate}
            className={({ isActive }) =>
              `flex items-center gap-2.5 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors ${
                isActive ? "bg-brand-soft text-brand" : "text-ink-muted hover:bg-surface-hi hover:text-ink"
              }`
            }
          >
            <Icon size={17} />
            {label}
          </NavLink>
        ))}
      </nav>

      <div className="mt-auto pt-6">
        <NavLink to="/" className="mono-tag flex items-center gap-1.5 px-1 hover:text-ink-muted">
          ← Back to overview
        </NavLink>
      </div>
    </>
  );
}

export function AppLayout() {
  const [mobileOpen, setMobileOpen] = useState(false);

  return (
    <CityProvider>
      <div className="min-h-screen bg-canvas">
        {/* Desktop sidebar */}
        <aside className="fixed inset-y-0 left-0 z-30 hidden w-64 flex-col border-r border-border bg-canvas-raised/60 p-5 backdrop-blur-xl lg:flex">
          <SidebarContent />
        </aside>

        {/* Mobile topbar + drawer */}
        <div className="sticky top-0 z-40 flex items-center justify-between border-b border-border bg-canvas-raised/90 px-4 py-3 backdrop-blur-xl lg:hidden">
          <p className="font-display text-sm font-semibold text-ink">HeatShield AI</p>
          <button onClick={() => setMobileOpen(true)} aria-label="Open menu" className="text-ink-muted">
            <Menu size={22} />
          </button>
        </div>
        {mobileOpen && (
          <div className="fixed inset-0 z-50 flex lg:hidden">
            <div className="absolute inset-0 bg-black/60" onClick={() => setMobileOpen(false)} />
            <div className="relative flex w-72 flex-col bg-canvas-raised p-5">
              <button onClick={() => setMobileOpen(false)} aria-label="Close menu" className="mb-4 self-end text-ink-muted">
                <X size={20} />
              </button>
              <SidebarContent onNavigate={() => setMobileOpen(false)} />
            </div>
          </div>
        )}

        <main className="lg:pl-64">
          <div className="mx-auto max-w-[1400px] px-4 py-6 sm:px-6 lg:px-8 lg:py-8">
            <Outlet />
          </div>
        </main>
      </div>
    </CityProvider>
  );
}
