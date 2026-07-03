import { X, Play, Thermometer, TreePine, Building2, Users, Route, ShieldAlert, Info } from 'lucide-react';
import RiskBadge from './RiskBadge';
import { getRiskConfig } from '../utils/colors';
import { useNavigate } from 'react-router-dom';

interface Ward {
  id: number;
  name: string;
  city: string;
  latitude: number;
  longitude: number;
  lst_c: number;
  ndvi: number;
  ndbi: number;
  built_up_pct: number;
  road_density_km_km2: number;
  population_density: number;
  vulnerability_index: number;
  risk_score: number;
  risk_level: string;
  top_drivers: string[];
  recommendation: string[];
  data_source: string;
  last_updated: string;
}

interface Props {
  ward: Ward;
  onClose: () => void;
}

function FeatureItem({ icon, label, value, tooltip }: { icon: React.ReactNode; label: string; value: string; tooltip?: string }) {
  return (
    <div className="flex items-center gap-3 p-3 rounded-xl bg-[rgba(148,163,184,0.04)] border border-[rgba(148,163,184,0.08)]">
      <div className="text-slate-600">{icon}</div>
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-1">
          <span className="text-[10px] text-slate-600 uppercase tracking-wider">{label}</span>
          {tooltip && <span className="tooltip-trigger text-[10px] text-slate-700" title={tooltip}><Info className="w-3 h-3 inline" /></span>}
        </div>
        <span className="text-sm font-semibold text-white">{value}</span>
      </div>
    </div>
  );
}

export default function WardDetailPanel({ ward, onClose }: Props) {
  const navigate = useNavigate();
  const riskConfig = getRiskConfig(ward.risk_score);

  return (
    <div className="glass-card-static overflow-hidden animate-slide-in-right">
      {/* Header */}
      <div className="bg-[#0d1321] border-b border-[rgba(148,163,184,0.08)] p-5">
        <div className="flex items-start justify-between">
          <div>
            <h2 className="text-lg font-bold text-white">{ward.name}</h2>
            <div className="flex items-center gap-2 mt-1.5">
              <RiskBadge level={ward.risk_level} score={ward.risk_score} />
            </div>
          </div>
          <button onClick={onClose} className="p-1.5 rounded-lg hover:bg-[rgba(148,163,184,0.1)] text-slate-600 hover:text-white transition-colors" aria-label="Close">
            <X className="w-5 h-5" />
          </button>
        </div>
      </div>

      <div className="p-5 space-y-6 overflow-y-auto" style={{ maxHeight: 'calc(100vh - 200px)' }}>
        {/* Circular gauge */}
        <div className="flex items-center justify-center">
          <div className="relative w-32 h-32">
            <svg viewBox="0 0 120 120" className="w-full h-full -rotate-90">
              <circle cx="60" cy="60" r="52" fill="none" stroke="#1a2332" strokeWidth="8" />
              <circle cx="60" cy="60" r="52" fill="none" stroke={riskConfig.color} strokeWidth="8" strokeLinecap="round"
                strokeDasharray={`${(ward.risk_score / 100) * 327} 327`} className="transition-all duration-1000" />
            </svg>
            <div className="absolute inset-0 flex flex-col items-center justify-center">
              <span className="text-3xl font-black" style={{ color: riskConfig.color }}>{ward.risk_score.toFixed(0)}</span>
              <span className="text-[10px] text-slate-600 uppercase tracking-wider">Risk Score</span>
            </div>
          </div>
        </div>

        {/* Data source */}
        <div className="text-center text-xs text-slate-600">
          {ward.data_source} • {new Date(ward.last_updated).toLocaleString('en-IN', { day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit' })}
        </div>

        {/* Top drivers */}
        {ward.top_drivers && ward.top_drivers.length > 0 && (
          <div>
            <h3 className="text-xs font-bold text-slate-500 uppercase tracking-wider mb-3">Top Risk Factors</h3>
            <ul className="space-y-2">
              {ward.top_drivers.map((driver, i) => (
                <li key={i} className="flex gap-2 text-xs text-slate-400">
                  <span className="text-orange-400 mt-0.5">▸</span>
                  <span>{driver}</span>
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* Feature grid */}
        <div>
          <h3 className="text-xs font-bold text-slate-500 uppercase tracking-wider mb-3">Ward Features</h3>
          <div className="grid grid-cols-2 gap-2">
            <FeatureItem icon={<Thermometer className="w-4 h-4" />} label="LST" value={`${ward.lst_c.toFixed(1)}°C`} tooltip="Land Surface Temperature" />
            <FeatureItem icon={<TreePine className="w-4 h-4" />} label="NDVI" value={ward.ndvi.toFixed(3)} tooltip="Vegetation Index (0-1)" />
            <FeatureItem icon={<Building2 className="w-4 h-4" />} label="Built-up" value={`${ward.built_up_pct.toFixed(0)}%`} tooltip="Built-up area percentage" />
            <FeatureItem icon={<ShieldAlert className="w-4 h-4" />} label="Vulnerability" value={ward.vulnerability_index.toFixed(2)} tooltip="Socio-economic vulnerability" />
            <FeatureItem icon={<Route className="w-4 h-4" />} label="Road Density" value={`${ward.road_density_km_km2.toFixed(1)} km/km²`} />
            <FeatureItem icon={<Users className="w-4 h-4" />} label="Pop. Density" value={`${ward.population_density.toLocaleString()}/km²`} />
          </div>
        </div>

        {/* Recommendations */}
        {ward.recommendation && ward.recommendation.length > 0 && (
          <div>
            <h3 className="text-xs font-bold text-slate-500 uppercase tracking-wider mb-3">Recommendations</h3>
            <ul className="space-y-2">
              {ward.recommendation.map((rec, i) => (
                <li key={i} className="flex gap-2 text-xs text-slate-400">
                  <span className="text-emerald-400 mt-0.5">▸</span>
                  <span>{rec}</span>
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* Action */}
        <button
          onClick={() => navigate(`/simulator?ward=${ward.id}`)}
          className="w-full flex items-center justify-center gap-2 px-4 py-2.5 rounded-xl bg-orange-500/10 border border-orange-500/30 text-orange-400 hover:bg-orange-500/20 transition-all text-sm font-bold"
        >
          <Play className="w-4 h-4" /> Run Simulation
        </button>
      </div>
    </div>
  );
}
