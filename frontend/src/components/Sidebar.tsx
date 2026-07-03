import { NavLink } from 'react-router-dom';
import { LayoutDashboard, FlaskConical, Database, Info, Flame, ChevronLeft, Menu } from 'lucide-react';
import { useState } from 'react';

const navItems = [
  { to: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { to: '/simulator', label: 'Scenario Lab', icon: FlaskConical },
  { to: '/data-sources', label: 'Data Sources', icon: Database },
  { to: '/about', label: 'Model Card', icon: Info },
];

export default function Sidebar() {
  const [collapsed, setCollapsed] = useState(false);

  return (
    <aside className={`fixed inset-y-0 left-0 z-30 flex flex-col transition-all duration-300 ${collapsed ? 'w-[68px]' : 'w-[240px]'} bg-[#0d1321] border-r border-[rgba(148,163,184,0.1)]`}>
      {/* Brand */}
      <div className="flex items-center gap-3 px-4 py-5 border-b border-[rgba(148,163,184,0.08)]">
        <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-orange-500 to-amber-500 flex items-center justify-center flex-shrink-0">
          <Flame className="w-5 h-5 text-white" />
        </div>
        {!collapsed && (
          <div className="overflow-hidden">
            <div className="font-extrabold text-white text-sm leading-tight tracking-tight">HeatShield</div>
            <div className="text-[10px] text-slate-500 leading-tight">AI Decision Platform</div>
          </div>
        )}
      </div>

      {/* Navigation */}
      <nav className="flex-1 py-4 px-2 space-y-1">
        {navItems.map(({ to, label, icon: Icon }) => (
          <NavLink
            key={to}
            to={to}
            className={({ isActive }) =>
              `flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-semibold transition-all duration-200 group ${
                isActive
                  ? 'bg-[#1a2332] text-white shadow-lg shadow-orange-500/5'
                  : 'text-slate-400 hover:text-white hover:bg-[#151f2e]'
              }`
            }
          >
            <Icon className="w-[18px] h-[18px] flex-shrink-0" />
            {!collapsed && <span>{label}</span>}
          </NavLink>
        ))}
      </nav>

      {/* Team card */}
      {!collapsed && (
        <div className="mx-3 mb-3 p-3 rounded-xl bg-[#111c2d] border border-[rgba(148,163,184,0.08)]">
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 rounded-full bg-emerald-400 shadow-[0_0_6px_rgba(52,211,153,0.5)]" />
            <span className="text-xs font-bold text-white">TEAM-ARS</span>
          </div>
          <p className="text-[10px] text-slate-500 mt-1">AI for a Cooler Tomorrow</p>
        </div>
      )}

      {/* Collapse toggle */}
      <button
        onClick={() => setCollapsed(!collapsed)}
        className="mx-3 mb-3 p-2 rounded-lg text-slate-500 hover:text-white hover:bg-[#1a2332] transition-colors"
        aria-label={collapsed ? 'Expand sidebar' : 'Collapse sidebar'}
      >
        {collapsed ? <Menu className="w-4 h-4" /> : <ChevronLeft className="w-4 h-4" />}
      </button>
    </aside>
  );
}
