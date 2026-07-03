"""Demo dataset: one Jodhpur city record, 16 wards (>= the 15 required),
simplified placeholder polygons, feature snapshots, computed risk scores, the
intervention catalog, and initial data-source status rows.

Ward lat/longs are approximately correct real Jodhpur locality positions;
feature values (LST, NDVI, etc.) are explicitly labeled demo/seeded, not
measured. Ward boundary polygons are simplified squares around each centroid,
NOT official municipal boundaries — see WardGeometry.is_demo_geometry.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from .interventions import CATALOG
from .models import (
    City,
    DataSourceStatus,
    HeatRiskScore,
    InterventionCatalog,
    Ward,
    WardFeatureSnapshot,
    WardGeometry,
)
from .risk_engine import score_ward

JODHPUR = {"name": "Jodhpur", "state": "Rajasthan", "country": "India", "center_lat": 26.2389, "center_lon": 73.0243}

# name, lat, lon, legacy map_x/map_y (0-100, CSS-map fallback), area_km2, then feature dict
DEMO_WARDS = [
    ("Mandore", 26.401, 73.042, 28, 25, 3.4, dict(lst_c=49.4, air_temp_c=40.6, humidity_pct=23, wind_speed_mps=3.1, ndvi=0.16, ndbi=0.73, built_up_pct=79, road_density_km_km2=5.2, population_density=12800, vulnerability_index=0.66)),
    ("Paota", 26.302, 73.024, 49, 30, 2.1, dict(lst_c=51.1, air_temp_c=41.2, humidity_pct=21, wind_speed_mps=2.8, ndvi=0.10, ndbi=0.81, built_up_pct=88, road_density_km_km2=7.6, population_density=24100, vulnerability_index=0.71)),
    ("BJS Colony", 26.329, 73.031, 72, 20, 2.6, dict(lst_c=47.8, air_temp_c=40.1, humidity_pct=25, wind_speed_mps=3.4, ndvi=0.25, ndbi=0.62, built_up_pct=69, road_density_km_km2=4.8, population_density=15300, vulnerability_index=0.55)),
    ("Sardarpura", 26.277, 73.004, 40, 51, 1.9, dict(lst_c=50.6, air_temp_c=41.0, humidity_pct=22, wind_speed_mps=2.6, ndvi=0.12, ndbi=0.84, built_up_pct=90, road_density_km_km2=8.2, population_density=27600, vulnerability_index=0.68)),
    ("Ratanada", 26.251, 73.037, 64, 51, 3.9, dict(lst_c=44.6, air_temp_c=39.4, humidity_pct=27, wind_speed_mps=3.7, ndvi=0.38, ndbi=0.49, built_up_pct=56, road_density_km_km2=4.1, population_density=9800, vulnerability_index=0.42)),
    ("Sojati Gate", 26.287, 73.018, 56, 42, 1.4, dict(lst_c=52.2, air_temp_c=41.6, humidity_pct=19, wind_speed_mps=2.3, ndvi=0.08, ndbi=0.89, built_up_pct=93, road_density_km_km2=9.4, population_density=30100, vulnerability_index=0.79)),
    ("Shastri Nagar", 26.273, 73.046, 82, 47, 2.8, dict(lst_c=48.9, air_temp_c=40.3, humidity_pct=24, wind_speed_mps=3.2, ndvi=0.18, ndbi=0.70, built_up_pct=77, road_density_km_km2=6.1, population_density=17200, vulnerability_index=0.59)),
    ("Basni", 26.227, 73.084, 78, 71, 4.5, dict(lst_c=53.1, air_temp_c=41.9, humidity_pct=18, wind_speed_mps=2.4, ndvi=0.06, ndbi=0.92, built_up_pct=95, road_density_km_km2=6.9, population_density=14400, vulnerability_index=0.63)),
    ("Chopasni", 26.249, 72.993, 29, 74, 3.7, dict(lst_c=45.2, air_temp_c=39.6, humidity_pct=28, wind_speed_mps=3.9, ndvi=0.34, ndbi=0.52, built_up_pct=58, road_density_km_km2=3.3, population_density=8700, vulnerability_index=0.37)),
    ("Kudi", 26.207, 73.062, 56, 84, 3.1, dict(lst_c=49.8, air_temp_c=40.7, humidity_pct=23, wind_speed_mps=3.0, ndvi=0.19, ndbi=0.74, built_up_pct=80, road_density_km_km2=5.0, population_density=11300, vulnerability_index=0.53)),
    ("Nai Sadak", 26.293, 73.016, 58, 34, 1.1, dict(lst_c=51.7, air_temp_c=41.4, humidity_pct=20, wind_speed_mps=2.5, ndvi=0.09, ndbi=0.87, built_up_pct=92, road_density_km_km2=9.1, population_density=29400, vulnerability_index=0.76)),
    ("Pal Road", 26.254, 72.965, 13, 58, 5.2, dict(lst_c=43.9, air_temp_c=39.0, humidity_pct=29, wind_speed_mps=4.1, ndvi=0.43, ndbi=0.43, built_up_pct=47, road_density_km_km2=2.8, population_density=6400, vulnerability_index=0.31)),
    ("Airport Road", 26.259, 73.049, 62, 62, 4.0, dict(lst_c=46.5, air_temp_c=39.8, humidity_pct=26, wind_speed_mps=3.5, ndvi=0.29, ndbi=0.55, built_up_pct=61, road_density_km_km2=4.4, population_density=10200, vulnerability_index=0.46)),
    ("Banar", 26.334, 73.070, 85, 15, 4.8, dict(lst_c=45.9, air_temp_c=39.7, humidity_pct=27, wind_speed_mps=3.6, ndvi=0.31, ndbi=0.51, built_up_pct=54, road_density_km_km2=3.6, population_density=7600, vulnerability_index=0.40)),
    ("Jalori Gate", 26.281, 73.031, 60, 40, 1.0, dict(lst_c=52.6, air_temp_c=41.8, humidity_pct=18, wind_speed_mps=2.2, ndvi=0.07, ndbi=0.90, built_up_pct=94, road_density_km_km2=9.8, population_density=31200, vulnerability_index=0.81)),
    ("Circuit House", 26.294, 73.038, 66, 33, 2.3, dict(lst_c=46.8, air_temp_c=39.9, humidity_pct=25, wind_speed_mps=3.3, ndvi=0.33, ndbi=0.48, built_up_pct=55, road_density_km_km2=3.9, population_density=9100, vulnerability_index=0.44)),
]


def _square_polygon(lat: float, lon: float, half_size_deg: float = 0.006) -> dict:
    return {
        "type": "Polygon",
        "coordinates": [[
            [lon - half_size_deg, lat - half_size_deg],
            [lon + half_size_deg, lat - half_size_deg],
            [lon + half_size_deg, lat + half_size_deg],
            [lon - half_size_deg, lat + half_size_deg],
            [lon - half_size_deg, lat - half_size_deg],
        ]],
    }


def seed_database(session: Session) -> None:
    if session.scalar(select(Ward.id).limit(1)):
        return

    city = City(**JODHPUR)
    session.add(city)
    session.flush()

    now = datetime.now(timezone.utc)

    for name, lat, lon, map_x, map_y, area_km2, features in DEMO_WARDS:
        population = int(features["population_density"] * area_km2)
        ward = Ward(
            city_id=city.id,
            name=name,
            centroid_lat=lat,
            centroid_lon=lon,
            map_x=map_x,
            map_y=map_y,
            area_km2=area_km2,
            population=population,
        )
        session.add(ward)
        session.flush()

        session.add(
            WardGeometry(
                ward_id=ward.id,
                geometry_geojson=json.dumps(_square_polygon(lat, lon)),
                source="Simplified placeholder — not an official municipal boundary",
                is_demo_geometry=True,
                observed_at=now,
            )
        )

        snapshot = WardFeatureSnapshot(
            ward_id=ward.id,
            source="Seeded demo dataset — replace with validated satellite/ward data",
            confidence=0.6,
            observed_at=now,
            **features,
        )
        session.add(snapshot)
        session.flush()

        result = score_ward(features, observed_at=now)
        session.add(
            HeatRiskScore(
                ward_id=ward.id,
                snapshot_id=snapshot.id,
                score=result.score,
                category=result.category,
                top_factors=[{"key": f.key, "label": f.label, "value": f.value, "contribution_pts": f.contribution_pts} for f in result.top_factors],
                confidence=result.confidence,
                missing_data_warnings=result.missing_data_warnings,
                computed_at=now,
            )
        )

    for entry in CATALOG:
        session.add(
            InterventionCatalog(
                key=entry["key"],
                name=entry["name"],
                description=entry["description"],
                unit_cost_min_inr_lakh=entry["unit_cost_min_inr_lakh"],
                unit_cost_max_inr_lakh=entry["unit_cost_max_inr_lakh"],
                cooling_impact_min_c=entry["cooling_impact_min_c"],
                cooling_impact_max_c=entry["cooling_impact_max_c"],
                risk_reduction_min_pts=entry["risk_reduction_min_pts"],
                risk_reduction_max_pts=entry["risk_reduction_max_pts"],
                timeline_weeks_min=entry["timeline_weeks_min"],
                timeline_weeks_max=entry["timeline_weeks_max"],
                assumptions=entry["assumptions"],
            )
        )

    for provider_key, provider_name in [
        ("weather", "Open-Meteo (demo until refreshed live)"),
        ("satellite", "Demo satellite scene (synthetic)"),
        ("urban_features", "Demo urban features (seeded/CSV)"),
        ("geocoding", "Demo geocoding (static registry)"),
    ]:
        session.add(
            DataSourceStatus(
                provider_key=provider_key,
                provider_name=provider_name,
                mode="demo",
                connected=True,
                last_refresh_at=now,
                updated_at=now,
            )
        )

    session.commit()
