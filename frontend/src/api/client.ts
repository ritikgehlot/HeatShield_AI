/**
 * HeatShield AI — API Client
 * Fetch wrapper with error handling for backend communication
 */

const BASE_URL = '';

export class ApiError extends Error {
  constructor(
    public status: number,
    public statusText: string,
    public body?: unknown
  ) {
    super(`API Error ${status}: ${statusText}`);
    this.name = 'ApiError';
  }
}

async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    let body: unknown;
    try {
      body = await response.json();
    } catch {
      body = await response.text();
    }
    throw new ApiError(response.status, response.statusText, body);
  }
  if (response.status === 204) {
    return undefined as T;
  }
  return response.json() as Promise<T>;
}

export async function apiGet<T>(endpoint: string, params?: Record<string, string>): Promise<T> {
  const url = new URL(`${BASE_URL}${endpoint}`, window.location.origin);
  if (params) {
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined && value !== '') {
        url.searchParams.set(key, value);
      }
    });
  }
  const response = await fetch(url.toString(), {
    method: 'GET',
    headers: { 'Accept': 'application/json' },
  });
  return handleResponse<T>(response);
}

export async function apiPost<T>(endpoint: string, body?: unknown): Promise<T> {
  const response = await fetch(`${BASE_URL}${endpoint}`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
    },
    body: body ? JSON.stringify(body) : undefined,
  });
  return handleResponse<T>(response);
}

export async function apiUpload<T>(endpoint: string, file: File, fieldName = 'file'): Promise<T> {
  const formData = new FormData();
  formData.append(fieldName, file);
  const response = await fetch(`${BASE_URL}${endpoint}`, {
    method: 'POST',
    headers: { 'Accept': 'application/json' },
    body: formData,
  });
  return handleResponse<T>(response);
}

// ============================
// API Response Types
// ============================

export interface HealthResponse {
  status: string;
  version: string;
  mode: 'demo' | 'live';
  city: string;
  timestamp: string;
}

export interface WardRisk {
  ward_id: string;
  ward_name: string;
  risk_score: number;
  risk_label: string;
  lat: number;
  lon: number;
  lst: number;
  ndvi: number;
  built_up_pct: number;
  population_density: number;
  road_density: number;
  vulnerability_index: number;
  data_source: string;
  timestamp: string;
  top_factors: RiskFactor[];
  recommendations: string[];
}

export interface RiskFactor {
  factor: string;
  contribution: number;
  description: string;
}

export interface DashboardData {
  city: string;
  mode: 'demo' | 'live';
  timestamp: string;
  summary: {
    total_wards: number;
    avg_risk_score: number;
    severe_count: number;
    extreme_count: number;
    population_at_risk: number;
    green_cover_deficit_pct: number;
  };
  risk_distribution: Record<string, number>;
  wards: WardRisk[];
  weather?: WeatherData;
}

export interface WeatherData {
  temperature: number;
  humidity: number;
  wind_speed: number;
  description: string;
  feels_like: number;
  uv_index?: number;
  source: string;
  timestamp: string;
}

export interface SimulationRequest {
  ward_id: string;
  cool_roof_pct: number;
  tree_canopy_gain_pct: number;
  shade_structures: number;
  reflective_pavement_pct: number;
  water_cooling_points: number;
  budget_lakhs: number;
}

export interface SimulationResult {
  ward_id: string;
  ward_name: string;
  original_risk_score: number;
  projected_risk_score: number;
  risk_reduction: number;
  risk_reduction_pct: number;
  original_risk_label: string;
  projected_risk_label: string;
  cost_summary: CostItem[];
  total_cost_lakhs: number;
  interventions: InterventionDetail[];
  action_brief: string;
  assumptions: string[];
}

export interface CostItem {
  item: string;
  cost_lakhs: number;
  unit: string;
}

export interface InterventionDetail {
  name: string;
  description: string;
  impact_score: number;
  priority: 'high' | 'medium' | 'low';
}

export interface DataSourceStatus {
  provider: string;
  status: 'connected' | 'disconnected' | 'error';
  last_refresh: string;
  mode: 'live' | 'demo';
  description: string;
  records_count?: number;
}

export interface UploadResponse {
  success: boolean;
  message: string;
  records_imported: number;
  errors?: string[];
}
