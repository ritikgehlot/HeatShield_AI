from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class WardOut(BaseModel):
    id: int
    city: str
    name: str
    latitude: float
    longitude: float
    map_x: float
    map_y: float
    lst_c: float
    ndvi: float
    ndbi: float
    built_up_pct: float
    road_density_km_km2: float
    population_density: float
    vulnerability_index: float
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
