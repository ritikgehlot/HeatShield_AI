"""Business logic: joins Ward + latest WardFeatureSnapshot + latest
HeatRiskScore (the "current state" pattern models.py documents), CSV/GeoJSON
import for both the V1 and V2 column contracts, dashboard aggregation, and
data-source status refresh.

Performance note: at this dataset's scale (dozens of wards) per-ward lookup
queries for "latest snapshot"/"latest score" are simple and fine. At real
city scale this should become a window-function query instead — flagged
here rather than silently left as a hidden scaling cliff.
"""
from __future__ import annotations

import csv
import io
import json
from datetime import datetime, timezone
from typing import Any, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from .interventions import CATALOG
from .models import (
    City,
    DataSourceStatus,
    HeatRiskScore,
    IngestionRun,
    SatelliteScene,
    Ward,
    WardFeatureSnapshot,
    WardGeometry,
    WeatherObservation,
)
from .providers.geocoding_provider import get_geocoding_provider
from .providers.provider_base import ProviderMode
from .providers.satellite_provider import DemoSatelliteProvider, get_satellite_provider
from .providers.urban_features_provider import get_urban_features_provider
from .providers.weather_provider import DemoWeatherProvider, get_weather_provider
from .risk_engine import derive_recommendations, score_ward

FEATURE_KEYS = [
    "lst_c", "air_temp_c", "humidity_pct", "wind_speed_mps", "ndvi", "ndbi",
    "built_up_pct", "road_density_km_km2", "population_density", "vulnerability_index",
]

V1_REQUIRED_COLUMNS = {
    "name", "latitude", "longitude", "lst_c", "ndvi", "ndbi", "built_up_pct",
    "road_density_km_km2", "population_density", "vulnerability_index",
}
V2_REQUIRED_COLUMNS = {
    "ward_name", "latitude", "longitude", "lst_c", "ndvi", "ndbi", "built_up_pct",
    "road_density_km_km2", "population_density", "vulnerability_index",
}


# --- "current state" lookups ------------------------------------------------
def latest_snapshot(session: Session, ward_id: int) -> Optional[WardFeatureSnapshot]:
    return session.scalar(
        select(WardFeatureSnapshot).where(WardFeatureSnapshot.ward_id == ward_id).order_by(WardFeatureSnapshot.observed_at.desc()).limit(1)
    )


def latest_score(session: Session, ward_id: int) -> Optional[HeatRiskScore]:
    return session.scalar(
        select(HeatRiskScore).where(HeatRiskScore.ward_id == ward_id).order_by(HeatRiskScore.computed_at.desc()).limit(1)
    )


def latest_geometry(session: Session, ward_id: int) -> Optional[WardGeometry]:
    return session.scalar(select(WardGeometry).where(WardGeometry.ward_id == ward_id))


def snapshot_features(snapshot: Optional[WardFeatureSnapshot]) -> dict[str, Any]:
    if not snapshot:
        return {key: None for key in FEATURE_KEYS}
    return {key: getattr(snapshot, key) for key in FEATURE_KEYS}


def _approx_map_xy(lat: float, lon: float, city: City) -> tuple[float, float]:
    scale = 220.0
    x = 50 + (lon - city.center_lon) * scale
    y = 50 - (lat - city.center_lat) * scale
    return max(5.0, min(95.0, x)), max(5.0, min(95.0, y))


# --- Serialization -----------------------------------------------------------
def serialize_ward_summary(session: Session, ward: Ward) -> dict[str, Any]:
    score = latest_score(session, ward.id)
    geometry = latest_geometry(session, ward.id)
    return {
        "id": ward.id,
        "name": ward.name,
        "latitude": ward.centroid_lat,
        "longitude": ward.centroid_lon,
        "map_x": ward.map_x,
        "map_y": ward.map_y,
        "population": ward.population,
        "score": score.score if score else None,
        "category": score.category if score else None,
        "confidence": score.confidence if score else None,
        "last_updated": score.computed_at if score else ward.updated_at,
        "geometry_geojson": geometry.geometry_geojson if geometry else None,
    }


def serialize_ward_detail(session: Session, ward: Ward) -> dict[str, Any]:
    snapshot = latest_snapshot(session, ward.id)
    score_row = latest_score(session, ward.id)
    geometry = latest_geometry(session, ward.id)
    features = snapshot_features(snapshot)

    result = score_ward(features, observed_at=snapshot.observed_at if snapshot else None)

    return {
        "id": ward.id,
        "city": ward.city.name,
        "name": ward.name,
        "latitude": ward.centroid_lat,
        "longitude": ward.centroid_lon,
        "population": ward.population,
        "area_km2": ward.area_km2,
        "features": features,
        "feature_source": snapshot.source if snapshot else "No data imported yet",
        "feature_observed_at": snapshot.observed_at if snapshot else None,
        "feature_confidence": snapshot.confidence if snapshot else 0.0,
        "score": score_row.score if score_row else result.score,
        "category": score_row.category if score_row else result.category,
        "confidence": score_row.confidence if score_row else result.confidence,
        "top_factors": [
            {"key": f.key, "label": f.label, "value": f.value, "normalized_risk": f.normalized_risk, "weight": f.weight, "contribution_pts": f.contribution_pts}
            for f in result.top_factors
        ],
        "missing_data_warnings": result.missing_data_warnings,
        "explanation": result.explanation,
        "recommendations": derive_recommendations(features),
        "geometry_geojson": geometry.geometry_geojson if geometry else None,
        "is_demo_geometry": geometry.is_demo_geometry if geometry else None,
        "last_updated": score_row.computed_at if score_row else ward.updated_at,
    }


def serialize_ward_legacy(session: Session, ward: Ward) -> dict[str, Any]:
    """Matches the original (V1) WardOut shape, backed by the new schema."""
    snapshot = latest_snapshot(session, ward.id)
    score_row = latest_score(session, ward.id)
    features = snapshot_features(snapshot)
    top_factor_labels = [f["label"] for f in (score_row.top_factors or [])] if score_row else []
    return {
        "id": ward.id,
        "city": ward.city.name,
        "name": ward.name,
        "latitude": ward.centroid_lat,
        "longitude": ward.centroid_lon,
        "map_x": ward.map_x,
        "map_y": ward.map_y,
        **features,
        "risk_score": score_row.score if score_row else 0.0,
        "risk_level": score_row.category if score_row else "Low",
        "top_drivers": top_factor_labels,
        "recommendation": derive_recommendations(features),
        "data_source": snapshot.source if snapshot else "No data",
        "last_updated": score_row.computed_at if score_row else ward.updated_at,
    }


# --- Recompute/store ----------------------------------------------------------
def store_snapshot_and_score(session: Session, ward: Ward, features: dict[str, Any], source: str, confidence: float, observed_at: datetime) -> HeatRiskScore:
    snapshot = WardFeatureSnapshot(ward_id=ward.id, source=source, confidence=confidence, observed_at=observed_at, **{k: features.get(k) for k in FEATURE_KEYS})
    session.add(snapshot)
    session.flush()

    result = score_ward(features, observed_at=observed_at)
    score_row = HeatRiskScore(
        ward_id=ward.id,
        snapshot_id=snapshot.id,
        score=result.score,
        category=result.category,
        top_factors=[{"key": f.key, "label": f.label, "value": f.value, "contribution_pts": f.contribution_pts} for f in result.top_factors],
        confidence=result.confidence,
        missing_data_warnings=result.missing_data_warnings,
        computed_at=observed_at,
    )
    session.add(score_row)
    ward.updated_at = observed_at
    return score_row


# --- CSV import (V1 + V2) -----------------------------------------------------
def _get_or_create_city(session: Session, name: str) -> City:
    city = session.scalar(select(City).where(City.name == name))
    if city:
        return city
    city = City(name=name, state="", country="India", center_lat=26.2389, center_lon=73.0243)
    session.add(city)
    session.flush()
    return city


def import_wards_from_csv(session: Session, raw_bytes: bytes) -> tuple[int, int, int, IngestionRun]:
    started_at = datetime.now(timezone.utc)
    text = raw_bytes.decode("utf-8-sig")
    reader = csv.DictReader(io.StringIO(text))
    if not reader.fieldnames:
        raise ValueError("The uploaded file has no header row.")

    headers = set(reader.fieldnames)
    is_v2 = "ward_name" in headers
    required = V2_REQUIRED_COLUMNS if is_v2 else V1_REQUIRED_COLUMNS
    missing = required - headers
    if missing:
        raise ValueError("Missing required columns: " + ", ".join(sorted(missing)))

    imported = updated = skipped = 0
    errors: list[str] = []

    for row_num, row in enumerate(reader, start=2):
        try:
            name = (row["ward_name"] if is_v2 else row["name"]).strip()
            if not name:
                raise ValueError("empty ward name")
            city_name = (row.get("city") or "Jodhpur").strip() or "Jodhpur"
            city = _get_or_create_city(session, city_name)

            features = {
                "lst_c": float(row["lst_c"]),
                "ndvi": float(row["ndvi"]),
                "ndbi": float(row["ndbi"]),
                "built_up_pct": float(row["built_up_pct"]),
                "road_density_km_km2": float(row["road_density_km_km2"]),
                "population_density": float(row["population_density"]),
                "vulnerability_index": float(row["vulnerability_index"]),
                "air_temp_c": float(row["air_temp_c"]) if row.get("air_temp_c") else None,
                "humidity_pct": float(row["humidity_pct"]) if row.get("humidity_pct") else None,
                "wind_speed_mps": float(row["wind_speed_mps"]) if row.get("wind_speed_mps") else None,
            }
            lat, lon = float(row["latitude"]), float(row["longitude"])
            source = (row.get("source") or row.get("data_source") or "Imported CSV").strip() or "Imported CSV"
            confidence = float(row["confidence"]) if row.get("confidence") else 0.75
            observed_at = started_at
            if row.get("observed_at"):
                try:
                    observed_at = datetime.fromisoformat(row["observed_at"]).replace(tzinfo=timezone.utc)
                except ValueError:
                    pass

            ward = session.scalar(select(Ward).where(Ward.city_id == city.id, Ward.name == name))
            if ward:
                ward.centroid_lat, ward.centroid_lon = lat, lon
                updated += 1
            else:
                map_x, map_y = (float(row["map_x"]), float(row["map_y"])) if row.get("map_x") and row.get("map_y") else _approx_map_xy(lat, lon, city)
                ward = Ward(city_id=city.id, name=name, centroid_lat=lat, centroid_lon=lon, map_x=map_x, map_y=map_y)
                session.add(ward)
                session.flush()
                imported += 1

            store_snapshot_and_score(session, ward, features, source, confidence, observed_at)
        except (ValueError, TypeError, KeyError) as exc:
            skipped += 1
            errors.append(f"row {row_num}: {exc}")

    finished_at = datetime.now(timezone.utc)
    run = IngestionRun(
        source_type="csv",
        status="success" if not errors else ("partial" if imported or updated else "failed"),
        rows_imported=imported,
        rows_updated=updated,
        rows_skipped=skipped,
        error_message="; ".join(errors[:20]) if errors else None,
        started_at=started_at,
        finished_at=finished_at,
    )
    session.add(run)
    session.commit()
    return imported, updated, skipped, run


def import_ward_boundaries_geojson(session: Session, raw_bytes: bytes) -> tuple[int, int, IngestionRun]:
    started_at = datetime.now(timezone.utc)
    try:
        payload = json.loads(raw_bytes.decode("utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid GeoJSON: {exc}") from exc

    features = payload.get("features")
    if not isinstance(features, list):
        raise ValueError("GeoJSON must be a FeatureCollection with a 'features' array.")

    matched = unmatched = 0
    errors: list[str] = []
    for feature in features:
        props = feature.get("properties", {}) or {}
        name = (props.get("name") or props.get("ward_name") or "").strip()
        geometry = feature.get("geometry")
        if not name or not geometry:
            unmatched += 1
            errors.append("feature missing name or geometry")
            continue
        ward = session.scalar(select(Ward).where(Ward.name.ilike(name)))
        if not ward:
            unmatched += 1
            errors.append(f"no ward matched name '{name}'")
            continue
        existing = session.scalar(select(WardGeometry).where(WardGeometry.ward_id == ward.id))
        if existing:
            existing.geometry_geojson = json.dumps(geometry)
            existing.source = "Uploaded GeoJSON"
            existing.is_demo_geometry = False
            existing.observed_at = started_at
        else:
            session.add(WardGeometry(ward_id=ward.id, geometry_geojson=json.dumps(geometry), source="Uploaded GeoJSON", is_demo_geometry=False, observed_at=started_at))
        matched += 1

    finished_at = datetime.now(timezone.utc)
    run = IngestionRun(
        source_type="geojson",
        status="success" if not errors else ("partial" if matched else "failed"),
        rows_imported=matched,
        rows_skipped=unmatched,
        error_message="; ".join(errors[:20]) if errors else None,
        started_at=started_at,
        finished_at=finished_at,
    )
    session.add(run)
    session.commit()
    return matched, unmatched, run


def csv_template_rows_v1() -> list[dict]:
    return [{
        "city": "Jodhpur", "name": "Example Ward", "latitude": 26.25, "longitude": 73.02,
        "map_x": 50, "map_y": 50, "lst_c": 48.2, "ndvi": 0.18, "ndbi": 0.72,
        "built_up_pct": 78, "road_density_km_km2": 6.4, "population_density": 18500,
        "vulnerability_index": 0.63, "data_source": "Validated local dataset",
    }]


def csv_template_rows_v2() -> list[dict]:
    return [{
        "city": "Jodhpur", "ward_id": "", "ward_name": "Example Ward",
        "observed_at": datetime.now(timezone.utc).isoformat(), "latitude": 26.25, "longitude": 73.02,
        "lst_c": 48.2, "air_temp_c": 40.5, "humidity_pct": 24, "wind_speed_mps": 3.2,
        "ndvi": 0.18, "ndbi": 0.72, "built_up_pct": 78, "road_density_km_km2": 6.4,
        "population_density": 18500, "vulnerability_index": 0.63,
        "source": "Validated local dataset", "confidence": 0.85,
    }]


# --- Dashboard / provider aggregation -----------------------------------------
def get_weather_summary(session: Session, city: City) -> dict[str, Any]:
    latest = session.scalar(select(WeatherObservation).where(WeatherObservation.city_id == city.id).order_by(WeatherObservation.fetched_at.desc()).limit(1))
    if latest:
        return {
            "air_temp_c": latest.air_temp_c, "apparent_temp_c": latest.apparent_temp_c,
            "humidity_pct": latest.humidity_pct, "wind_speed_mps": latest.wind_speed_mps,
            "badge": {"source": latest.source, "mode": latest.mode, "observed_at": latest.observed_at, "fetched_at": latest.fetched_at, "confidence": None, "message": ""},
        }
    provider = get_weather_provider()
    result = provider.fetch(city.center_lat, city.center_lon) if hasattr(provider, "fetch") else provider.status()
    if result.mode == ProviderMode.ERROR or not result.data:
        # Live attempt genuinely failed and nothing is cached yet. Demo mode must
        # still work with zero keys, so fall back to clearly-labeled demo values
        # rather than showing the dashboard a dead "error" tile — the real error
        # is still visible on the Data Sources page via refresh_data_source_status.
        fallback = DemoWeatherProvider().status()
        fallback.message = f"Live weather unavailable right now ({result.error or 'no response'}) — showing demo values instead."
        result = fallback
    return {
        "air_temp_c": result.data.get("air_temp_c"), "apparent_temp_c": result.data.get("apparent_temp_c"),
        "humidity_pct": result.data.get("humidity_pct"), "wind_speed_mps": result.data.get("wind_speed_mps"),
        "badge": {"source": result.source or result.provider_name, "mode": result.mode.value, "observed_at": result.observed_at, "fetched_at": result.fetched_at, "confidence": None, "message": result.message},
    }


def get_satellite_summary(session: Session, city: City) -> dict[str, Any]:
    latest = session.scalar(select(SatelliteScene).where(SatelliteScene.city_id == city.id).order_by(SatelliteScene.fetched_at.desc()).limit(1))
    if latest:
        return {
            "scene_id": latest.scene_id, "lst_c": latest.lst_c, "ndvi": latest.ndvi, "ndbi": latest.ndbi,
            "cloud_cover_pct": latest.cloud_cover_pct,
            "badge": {"source": latest.source, "mode": latest.mode, "observed_at": latest.observed_at, "fetched_at": latest.fetched_at, "confidence": None, "message": ""},
        }
    provider = get_satellite_provider()
    result = provider.status()
    if result.mode == ProviderMode.ERROR or (not result.data and result.mode != ProviderMode.NOT_CONFIGURED):
        fallback = DemoSatelliteProvider().status()
        fallback.message = f"Live satellite provider unavailable right now ({result.error or 'no response'}) — showing a labeled demo scene instead."
        result = fallback
    return {
        "scene_id": result.data.get("scene_id"), "lst_c": result.data.get("lst_c"), "ndvi": result.data.get("ndvi"), "ndbi": result.data.get("ndbi"),
        "cloud_cover_pct": result.data.get("cloud_cover_pct"),
        "badge": {"source": result.source or result.provider_name, "mode": result.mode.value, "observed_at": result.observed_at, "fetched_at": result.fetched_at, "confidence": None, "message": result.message},
    }


def get_dashboard(session: Session, city: City) -> dict[str, Any]:
    wards = session.scalars(select(Ward).where(Ward.city_id == city.id)).all()
    summaries = [serialize_ward_summary(session, w) for w in wards]

    scored = [s for s in summaries if s["score"] is not None]
    avg_score = round(sum(s["score"] for s in scored) / len(scored), 1) if scored else None
    from .risk_engine import _category  # local import to avoid polluting module namespace

    severe_extreme = [s for s in scored if s["category"] in ("Severe", "Extreme")]
    pop_exposed = sum((s["population"] or 0) for s in severe_extreme)

    ndvi_values = []
    for ward in wards:
        snap = latest_snapshot(session, ward.id)
        if snap and snap.ndvi is not None:
            ndvi_values.append(snap.ndvi)
    green_deficit = round(max(0.0, min(100.0, (1 - (sum(ndvi_values) / len(ndvi_values) if ndvi_values else 0.2) / 0.5) * 100)), 1)

    return {
        "city": {"id": city.id, "name": city.name, "state": city.state, "country": city.country, "center_lat": city.center_lat, "center_lon": city.center_lon, "ward_count": len(wards)},
        "kpis": {
            "city_heat_risk": avg_score,
            "city_heat_category": _category(avg_score) if avg_score is not None else None,
            "severe_or_extreme_wards": len(severe_extreme),
            "estimated_population_exposed": pop_exposed,
            "green_cover_deficit_pct": green_deficit,
            "total_wards": len(wards),
        },
        "wards": summaries,
        "weather": get_weather_summary(session, city),
        "satellite": get_satellite_summary(session, city),
        "generated_at": datetime.now(timezone.utc),
    }


def refresh_data_source_status(session: Session) -> list[DataSourceStatus]:
    """Reports REAL operational status, not just static configuration.

    Earlier version called provider.status() for every provider, which for the
    keyless-live weather provider just asserts "no key needed" — so it showed
    mode=live even in the exact run where the dashboard's actual fetch attempt
    had just failed over to demo. That's the "claims live but isn't" gap this
    whole project exists to avoid, so providers that support a real .fetch()
    are actually exercised here against a representative city, not just
    asked to self-report.
    """
    city = session.scalar(select(City).order_by(City.id.asc()).limit(1))

    weather_provider = get_weather_provider()
    weather_result = (
        weather_provider.fetch(city.center_lat, city.center_lon)
        if city and hasattr(weather_provider, "fetch")
        else weather_provider.status()
    )

    providers_and_results = [
        weather_result,
        get_satellite_provider().status(),
        get_urban_features_provider(live=False).status(),
        get_geocoding_provider(live=False).status(),
    ]
    rows = []
    for result in providers_and_results:
        row = session.scalar(select(DataSourceStatus).where(DataSourceStatus.provider_key == result.provider_key))
        now = datetime.now(timezone.utc)
        if row:
            row.provider_name = result.provider_name
            row.mode = result.mode.value
            row.connected = result.mode in (ProviderMode.LIVE, ProviderMode.DEMO, ProviderMode.CACHED_FALLBACK)
            row.last_refresh_at = now
            row.last_error = result.error
            row.updated_at = now
        else:
            row = DataSourceStatus(
                provider_key=result.provider_key, provider_name=result.provider_name, mode=result.mode.value,
                connected=result.mode in (ProviderMode.LIVE, ProviderMode.DEMO, ProviderMode.CACHED_FALLBACK),
                last_refresh_at=now, last_error=result.error, updated_at=now,
            )
            session.add(row)
        rows.append(row)
    session.commit()
    return rows
