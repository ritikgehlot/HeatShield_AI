import { useEffect, useRef, useState } from "react";
import maplibregl, { type Map as MapLibreMap } from "maplibre-gl";
import type { WardSummary } from "@/types/api";
import { thermalColorForScore } from "@/lib/risk";

const KEYLESS_DARK_STYLE = "https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json";
const MAP_KEY = import.meta.env.VITE_MAP_PROVIDER_KEY as string | undefined;
const STYLE_URL = MAP_KEY ? `https://api.maptiler.com/maps/darkmatter/style.json?key=${MAP_KEY}` : KEYLESS_DARK_STYLE;

interface HeatMapProps {
  wards: WardSummary[];
  centerLat: number;
  centerLon: number;
  selectedWardId?: number;
  onSelectWard?: (wardId: number) => void;
}

function wardsToFeatureCollection(wards: WardSummary[]) {
  const features = wards
    .map((ward) => {
      if (ward.geometry_geojson) {
        try {
          const geometry = JSON.parse(ward.geometry_geojson);
          return { type: "Feature" as const, geometry, properties: { id: ward.id, name: ward.name, score: ward.score ?? 0, category: ward.category ?? "Unknown", hasScore: ward.score !== null } };
        } catch {
          // fall through to point fallback below
        }
      }
      return {
        type: "Feature" as const,
        geometry: { type: "Point" as const, coordinates: [ward.longitude, ward.latitude] },
        properties: { id: ward.id, name: ward.name, score: ward.score ?? 0, category: ward.category ?? "Unknown", hasScore: ward.score !== null },
      };
    })
    .filter(Boolean);
  return { type: "FeatureCollection" as const, features };
}

export function HeatMap({ wards, centerLat, centerLon, selectedWardId, onSelectWard }: HeatMapProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const mapRef = useRef<MapLibreMap | null>(null);
  const [loaded, setLoaded] = useState(false);
  const [styleError, setStyleError] = useState(false);

  useEffect(() => {
    if (!containerRef.current || mapRef.current) return;
    const map = new maplibregl.Map({
      container: containerRef.current,
      style: STYLE_URL,
      center: [centerLon, centerLat],
      zoom: 11.2,
      attributionControl: { compact: true },
    });
    map.addControl(new maplibregl.NavigationControl({ showCompass: false }), "top-right");
    map.on("error", (e) => {
      // Basemap tiles unreachable (offline, blocked network, etc.) — degrade
      // gracefully rather than leaving a blank/broken map with no explanation.
      if (String(e?.error?.message || "").toLowerCase().includes("style")) setStyleError(true);
    });
    map.on("load", () => setLoaded(true));
    mapRef.current = map;
    return () => {
      map.remove();
      mapRef.current = null;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    const map = mapRef.current;
    if (!map || !loaded) return;
    const data = wardsToFeatureCollection(wards);

    const applyLayers = () => {
      const colorExpression: maplibregl.ExpressionSpecification = [
        "interpolate",
        ["linear"],
        ["get", "score"],
        0, "#3FC7B0",
        35, "#E8C547",
        60, "#E8934A",
        80, "#E0602F",
        100, "#C81E3A",
      ];

      if (!map.getSource("wards")) {
        map.addSource("wards", { type: "geojson", data });
        map.addLayer({ id: "ward-fill", type: "fill", source: "wards", filter: ["==", ["geometry-type"], "Polygon"], paint: { "fill-color": colorExpression, "fill-opacity": 0.55 } });
        map.addLayer({ id: "ward-outline", type: "line", source: "wards", filter: ["==", ["geometry-type"], "Polygon"], paint: { "line-color": "#0A1128", "line-width": 1.2 } });
        map.addLayer({ id: "ward-selected", type: "line", source: "wards", filter: ["==", ["get", "id"], selectedWardId ?? -1], paint: { "line-color": "#EDF1FA", "line-width": 2.5 } });
        map.addLayer({ id: "ward-points", type: "circle", source: "wards", filter: ["==", ["geometry-type"], "Point"], paint: { "circle-radius": 7, "circle-color": colorExpression, "circle-stroke-width": 1.5, "circle-stroke-color": "#0A1128" } });

        const clickHandler = (e: maplibregl.MapLayerMouseEvent) => {
          const id = e.features?.[0]?.properties?.id;
          if (id !== undefined && onSelectWard) onSelectWard(Number(id));
        };
        map.on("click", "ward-fill", clickHandler);
        map.on("click", "ward-points", clickHandler);
        for (const layer of ["ward-fill", "ward-points"]) {
          map.on("mouseenter", layer, () => (map.getCanvas().style.cursor = "pointer"));
          map.on("mouseleave", layer, () => (map.getCanvas().style.cursor = ""));
        }

        const popup = new maplibregl.Popup({ closeButton: false, closeOnClick: false, className: "heatshield-popup" });
        for (const layer of ["ward-fill", "ward-points"]) {
          map.on("mousemove", layer, (e) => {
            const f = e.features?.[0];
            if (!f) return;
            const name = f.properties?.name;
            const score = f.properties?.hasScore ? Number(f.properties?.score).toFixed(0) : "—";
            const category = f.properties?.category;
            popup
              .setLngLat(e.lngLat)
              .setHTML(`<div style="font-family: 'IBM Plex Sans', sans-serif; font-size: 12px;"><strong>${name}</strong><br/>Score ${score} · ${category}</div>`)
              .addTo(map);
          });
          map.on("mouseleave", layer, () => popup.remove());
        }
      } else {
        (map.getSource("wards") as maplibregl.GeoJSONSource).setData(data as GeoJSON.FeatureCollection);
        map.setFilter("ward-selected", ["==", ["get", "id"], selectedWardId ?? -1]);
      }
    };

    if (map.isStyleLoaded()) applyLayers();
    else map.once("styledata", applyLayers);
  }, [wards, loaded, selectedWardId, onSelectWard]);

  return (
    <div className="relative h-full w-full overflow-hidden rounded-xl2 border border-border">
      <div ref={containerRef} className="h-full w-full" />
      {styleError && (
        <div className="absolute inset-x-3 top-3 rounded-lg border border-risk-moderate/40 bg-canvas-raised/95 px-3 py-2 text-xs text-ink-muted backdrop-blur">
          Basemap tiles could not be loaded (offline or blocked network). Ward shapes and colors below are still accurate.
        </div>
      )}
      <MapLegend />
    </div>
  );
}

function MapLegend() {
  return (
    <div className="absolute bottom-3 left-3 rounded-lg border border-border bg-canvas-raised/90 px-3 py-2.5 backdrop-blur-md">
      <p className="mono-tag mb-1.5">Heat risk score</p>
      <div className="h-2 w-40 rounded-full bg-thermal-gradient" />
      <div className="mt-1 flex justify-between text-[10px] text-ink-faint">
        <span>0 Low</span>
        <span>100 Extreme</span>
      </div>
    </div>
  );
}
