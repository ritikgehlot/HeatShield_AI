const BASE_URL = "/api";

export class ApiError extends Error {
  status: number;
  constructor(message: string, status: number) {
    super(message);
    this.status = status;
  }
}

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${BASE_URL}${path}`, {
    ...options,
    headers: { "Content-Type": "application/json", ...options?.headers },
  });
  if (!response.ok) {
    let detail = response.statusText;
    try {
      const body = await response.json();
      detail = body.detail || detail;
    } catch {
      // response wasn't JSON — keep statusText
    }
    throw new ApiError(detail, response.status);
  }
  return response.json() as Promise<T>;
}

export const api = {
  health: () => request<{ status: string; service: string }>("/health"),
  cities: () => request<import("../types/api").City[]>("/cities"),
  dashboard: (cityId: number) => request<import("../types/api").Dashboard>(`/cities/${cityId}/dashboard`),
  wardDetail: (wardId: number) => request<import("../types/api").WardDetail>(`/wards/${wardId}`),
  wardTimeseries: (wardId: number) => request<import("../types/api").Timeseries>(`/wards/${wardId}/timeseries`),
  riskExplanation: (wardId: number) => request<import("../types/api").RiskExplanation>(`/wards/${wardId}/risk-explanation`),
  wardReport: (wardId: number) => request<import("../types/api").WardReport>(`/reports/ward/${wardId}`),
  dataSourcesStatus: () => request<import("../types/api").DataSourceStatus[]>("/data-sources/status"),
  refreshWeather: (cityId?: number) => request<{ mode: string; message: string }>(`/refresh/weather${cityId ? `?city_id=${cityId}` : ""}`, { method: "POST" }),
  refreshSatellite: (cityId?: number) => request<{ mode: string; message: string }>(`/refresh/satellite${cityId ? `?city_id=${cityId}` : ""}`, { method: "POST" }),
  createSimulation: (payload: import("../types/api").SimulationRequest) =>
    request<import("../types/api").SimulationResult>("/simulations", { method: "POST", body: JSON.stringify(payload) }),

  async uploadWardFeaturesCsv(file: File) {
    const form = new FormData();
    form.append("file", file);
    const response = await fetch(`${BASE_URL}/upload/ward-features-csv`, { method: "POST", body: form });
    if (!response.ok) {
      const body = await response.json().catch(() => ({ detail: response.statusText }));
      throw new ApiError(body.detail, response.status);
    }
    return response.json() as Promise<{ imported: number; updated: number; skipped: number; message: string }>;
  },

  async uploadWardBoundariesGeoJson(file: File) {
    const form = new FormData();
    form.append("file", file);
    const response = await fetch(`${BASE_URL}/upload/ward-boundaries-geojson`, { method: "POST", body: form });
    if (!response.ok) {
      const body = await response.json().catch(() => ({ detail: response.statusText }));
      throw new ApiError(body.detail, response.status);
    }
    return response.json() as Promise<{ matched: number; unmatched: number; message: string }>;
  },

  templateUrl: (version: "v1" | "v2" = "v2") => `${BASE_URL}/data/template?version=${version}`,
};
