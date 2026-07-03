"""Pydantic v2 response/request models.

Ward-related schemas are built from Ward + latest WardFeatureSnapshot + latest
HeatRiskScore joined together (see services.py) since that's how the data is
now stored — the flat WardOut/SummaryOut/ScenarioOut shapes are kept for the
legacy endpoints so nothing that used to work stops working.
"""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


# --- Legacy (V1) shapes, kept for backward compatibility -------------------
class WardOut(BaseModel):
    id: int
    city: str
    name: str
    latitude: float
    longitude: float
    map_x: float
    map_y: float
    lst_c: Optional[float] = None
    ndvi: Optional[float] = None
    ndbi: Optional[float] = None
    built_up_pct: Optional[float] = None
    road_density_km_km2: Optional[float] = None
    population_density: Optional[float] = None
    vulnerability_index: Optional[float] = None
    risk_score: float
    risk_level: str
    top_drivers: list[str]
    recommendation: list[str]
    data_source: str
    last_updated: datetime


class SummaryOut(BaseModel):
    city: str
    total_wards: int
    high_risk_wards: int
    average_risk_score: float
    average_lst_c: float
    green_cover_average: float
    data_note: str


class ScenarioRequest(BaseModel):
    ward_id: int
    cool_roof_coverage: float = Field(default=25, ge=0, le=100)
    tree_cover_gain: float = Field(default=5, ge=0, le=25)
    shade_units: int = Field(default=5, ge=0, le=100)
    budget_lakh: float = Field(default=10, ge=0, le=1000)


class ScenarioOut(BaseModel):
    ward_id: int
    ward_name: str
    baseline_score: float
    projected_score: float
    risk_reduction: float
    baseline_lst_c: float
    projected_lst_c: float
    risk_level: str
    intervention_summary: list[str]
    action_brief: str
    model_note: str


class UploadResult(BaseModel):
    imported: int
    updated: int
    skipped: int
    message: str


# --- V2 shapes ---------------------------------------------------------------
class DataBadge(BaseModel):
    """Attached to every value that carries source/freshness/confidence info —
    the "never show fake live data" contract, made into a reusable shape."""
    source: str
    mode: str  # demo | live | cached_fallback | not_configured | error
    observed_at: Optional[datetime] = None
    fetched_at: Optional[datetime] = None
    confidence: Optional[float] = None
    message: str = ""


class CityOut(BaseModel):
    id: int
    name: str
    state: str
    country: str
    center_lat: float
    center_lon: float
    ward_count: int


class WardSummaryOut(BaseModel):
    id: int
    name: str
    latitude: float
    longitude: float
    map_x: float
    map_y: float
    population: Optional[int] = None
    score: Optional[float] = None
    category: Optional[str] = None
    confidence: Optional[float] = None
    last_updated: Optional[datetime] = None
    geometry_geojson: Optional[str] = None


class FeatureContributionOut(BaseModel):
    key: str
    label: str
    value: Optional[float] = None
    normalized_risk: Optional[float] = None
    weight: float
    contribution_pts: float


class WardDetailOut(BaseModel):
    id: int
    city: str
    name: str
    latitude: float
    longitude: float
    population: Optional[int] = None
    area_km2: Optional[float] = None
    features: dict
    feature_source: str
    feature_observed_at: Optional[datetime] = None
    feature_confidence: float
    score: Optional[float] = None
    category: Optional[str] = None
    confidence: Optional[float] = None
    top_factors: list[FeatureContributionOut] = []
    missing_data_warnings: list[str] = []
    explanation: str = ""
    recommendations: list[str] = []
    geometry_geojson: Optional[str] = None
    is_demo_geometry: Optional[bool] = None
    last_updated: Optional[datetime] = None


class RiskExplanationOut(BaseModel):
    ward_id: int
    ward_name: str
    score: Optional[float] = None
    category: Optional[str] = None
    confidence: Optional[float] = None
    all_factors: list[FeatureContributionOut] = []
    missing_data_warnings: list[str] = []
    explanation: str = ""
    model_version: str = "hybrid-v2"


class TimeseriesPointOut(BaseModel):
    computed_at: datetime
    score: float
    category: str


class TimeseriesOut(BaseModel):
    ward_id: int
    ward_name: str
    points: list[TimeseriesPointOut]


class WeatherSummaryOut(BaseModel):
    air_temp_c: Optional[float] = None
    apparent_temp_c: Optional[float] = None
    humidity_pct: Optional[float] = None
    wind_speed_mps: Optional[float] = None
    badge: DataBadge


class SatelliteSummaryOut(BaseModel):
    scene_id: Optional[str] = None
    lst_c: Optional[float] = None
    ndvi: Optional[float] = None
    ndbi: Optional[float] = None
    cloud_cover_pct: Optional[float] = None
    badge: DataBadge


class DashboardKPIs(BaseModel):
    city_heat_risk: Optional[float] = None
    city_heat_category: Optional[str] = None
    severe_or_extreme_wards: int = 0
    estimated_population_exposed: int = 0
    green_cover_deficit_pct: Optional[float] = None
    total_wards: int = 0


class DashboardOut(BaseModel):
    city: CityOut
    kpis: DashboardKPIs
    wards: list[WardSummaryOut]
    weather: WeatherSummaryOut
    satellite: SatelliteSummaryOut
    generated_at: datetime


class DataSourceStatusOut(BaseModel):
    provider_key: str
    provider_name: str
    mode: str
    connected: bool
    last_refresh_at: Optional[datetime] = None
    last_error: Optional[str] = None
    message: str = ""


class RefreshResult(BaseModel):
    provider_key: str
    mode: str
    message: str
    observed_at: Optional[datetime] = None


class InterventionRecommendationOut(BaseModel):
    key: str
    name: str
    priority_rank: int
    risk_reduction_range: tuple[float, float]
    cooling_impact_range_c: tuple[float, float]
    cost_range_inr_lakh: tuple[float, float]
    timeline_weeks: tuple[int, int]
    population_affected_range: tuple[int, int]
    confidence: str
    assumptions: str
    why_selected: str


class SimulationRequest(BaseModel):
    ward_id: int
    budget_inr_lakh: float = Field(default=15, ge=0, le=2000)
    roof_treatment_pct: float = Field(default=25, ge=0, le=100)
    tree_canopy_target_pct: float = Field(default=8, ge=0, le=30)
    shade_structures: int = Field(default=10, ge=0, le=200)
    infra_focus: str = Field(default="mixed")


class SimulationOut(BaseModel):
    id: int
    ward_id: int
    ward_name: str
    baseline_score: float
    baseline_category: str
    projected_score: float
    projected_category: str
    risk_reduction_pts: float
    risk_reduction_range_pts: tuple[float, float]
    projected_lst_c: float
    allocations: list[dict]
    assumptions: list[str]
    created_at: datetime


class WardReportOut(BaseModel):
    ward: WardDetailOut
    recommended_interventions: list[InterventionRecommendationOut]
    generated_at: datetime
    disclaimer: str
