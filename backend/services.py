import csv
import io
import json
from datetime import datetime, timezone
from typing import Iterable

from sqlalchemy import select
from sqlalchemy.orm import Session

from .models import Ward
from .risk_engine import predict_risk, recommendations

REQUIRED_COLUMNS = {
    "name", "latitude", "longitude", "lst_c", "ndvi", "ndbi", "built_up_pct",
    "road_density_km_km2", "population_density", "vulnerability_index"
}


def serialize_ward(ward: Ward) -> dict:
    return {
        "id": ward.id,
        "city": ward.city,
        "name": ward.name,
        "latitude": ward.latitude,
        "longitude": ward.longitude,
        "map_x": ward.map_x,
        "map_y": ward.map_y,
        "lst_c": ward.lst_c,
        "ndvi": ward.ndvi,
        "ndbi": ward.ndbi,
        "built_up_pct": ward.built_up_pct,
        "road_density_km_km2": ward.road_density_km_km2,
        "population_density": ward.population_density,
        "vulnerability_index": ward.vulnerability_index,
        "risk_score": ward.risk_score,
        "risk_level": ward.risk_level,
        "top_drivers": json.loads(ward.top_drivers or "[]"),
        "recommendation": json.loads(ward.recommendation or "[]"),
        "data_source": ward.data_source,
        "last_updated": ward.last_updated,
    }


def ward_features(ward: Ward) -> dict:
    return {
        "lst_c": ward.lst_c,
        "ndvi": ward.ndvi,
        "ndbi": ward.ndbi,
        "built_up_pct": ward.built_up_pct,
        "road_density_km_km2": ward.road_density_km_km2,
        "population_density": ward.population_density,
        "vulnerability_index": ward.vulnerability_index,
    }


def import_wards_from_csv(session: Session, raw_bytes: bytes) -> tuple[int, int, int]:
    text = raw_bytes.decode("utf-8-sig")
    reader = csv.DictReader(io.StringIO(text))
    if not reader.fieldnames:
        raise ValueError("The uploaded file has no header row.")

    headers = set(reader.fieldnames)
    missing = REQUIRED_COLUMNS - headers
    if missing:
        raise ValueError("Missing required columns: " + ", ".join(sorted(missing)))

    imported = updated = skipped = 0
    for row in reader:
        try:
            features = {
                "lst_c": float(row["lst_c"]),
                "ndvi": float(row["ndvi"]),
                "ndbi": float(row["ndbi"]),
                "built_up_pct": float(row["built_up_pct"]),
                "road_density_km_km2": float(row["road_density_km_km2"]),
                "population_density": float(row["population_density"]),
                "vulnerability_index": float(row["vulnerability_index"]),
            }
            prediction = predict_risk(features)
            existing = session.scalar(select(Ward).where(Ward.name == row["name"].strip()))
            payload = {
                "city": row.get("city", "Imported City").strip() or "Imported City",
                "latitude": float(row["latitude"]),
                "longitude": float(row["longitude"]),
                "map_x": float(row.get("map_x", 50)),
                "map_y": float(row.get("map_y", 50)),
                **features,
                "risk_score": prediction.score,
                "risk_level": prediction.risk_level,
                "top_drivers": json.dumps(prediction.top_drivers),
                "recommendation": json.dumps(recommendations(features)),
                "data_source": row.get("data_source", "Imported CSV").strip() or "Imported CSV",
                "last_updated": datetime.now(timezone.utc),
            }
            if existing:
                for key, value in payload.items():
                    setattr(existing, key, value)
                updated += 1
            else:
                session.add(Ward(name=row["name"].strip(), **payload))
                imported += 1
        except (ValueError, TypeError, KeyError):
            skipped += 1
    session.commit()
    return imported, updated, skipped


def csv_template_rows() -> Iterable[dict]:
    return [
        {
            "city": "Jodhpur", "name": "Example Ward", "latitude": 26.25, "longitude": 73.02,
            "map_x": 50, "map_y": 50, "lst_c": 48.2, "ndvi": 0.18, "ndbi": 0.72,
            "built_up_pct": 78, "road_density_km_km2": 6.4, "population_density": 18500,
            "vulnerability_index": 0.63, "data_source": "Validated local dataset"
        }
    ]
