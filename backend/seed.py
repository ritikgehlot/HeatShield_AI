from datetime import datetime, timezone
import json

from sqlalchemy import select
from sqlalchemy.orm import Session

from .models import Ward
from .risk_engine import predict_risk, recommendations

DEMO_WARDS = [
    {"name": "Mandore", "latitude": 26.401, "longitude": 73.042, "map_x": 28, "map_y": 25, "lst_c": 49.4, "ndvi": 0.16, "ndbi": 0.73, "built_up_pct": 79, "road_density_km_km2": 5.2, "population_density": 12800, "vulnerability_index": 0.66},
    {"name": "Paota", "latitude": 26.302, "longitude": 73.024, "map_x": 49, "map_y": 30, "lst_c": 51.1, "ndvi": 0.10, "ndbi": 0.81, "built_up_pct": 88, "road_density_km_km2": 7.6, "population_density": 24100, "vulnerability_index": 0.71},
    {"name": "BJS Colony", "latitude": 26.329, "longitude": 73.031, "map_x": 72, "map_y": 20, "lst_c": 47.8, "ndvi": 0.25, "ndbi": 0.62, "built_up_pct": 69, "road_density_km_km2": 4.8, "population_density": 15300, "vulnerability_index": 0.55},
    {"name": "Sardarpura", "latitude": 26.277, "longitude": 73.004, "map_x": 40, "map_y": 51, "lst_c": 50.6, "ndvi": 0.12, "ndbi": 0.84, "built_up_pct": 90, "road_density_km_km2": 8.2, "population_density": 27600, "vulnerability_index": 0.68},
    {"name": "Ratanada", "latitude": 26.251, "longitude": 73.037, "map_x": 64, "map_y": 51, "lst_c": 44.6, "ndvi": 0.38, "ndbi": 0.49, "built_up_pct": 56, "road_density_km_km2": 4.1, "population_density": 9800, "vulnerability_index": 0.42},
    {"name": "Sojati Gate", "latitude": 26.287, "longitude": 73.018, "map_x": 56, "map_y": 42, "lst_c": 52.2, "ndvi": 0.08, "ndbi": 0.89, "built_up_pct": 93, "road_density_km_km2": 9.4, "population_density": 30100, "vulnerability_index": 0.79},
    {"name": "Shastri Nagar", "latitude": 26.273, "longitude": 73.046, "map_x": 82, "map_y": 47, "lst_c": 48.9, "ndvi": 0.18, "ndbi": 0.70, "built_up_pct": 77, "road_density_km_km2": 6.1, "population_density": 17200, "vulnerability_index": 0.59},
    {"name": "Basni", "latitude": 26.227, "longitude": 73.084, "map_x": 78, "map_y": 71, "lst_c": 53.1, "ndvi": 0.06, "ndbi": 0.92, "built_up_pct": 95, "road_density_km_km2": 6.9, "population_density": 14400, "vulnerability_index": 0.63},
    {"name": "Chopasni", "latitude": 26.249, "longitude": 72.993, "map_x": 29, "map_y": 74, "lst_c": 45.2, "ndvi": 0.34, "ndbi": 0.52, "built_up_pct": 58, "road_density_km_km2": 3.3, "population_density": 8700, "vulnerability_index": 0.37},
    {"name": "Kudi", "latitude": 26.207, "longitude": 73.062, "map_x": 56, "map_y": 84, "lst_c": 49.8, "ndvi": 0.19, "ndbi": 0.74, "built_up_pct": 80, "road_density_km_km2": 5.0, "population_density": 11300, "vulnerability_index": 0.53},
    {"name": "Nai Sadak", "latitude": 26.293, "longitude": 73.016, "map_x": 58, "map_y": 34, "lst_c": 51.7, "ndvi": 0.09, "ndbi": 0.87, "built_up_pct": 92, "road_density_km_km2": 9.1, "population_density": 29400, "vulnerability_index": 0.76},
    {"name": "Pal Road", "latitude": 26.254, "longitude": 72.965, "map_x": 13, "map_y": 58, "lst_c": 43.9, "ndvi": 0.43, "ndbi": 0.43, "built_up_pct": 47, "road_density_km_km2": 2.8, "population_density": 6400, "vulnerability_index": 0.31},
]


def seed_database(session: Session) -> None:
    existing = session.scalar(select(Ward.id).limit(1))
    if existing:
        return

    for data in DEMO_WARDS:
        result = predict_risk(data)
        session.add(
            Ward(
                city="Jodhpur",
                **data,
                risk_score=result.score,
                risk_level=result.risk_level,
                top_drivers=json.dumps(result.top_drivers),
                recommendation=json.dumps(recommendations(data)),
                data_source="Seeded demo data — replace with validated satellite/ward data",
                last_updated=datetime.now(timezone.utc),
            )
        )
    session.commit()
