"""SQLAlchemy models.

12 tables per the V2 spec, plus the original ``ScenarioRun`` table kept so the
legacy /api/simulate endpoint keeps working unchanged. UTC timestamps
throughout. Geometry is stored as GeoJSON text (works identically on SQLite and
PostgreSQL) rather than a PostGIS-specific column type — see
docs/ARCHITECTURE_V2.md for the tradeoff and native-geometry upgrade path.

Design note: ``Ward`` itself holds only stable identity/location fields.
Feature values live in ``WardFeatureSnapshot`` (one row per import/refresh) and
scores live in ``HeatRiskScore`` (one row per computation), so "current" ward
state is always "latest snapshot + latest score" rather than a single mutable
row. This is what makes freshness badges, history, and timeseries endpoints
possible without bolting more mutable columns onto Ward.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import (
    JSON,
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .db import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class City(Base):
    __tablename__ = "cities"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    state: Mapped[str] = mapped_column(String(100), default="")
    country: Mapped[str] = mapped_column(String(100), default="India")
    center_lat: Mapped[float] = mapped_column(Float)
    center_lon: Mapped[float] = mapped_column(Float)
    timezone: Mapped[str] = mapped_column(String(50), default="Asia/Kolkata")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)

    wards: Mapped[list["Ward"]] = relationship(back_populates="city", cascade="all, delete-orphan")


class Ward(Base):
    __tablename__ = "wards"
    __table_args__ = (UniqueConstraint("city_id", "name", name="uq_ward_city_name"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    city_id: Mapped[int] = mapped_column(ForeignKey("cities.id"), index=True)
    name: Mapped[str] = mapped_column(String(120), index=True)
    code: Mapped[str] = mapped_column(String(30), default="")
    population: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    area_km2: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    centroid_lat: Mapped[float] = mapped_column(Float)
    centroid_lon: Mapped[float] = mapped_column(Float)
    map_x: Mapped[float] = mapped_column(Float, default=50.0)  # legacy 0-100 layout fallback
    map_y: Mapped[float] = mapped_column(Float, default=50.0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow, onupdate=utcnow)

    city: Mapped["City"] = relationship(back_populates="wards")


class WardGeometry(Base):
    __tablename__ = "ward_geometries"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    ward_id: Mapped[int] = mapped_column(ForeignKey("wards.id"), unique=True, index=True)
    geometry_geojson: Mapped[str] = mapped_column(Text)  # Polygon/MultiPolygon GeoJSON
    source: Mapped[str] = mapped_column(String(120), default="")
    is_demo_geometry: Mapped[bool] = mapped_column(Boolean, default=True)
    observed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)


class WeatherObservation(Base):
    __tablename__ = "weather_observations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    city_id: Mapped[int] = mapped_column(ForeignKey("cities.id"), index=True)
    ward_id: Mapped[Optional[int]] = mapped_column(ForeignKey("wards.id"), nullable=True, index=True)
    source: Mapped[str] = mapped_column(String(120))
    mode: Mapped[str] = mapped_column(String(20))  # demo | live | cached_fallback
    air_temp_c: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    apparent_temp_c: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    humidity_pct: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    wind_speed_mps: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    cloud_cover_pct: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    precipitation_mm: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    is_forecast: Mapped[bool] = mapped_column(Boolean, default=False)
    observed_at: Mapped[datetime] = mapped_column(DateTime, index=True)
    fetched_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)
    raw_payload: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)


class SatelliteScene(Base):
    __tablename__ = "satellite_scenes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    city_id: Mapped[int] = mapped_column(ForeignKey("cities.id"), index=True)
    ward_id: Mapped[Optional[int]] = mapped_column(ForeignKey("wards.id"), nullable=True, index=True)
    source: Mapped[str] = mapped_column(String(120))
    scene_id: Mapped[str] = mapped_column(String(200))
    mode: Mapped[str] = mapped_column(String(20))  # demo | live | not_configured
    observed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True, index=True)
    cloud_cover_pct: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    processing_status: Mapped[str] = mapped_column(String(40), default="unknown")
    geometry_coverage: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    lst_c: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    ndvi: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    ndbi: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    fetched_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)


class WardFeatureSnapshot(Base):
    __tablename__ = "ward_feature_snapshots"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    ward_id: Mapped[int] = mapped_column(ForeignKey("wards.id"), index=True)
    source: Mapped[str] = mapped_column(String(120))
    confidence: Mapped[float] = mapped_column(Float, default=0.6)
    lst_c: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    air_temp_c: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    humidity_pct: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    wind_speed_mps: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    ndvi: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    ndbi: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    built_up_pct: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    road_density_km_km2: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    population_density: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    vulnerability_index: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    observed_at: Mapped[datetime] = mapped_column(DateTime, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow, index=True)


class HeatRiskScore(Base):
    __tablename__ = "heat_risk_scores"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    ward_id: Mapped[int] = mapped_column(ForeignKey("wards.id"), index=True)
    snapshot_id: Mapped[Optional[int]] = mapped_column(ForeignKey("ward_feature_snapshots.id"), nullable=True)
    score: Mapped[float] = mapped_column(Float)
    category: Mapped[str] = mapped_column(String(20))  # Low/Moderate/High/Severe/Extreme
    top_factors: Mapped[list] = mapped_column(JSON, default=list)
    confidence: Mapped[float] = mapped_column(Float, default=0.6)
    missing_data_warnings: Mapped[list] = mapped_column(JSON, default=list)
    model_version: Mapped[str] = mapped_column(String(40), default="hybrid-v2")
    computed_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow, index=True)


class InterventionCatalog(Base):
    __tablename__ = "intervention_catalog"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    key: Mapped[str] = mapped_column(String(60), unique=True)
    name: Mapped[str] = mapped_column(String(150))
    description: Mapped[str] = mapped_column(Text, default="")
    unit_cost_min_inr_lakh: Mapped[float] = mapped_column(Float)
    unit_cost_max_inr_lakh: Mapped[float] = mapped_column(Float)
    cooling_impact_min_c: Mapped[float] = mapped_column(Float)
    cooling_impact_max_c: Mapped[float] = mapped_column(Float)
    risk_reduction_min_pts: Mapped[float] = mapped_column(Float)
    risk_reduction_max_pts: Mapped[float] = mapped_column(Float)
    timeline_weeks_min: Mapped[int] = mapped_column(Integer)
    timeline_weeks_max: Mapped[int] = mapped_column(Integer)
    assumptions: Mapped[str] = mapped_column(Text, default="")


class InterventionSimulation(Base):
    __tablename__ = "intervention_simulations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    ward_id: Mapped[int] = mapped_column(ForeignKey("wards.id"), index=True)
    budget_inr_lakh: Mapped[float] = mapped_column(Float)
    roof_treatment_pct: Mapped[float] = mapped_column(Float, default=0.0)
    tree_canopy_target_pct: Mapped[float] = mapped_column(Float, default=0.0)
    shade_structures: Mapped[int] = mapped_column(Integer, default=0)
    infra_focus: Mapped[str] = mapped_column(String(60), default="mixed")
    baseline_score: Mapped[float] = mapped_column(Float)
    projected_score: Mapped[float] = mapped_column(Float)
    risk_reduction_pts: Mapped[float] = mapped_column(Float)
    allocations: Mapped[list] = mapped_column(JSON, default=list)
    assumptions: Mapped[list] = mapped_column(JSON, default=list)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow, index=True)


class IngestionRun(Base):
    __tablename__ = "ingestion_runs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    source_type: Mapped[str] = mapped_column(String(40))  # csv | geojson | weather_refresh | satellite_refresh
    status: Mapped[str] = mapped_column(String(20), default="success")  # success | partial | failed
    rows_imported: Mapped[int] = mapped_column(Integer, default=0)
    rows_updated: Mapped[int] = mapped_column(Integer, default=0)
    rows_skipped: Mapped[int] = mapped_column(Integer, default=0)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    started_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow, index=True)
    finished_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)


class DataSourceStatus(Base):
    __tablename__ = "data_source_status"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    provider_key: Mapped[str] = mapped_column(String(60), unique=True)  # weather|satellite|urban_features|geocoding
    provider_name: Mapped[str] = mapped_column(String(120))
    mode: Mapped[str] = mapped_column(String(20))  # demo | live | not_configured | error
    connected: Mapped[bool] = mapped_column(Boolean, default=False)
    last_refresh_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    last_error: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow, onupdate=utcnow)


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    action: Mapped[str] = mapped_column(String(80), index=True)
    entity_type: Mapped[str] = mapped_column(String(60), default="")
    entity_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    detail: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow, index=True)


# Retained so the original prototype's /api/simulate endpoint keeps working
# unchanged; new code should use InterventionSimulation instead.
class ScenarioRun(Base):
    __tablename__ = "scenario_runs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    ward_id: Mapped[int] = mapped_column(Integer, index=True)
    cool_roof_coverage: Mapped[float] = mapped_column(Float)
    tree_cover_gain: Mapped[float] = mapped_column(Float)
    shade_units: Mapped[int] = mapped_column(Integer)
    budget_lakh: Mapped[float] = mapped_column(Float)
    baseline_score: Mapped[float] = mapped_column(Float)
    projected_score: Mapped[float] = mapped_column(Float)
    projected_lst_c: Mapped[float] = mapped_column(Float)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)
