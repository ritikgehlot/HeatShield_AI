export type ProviderMode = "demo" | "live" | "cached_fallback" | "not_configured" | "error";
export type RiskCategory = "Low" | "Moderate" | "High" | "Severe" | "Extreme";

export interface DataBadge {
  source: string;
  mode: ProviderMode;
  observed_at: string | null;
  fetched_at: string | null;
  confidence: number | null;
  message: string;
}

export interface City {
  id: number;
  name: string;
  state: string;
  country: string;
  center_lat: number;
  center_lon: number;
  ward_count: number;
}

export interface WardSummary {
  id: number;
  name: string;
  latitude: number;
  longitude: number;
  map_x: number;
  map_y: number;
  population: number | null;
  score: number | null;
  category: RiskCategory | null;
  confidence: number | null;
  last_updated: string | null;
  geometry_geojson: string | null;
}

export interface FeatureContribution {
  key: string;
  label: string;
  value: number | null;
  normalized_risk: number | null;
  weight: number;
  contribution_pts: number;
}

export interface WardDetail {
  id: number;
  city: string;
  name: string;
  latitude: number;
  longitude: number;
  population: number | null;
  area_km2: number | null;
  features: Record<string, number | null>;
  feature_source: string;
  feature_observed_at: string | null;
  feature_confidence: number;
  score: number | null;
  category: RiskCategory | null;
  confidence: number | null;
  top_factors: FeatureContribution[];
  missing_data_warnings: string[];
  explanation: string;
  recommendations: string[];
  geometry_geojson: string | null;
  is_demo_geometry: boolean | null;
  last_updated: string | null;
}

export interface RiskExplanation {
  ward_id: number;
  ward_name: string;
  score: number | null;
  category: RiskCategory | null;
  confidence: number | null;
  all_factors: FeatureContribution[];
  missing_data_warnings: string[];
  explanation: string;
  model_version: string;
}

export interface TimeseriesPoint {
  computed_at: string;
  score: number;
  category: RiskCategory;
}

export interface Timeseries {
  ward_id: number;
  ward_name: string;
  points: TimeseriesPoint[];
}

export interface WeatherSummary {
  air_temp_c: number | null;
  apparent_temp_c: number | null;
  humidity_pct: number | null;
  wind_speed_mps: number | null;
  badge: DataBadge;
}

export interface SatelliteSummary {
  scene_id: string | null;
  lst_c: number | null;
  ndvi: number | null;
  ndbi: number | null;
  cloud_cover_pct: number | null;
  badge: DataBadge;
}

export interface DashboardKPIs {
  city_heat_risk: number | null;
  city_heat_category: RiskCategory | null;
  severe_or_extreme_wards: number;
  estimated_population_exposed: number;
  green_cover_deficit_pct: number | null;
  total_wards: number;
}

export interface Dashboard {
  city: City;
  kpis: DashboardKPIs;
  wards: WardSummary[];
  weather: WeatherSummary;
  satellite: SatelliteSummary;
  generated_at: string;
}

export interface DataSourceStatus {
  provider_key: string;
  provider_name: string;
  mode: ProviderMode;
  connected: boolean;
  last_refresh_at: string | null;
  last_error: string | null;
  message: string;
}

export interface InterventionRecommendation {
  key: string;
  name: string;
  priority_rank: number;
  risk_reduction_range: [number, number];
  cooling_impact_range_c: [number, number];
  cost_range_inr_lakh: [number, number];
  timeline_weeks: [number, number];
  population_affected_range: [number, number];
  confidence: "Low" | "Moderate" | "High";
  assumptions: string;
  why_selected: string;
}

export interface SimulationRequest {
  ward_id: number;
  budget_inr_lakh: number;
  roof_treatment_pct: number;
  tree_canopy_target_pct: number;
  shade_structures: number;
  infra_focus?: string;
}

export interface SimulationResult {
  id: number;
  ward_id: number;
  ward_name: string;
  baseline_score: number;
  baseline_category: RiskCategory;
  projected_score: number;
  projected_category: RiskCategory;
  risk_reduction_pts: number;
  risk_reduction_range_pts: [number, number];
  projected_lst_c: number;
  allocations: { key: string; label: string; estimated_cost_inr_lakh: number }[];
  assumptions: string[];
  created_at: string;
}

export interface WardReport {
  ward: WardDetail;
  recommended_interventions: InterventionRecommendation[];
  generated_at: string;
  disclaimer: string;
}
