import csv
import io
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import City, SatelliteScene, WeatherObservation
from ..providers.provider_base import ProviderMode
from ..providers.satellite_provider import get_satellite_provider
from ..providers.weather_provider import get_weather_provider
from ..schemas import DataSourceStatusOut, RefreshResult, UploadResult
from ..services import (
    csv_template_rows_v1,
    csv_template_rows_v2,
    import_ward_boundaries_geojson,
    import_wards_from_csv,
    refresh_data_source_status,
)

router = APIRouter(tags=["data"])


def _first_city(db: Session) -> City:
    city = db.scalar(select(City).order_by(City.id.asc()).limit(1))
    if not city:
        raise HTTPException(status_code=404, detail="No city configured yet — import ward data first.")
    return city


@router.post("/api/refresh/weather", response_model=RefreshResult)
def refresh_weather(city_id: int | None = None, db: Session = Depends(get_db)):
    city = db.get(City, city_id) if city_id else _first_city(db)
    if not city:
        raise HTTPException(status_code=404, detail="City not found")

    provider = get_weather_provider()
    result = provider.fetch(city.center_lat, city.center_lon) if hasattr(provider, "fetch") else provider.status()

    if result.mode in (ProviderMode.LIVE, ProviderMode.CACHED_FALLBACK, ProviderMode.DEMO) and result.data:
        db.add(
            WeatherObservation(
                city_id=city.id, source=result.source or result.provider_name, mode=result.mode.value,
                air_temp_c=result.data.get("air_temp_c"), apparent_temp_c=result.data.get("apparent_temp_c"),
                humidity_pct=result.data.get("humidity_pct"), wind_speed_mps=result.data.get("wind_speed_mps"),
                cloud_cover_pct=result.data.get("cloud_cover_pct"), precipitation_mm=result.data.get("precipitation_mm"),
                observed_at=result.observed_at or datetime.now(timezone.utc), fetched_at=result.fetched_at,
            )
        )
    refresh_data_source_status(db)
    db.commit()
    return {"provider_key": "weather", "mode": result.mode.value, "message": result.message, "observed_at": result.observed_at}


@router.post("/api/refresh/satellite", response_model=RefreshResult)
def refresh_satellite(city_id: int | None = None, db: Session = Depends(get_db)):
    city = db.get(City, city_id) if city_id else _first_city(db)
    if not city:
        raise HTTPException(status_code=404, detail="City not found")

    provider = get_satellite_provider()
    result = provider.status()

    if result.mode == ProviderMode.DEMO and result.data:
        db.add(
            SatelliteScene(
                city_id=city.id, source=result.source or result.provider_name, scene_id=result.data.get("scene_id", "unknown"),
                mode=result.mode.value, observed_at=result.observed_at, cloud_cover_pct=result.data.get("cloud_cover_pct"),
                processing_status=result.data.get("processing_status", "unknown"), lst_c=result.data.get("lst_c"),
                ndvi=result.data.get("ndvi"), ndbi=result.data.get("ndbi"), fetched_at=result.fetched_at,
            )
        )
    refresh_data_source_status(db)
    db.commit()
    return {"provider_key": "satellite", "mode": result.mode.value, "message": result.message, "observed_at": result.observed_at}


@router.post("/api/upload/ward-features-csv", response_model=UploadResult)
async def upload_ward_features_csv(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not file.filename or not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Please upload a .csv file.")
    try:
        raw = await file.read()
        imported, updated, skipped, run = import_wards_from_csv(db, raw)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"imported": imported, "updated": updated, "skipped": skipped, "message": f"Import run #{run.id}: risk scores recomputed for imported/updated wards."}


@router.post("/api/upload/ward-boundaries-geojson")
async def upload_ward_boundaries(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not file.filename or not file.filename.lower().endswith((".geojson", ".json")):
        raise HTTPException(status_code=400, detail="Please upload a .geojson or .json file.")
    try:
        raw = await file.read()
        matched, unmatched, run = import_ward_boundaries_geojson(db, raw)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"matched": matched, "unmatched": unmatched, "message": f"Import run #{run.id}: {matched} ward boundaries updated, {unmatched} unmatched."}


@router.get("/api/data-sources/status", response_model=list[DataSourceStatusOut])
def data_sources_status(db: Session = Depends(get_db)):
    rows = refresh_data_source_status(db)
    return [
        {"provider_key": r.provider_key, "provider_name": r.provider_name, "mode": r.mode, "connected": r.connected, "last_refresh_at": r.last_refresh_at, "last_error": r.last_error, "message": ""}
        for r in rows
    ]


@router.get("/api/data/template")
def download_csv_template(version: str = Query(default="v1", pattern="^(v1|v2)$")):
    rows = csv_template_rows_v2() if version == "v2" else csv_template_rows_v1()
    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=list(rows[0].keys()))
    writer.writeheader()
    writer.writerows(rows)
    filename = "heatshield_import_template_v2.csv" if version == "v2" else "heatshield_import_template.csv"
    return StreamingResponse(iter([buffer.getvalue()]), media_type="text/csv", headers={"Content-Disposition": f"attachment; filename={filename}"})
