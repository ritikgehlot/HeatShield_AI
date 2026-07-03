import { useEffect, useRef, useState } from 'react';
import maplibregl from 'maplibre-gl';
import { getRiskColor, RISK_CONFIGS } from '../utils/colors';

interface Ward {
  id: number;
  name: string;
  latitude: number;
  longitude: number;
  risk_score: number;
  risk_level: string;
  lst_c: number;
  ndvi: number;
  population_density: number;
}

interface HeatMapProps {
  wards: Ward[];
  selectedWardId: number | null;
  onSelectWard: (wardId: number) => void;
}

const MAP_STYLE: maplibregl.StyleSpecification = {
  version: 8,
  sources: {
    osm: {
      type: 'raster',
      tiles: ['https://tile.openstreetmap.org/{z}/{x}/{y}.png'],
      tileSize: 256,
      attribution: '© OpenStreetMap contributors',
    },
  },
  layers: [
    {
      id: 'osm-tiles',
      type: 'raster',
      source: 'osm',
      minzoom: 0,
      maxzoom: 19,
      paint: {
        'raster-saturation': -0.6,
        'raster-brightness-max': 0.5,
        'raster-contrast': 0.2,
      },
    },
  ],
};

const JODHPUR_CENTER: [number, number] = [73.02, 26.28];

export default function HeatMap({ wards, selectedWardId, onSelectWard }: HeatMapProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const mapRef = useRef<maplibregl.Map | null>(null);
  const [loaded, setLoaded] = useState(false);

  useEffect(() => {
    if (!containerRef.current) return;

    const map = new maplibregl.Map({
      container: containerRef.current,
      style: MAP_STYLE,
      center: JODHPUR_CENTER,
      zoom: 12,
      attributionControl: true,
    });

    map.addControl(new maplibregl.NavigationControl({ showCompass: false }), 'bottom-right');
    map.on('load', () => setLoaded(true));
    mapRef.current = map;

    return () => { map.remove(); };
  }, []);

  // Update ward markers
  useEffect(() => {
    const map = mapRef.current;
    if (!map || !loaded || !wards.length) return;

    const geojson: GeoJSON.FeatureCollection = {
      type: 'FeatureCollection',
      features: wards.map(w => ({
        type: 'Feature' as const,
        geometry: { type: 'Point' as const, coordinates: [w.longitude, w.latitude] },
        properties: {
          ward_id: w.id,
          ward_name: w.name,
          risk_score: w.risk_score,
          risk_level: w.risk_level,
          color: getRiskColor(w.risk_score),
          lst_c: w.lst_c,
          ndvi: w.ndvi,
          population_density: w.population_density,
        },
      })),
    };

    const source = map.getSource('wards') as maplibregl.GeoJSONSource | undefined;
    if (source) {
      source.setData(geojson);
      return;
    }

    map.addSource('wards', { type: 'geojson', data: geojson });

    // Glow layer
    map.addLayer({
      id: 'ward-glow',
      type: 'circle',
      source: 'wards',
      paint: {
        'circle-radius': 22,
        'circle-color': ['get', 'color'],
        'circle-opacity': 0.15,
        'circle-blur': 1,
      },
    });

    // Main circle
    map.addLayer({
      id: 'ward-circles',
      type: 'circle',
      source: 'wards',
      paint: {
        'circle-radius': [
          'interpolate', ['linear'], ['get', 'risk_score'],
          0, 8, 50, 12, 100, 18,
        ],
        'circle-color': ['get', 'color'],
        'circle-opacity': 0.85,
        'circle-stroke-color': '#ffffff',
        'circle-stroke-width': 1.5,
        'circle-stroke-opacity': 0.4,
      },
    });

    // Labels
    map.addLayer({
      id: 'ward-labels',
      type: 'symbol',
      source: 'wards',
      layout: {
        'text-field': ['get', 'ward_name'],
        'text-size': 10,
        'text-offset': [0, 2],
        'text-anchor': 'top',
        'text-max-width': 8,
      },
      paint: {
        'text-color': '#94a3b8',
        'text-halo-color': '#0a0f1c',
        'text-halo-width': 1.5,
      },
    });

    // Click handler
    map.on('click', 'ward-circles', (e) => {
      const props = e.features?.[0]?.properties;
      if (props?.ward_id) onSelectWard(Number(props.ward_id));
    });

    // Cursor
    map.on('mouseenter', 'ward-circles', () => { map.getCanvas().style.cursor = 'pointer'; });
    map.on('mouseleave', 'ward-circles', () => { map.getCanvas().style.cursor = ''; });

    // Popup
    const popup = new maplibregl.Popup({ closeButton: false, closeOnClick: false, offset: 15 });

    map.on('mouseenter', 'ward-circles', (e) => {
      const f = e.features?.[0];
      if (!f) return;
      const p = f.properties!;
      const coords = (f.geometry as GeoJSON.Point).coordinates.slice() as [number, number];
      popup
        .setLngLat(coords)
        .setHTML(`
          <div style="font-family:Inter,sans-serif">
            <div style="font-weight:700;font-size:13px;color:#f1f5f9;margin-bottom:4px">${p.ward_name}</div>
            <div style="display:flex;align-items:center;gap:6px;margin-bottom:3px">
              <span style="width:8px;height:8px;border-radius:50%;background:${p.color};display:inline-block"></span>
              <span style="font-size:11px;color:#94a3b8">Risk: <strong style="color:${p.color}">${Number(p.risk_score).toFixed(0)}</strong>/100</span>
            </div>
            <div style="font-size:10px;color:#94a3b8">LST: ${Number(p.lst_c).toFixed(1)}°C · NDVI: ${Number(p.ndvi).toFixed(2)}</div>
            <div style="font-size:10px;color:#64748b;margin-top:3px">Click for details</div>
          </div>
        `)
        .addTo(map);
    });
    map.on('mouseleave', 'ward-circles', () => popup.remove());
  }, [wards, loaded, onSelectWard]);

  // Highlight selected
  useEffect(() => {
    const map = mapRef.current;
    if (!map || !loaded || !map.getLayer('ward-circles')) return;
    map.setPaintProperty('ward-circles', 'circle-stroke-width', [
      'case', ['==', ['get', 'ward_id'], selectedWardId ?? -1], 3.5, 1.5,
    ]);
    map.setPaintProperty('ward-circles', 'circle-stroke-opacity', [
      'case', ['==', ['get', 'ward_id'], selectedWardId ?? -1], 1, 0.4,
    ]);
  }, [selectedWardId, loaded]);

  return (
    <div className="relative">
      <div ref={containerRef} className="w-full" style={{ height: 520 }} />

      {/* Legend */}
      <div className="absolute bottom-4 left-4 glass-card-static p-3 z-10">
        <p className="text-[10px] font-bold text-slate-500 uppercase tracking-wider mb-2">Heat Risk</p>
        <div className="flex flex-col gap-1">
          {(['low', 'moderate', 'high', 'severe', 'extreme'] as const).map(level => (
            <div key={level} className="flex items-center gap-2">
              <span className="w-2.5 h-2.5 rounded-full" style={{ background: RISK_CONFIGS[level].mapColor }} />
              <span className="text-[10px] text-slate-400">{RISK_CONFIGS[level].label}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Loading */}
      {!loaded && (
        <div className="absolute inset-0 flex items-center justify-center bg-[#0a0f1c]/80 z-20">
          <div className="flex flex-col items-center gap-3">
            <div className="w-8 h-8 border-2 border-orange-500 border-t-transparent rounded-full animate-spin" />
            <span className="text-xs text-slate-400">Loading map…</span>
          </div>
        </div>
      )}
    </div>
  );
}
