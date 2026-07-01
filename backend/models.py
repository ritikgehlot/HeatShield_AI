from datetime import datetime, timezone

from sqlalchemy import DateTime, Float, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from .db import Base


class Ward(Base):
    __tablename__ = "wards"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    city: Mapped[str] = mapped_column(String(100), default="Jodhpur", index=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    latitude: Mapped[float] = mapped_column(Float)
    longitude: Mapped[float] = mapped_column(Float)
    map_x: Mapped[float] = mapped_column(Float, default=50.0)
    map_y: Mapped[float] = mapped_column(Float, default=50.0)

    lst_c: Mapped[float] = mapped_column(Float)  # Land surface temperature
    ndvi: Mapped[float] = mapped_column(Float)  # Green-cover index
    ndbi: Mapped[float] = mapped_column(Float)  # Built-up index
    built_up_pct: Mapped[float] = mapped_column(Float)
    road_density_km_km2: Mapped[float] = mapped_column(Float)
    population_density: Mapped[float] = mapped_column(Float)
    vulnerability_index: Mapped[float] = mapped_column(Float)

    risk_score: Mapped[float] = mapped_column(Float, default=0.0, index=True)
    risk_level: Mapped[str] = mapped_column(String(30), default="Medium")
    top_drivers: Mapped[str] = mapped_column(Text, default="[]")
    recommendation: Mapped[str] = mapped_column(Text, default="[]")
    data_source: Mapped[str] = mapped_column(String(120), default="Demo dataset")
    last_updated: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))


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
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
