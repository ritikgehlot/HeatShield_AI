import { useRef, useState } from "react";
import { CloudSun, Database, Download, FileUp, MapPin, RefreshCw, Satellite, Upload } from "lucide-react";
import { useSelectedCity } from "@/lib/CityContext";
import { useDataSourcesStatus, useRefreshSatellite, useRefreshWeather, useUploadWardBoundaries, useUploadWardFeaturesCsv } from "@/hooks/useApi";
import { api } from "@/lib/api";
import { Button, ErrorState, Skeleton } from "@/components/ui/Primitives";
import { PROVIDER_MODE_DOT, PROVIDER_MODE_LABEL } from "@/lib/risk";
import { formatRelativeTime } from "@/lib/format";

const PROVIDER_ICONS: Record<string, typeof CloudSun> = {
  weather: CloudSun,
  satellite: Satellite,
  urban_features: MapPin,
  geocoding: Database,
};

export function DataSourcesPage() {
  const { cityId } = useSelectedCity();
  const { data: sources, isLoading, isError, refetch } = useDataSourcesStatus();
  const refreshWeather = useRefreshWeather();
  const refreshSatellite = useRefreshSatellite();

  if (isLoading) return <Skeleton className="h-96" />;
  if (isError || !sources) return <ErrorState title="Couldn't load data sources" onRetry={() => refetch()} />;

  return (
    <div className="animate-fade-up space-y-6">
      <header>
        <p className="mono-tag mb-1">Provenance & imports</p>
        <h1 className="font-display text-2xl font-semibold text-ink">Data Sources</h1>
        <p className="mt-1 text-sm text-ink-muted">Every value on the dashboard traces back to one of these providers. Demo providers work with no API keys; live providers need credentials in your <span className="font-mono">.env</span>.</p>
      </header>

      <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
        {sources.map((source) => {
          const Icon = PROVIDER_ICONS[source.provider_key] ?? Database;
          return (
            <div key={source.provider_key} className="glass-card p-5">
              <div className="flex items-start justify-between">
                <div className="flex items-center gap-3">
                  <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-surface-hi text-ink-muted">
                    <Icon size={18} />
                  </div>
                  <div>
                    <p className="font-medium capitalize text-ink">{source.provider_key.replace("_", " ")}</p>
                    <p className="text-xs text-ink-muted">{source.provider_name}</p>
                  </div>
                </div>
                <span className="inline-flex items-center gap-1.5 rounded-full border border-border px-2.5 py-1 text-[11px] font-mono text-ink-muted">
                  <span className={`h-1.5 w-1.5 rounded-full ${PROVIDER_MODE_DOT[source.mode]}`} />
                  {PROVIDER_MODE_LABEL[source.mode]}
                </span>
              </div>

              <dl className="mt-4 space-y-1.5 text-xs">
                <div className="flex justify-between">
                  <dt className="text-ink-faint">Connected</dt>
                  <dd className={source.connected ? "text-green" : "text-ink-muted"}>{source.connected ? "Yes" : "No"}</dd>
                </div>
                <div className="flex justify-between">
                  <dt className="text-ink-faint">Last refresh</dt>
                  <dd className="text-ink-muted">{formatRelativeTime(source.last_refresh_at)}</dd>
                </div>
                {source.last_error && (
                  <div className="mt-1 rounded border border-risk-extreme/30 bg-risk-extreme/[0.06] p-2 text-risk-extreme">{source.last_error}</div>
                )}
                {source.mode === "not_configured" && (
                  <div className="mt-1 rounded border border-border bg-canvas-raised/60 p-2 text-ink-muted">Add credentials to your <span className="font-mono">.env</span> to enable live data.</div>
                )}
              </dl>

              {source.provider_key === "weather" && (
                <Button size="sm" variant="secondary" icon={RefreshCw} className="mt-4" onClick={() => refreshWeather.mutate(cityId)} disabled={refreshWeather.isPending}>
                  {refreshWeather.isPending ? "Refreshing…" : "Refresh weather"}
                </Button>
              )}
              {source.provider_key === "satellite" && (
                <Button size="sm" variant="secondary" icon={RefreshCw} className="mt-4" onClick={() => refreshSatellite.mutate(cityId)} disabled={refreshSatellite.isPending}>
                  {refreshSatellite.isPending ? "Refreshing…" : "Refresh satellite scene"}
                </Button>
              )}
            </div>
          );
        })}
      </div>

      <UploadSection />
    </div>
  );
}

function UploadSection() {
  const csvUpload = useUploadWardFeaturesCsv();
  const geojsonUpload = useUploadWardBoundaries();
  const csvInputRef = useRef<HTMLInputElement>(null);
  const geojsonInputRef = useRef<HTMLInputElement>(null);
  const [log, setLog] = useState<string[]>([]);

  function pushLog(line: string) {
    setLog((prev) => [`${new Date().toLocaleTimeString("en-IN")} — ${line}`, ...prev].slice(0, 8));
  }

  function handleCsv(file: File | undefined) {
    if (!file) return;
    csvUpload.mutate(file, {
      onSuccess: (r) => pushLog(`CSV "${file.name}": ${r.imported} imported, ${r.updated} updated, ${r.skipped} skipped.`),
      onError: (e) => pushLog(`CSV "${file.name}" rejected: ${(e as Error).message}`),
    });
  }

  function handleGeojson(file: File | undefined) {
    if (!file) return;
    geojsonUpload.mutate(file, {
      onSuccess: (r) => pushLog(`GeoJSON "${file.name}": ${r.matched} matched, ${r.unmatched} unmatched.`),
      onError: (e) => pushLog(`GeoJSON "${file.name}" rejected: ${(e as Error).message}`),
    });
  }

  return (
    <div className="glass-card p-5">
      <p className="font-display text-base font-medium text-ink">Import ward data</p>
      <p className="mt-1 text-sm text-ink-muted">Upload validated ward features (CSV, V1 or V2 format) or official ward boundaries (GeoJSON). Uploads recompute risk scores immediately.</p>

      <div className="mt-4 grid grid-cols-1 gap-4 sm:grid-cols-2">
        <div className="rounded-lg border border-dashed border-border p-4 text-center">
          <FileUp className="mx-auto mb-2 text-ink-faint" size={22} />
          <p className="text-sm font-medium text-ink">Ward features CSV</p>
          <input ref={csvInputRef} type="file" accept=".csv" className="hidden" onChange={(e) => handleCsv(e.target.files?.[0])} />
          <Button size="sm" variant="secondary" icon={Upload} className="mt-3" onClick={() => csvInputRef.current?.click()} disabled={csvUpload.isPending}>
            {csvUpload.isPending ? "Uploading…" : "Choose CSV"}
          </Button>
        </div>
        <div className="rounded-lg border border-dashed border-border p-4 text-center">
          <MapPin className="mx-auto mb-2 text-ink-faint" size={22} />
          <p className="text-sm font-medium text-ink">Ward boundaries GeoJSON</p>
          <input ref={geojsonInputRef} type="file" accept=".geojson,.json" className="hidden" onChange={(e) => handleGeojson(e.target.files?.[0])} />
          <Button size="sm" variant="secondary" icon={Upload} className="mt-3" onClick={() => geojsonInputRef.current?.click()} disabled={geojsonUpload.isPending}>
            {geojsonUpload.isPending ? "Uploading…" : "Choose GeoJSON"}
          </Button>
        </div>
      </div>

      <div className="mt-4 flex flex-wrap gap-2">
        <a href={api.templateUrl("v2")} className="inline-flex items-center gap-1.5 rounded-lg border border-border-strong px-3 py-1.5 text-sm text-ink hover:bg-surface-hi">
          <Download size={14} /> V2 CSV template
        </a>
        <a href={api.templateUrl("v1")} className="inline-flex items-center gap-1.5 rounded-lg border border-border px-3 py-1.5 text-sm text-ink-muted hover:bg-surface-hi">
          <Download size={14} /> V1 template
        </a>
      </div>

      {log.length > 0 && (
        <div className="mt-4 rounded-lg border border-border bg-canvas-raised/60 p-3">
          <p className="mono-tag mb-2">Import log</p>
          <div className="space-y-1 font-mono text-[11px] text-ink-muted">
            {log.map((line, i) => (
              <p key={i}>{line}</p>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
