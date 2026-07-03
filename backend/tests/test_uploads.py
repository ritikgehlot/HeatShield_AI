import io

from fastapi.testclient import TestClient
from backend.main import app

V1_CSV = (
    "city,name,latitude,longitude,map_x,map_y,lst_c,ndvi,ndbi,built_up_pct,"
    "road_density_km_km2,population_density,vulnerability_index,data_source\n"
    "Jodhpur,Test Ward V1,26.26,73.01,55,55,47.5,0.22,0.61,65,4.5,13000,0.5,Test upload\n"
)

V2_CSV = (
    "city,ward_id,ward_name,observed_at,latitude,longitude,lst_c,air_temp_c,humidity_pct,"
    "wind_speed_mps,ndvi,ndbi,built_up_pct,road_density_km_km2,population_density,"
    "vulnerability_index,source,confidence\n"
    "Jodhpur,,Test Ward V2,2026-07-01T10:00:00,26.27,73.03,44.1,39.2,30,3.8,0.4,0.45,52,3.1,7200,0.35,Test upload,0.9\n"
)

INVALID_CSV = "name,latitude,longitude\nIncomplete Ward,26.2,73.0\n"  # missing required feature columns


def test_v1_csv_upload_creates_ward():
    with TestClient(app) as client:
        response = client.post(
            "/api/upload/ward-features-csv",
            files={"file": ("v1.csv", io.BytesIO(V1_CSV.encode()), "text/csv")},
        )
        assert response.status_code == 200
        payload = response.json()
        assert payload["imported"] == 1
        assert payload["skipped"] == 0

        wards = client.get("/api/wards").json()
        assert any(w["name"] == "Test Ward V1" for w in wards)


def test_v2_csv_upload_creates_ward_with_confidence():
    with TestClient(app) as client:
        response = client.post(
            "/api/upload/ward-features-csv",
            files={"file": ("v2.csv", io.BytesIO(V2_CSV.encode()), "text/csv")},
        )
        assert response.status_code == 200
        payload = response.json()
        assert payload["imported"] == 1

        wards = client.get("/api/wards").json()
        new_ward = next(w for w in wards if w["name"] == "Test Ward V2")
        assert new_ward["data_source"] == "Test upload"


def test_invalid_csv_returns_400_not_500():
    with TestClient(app) as client:
        response = client.post(
            "/api/upload/ward-features-csv",
            files={"file": ("bad.csv", io.BytesIO(INVALID_CSV.encode()), "text/csv")},
        )
        assert response.status_code == 400
        assert "Missing required columns" in response.json()["detail"]


def test_non_csv_file_rejected():
    with TestClient(app) as client:
        response = client.post(
            "/api/upload/ward-features-csv",
            files={"file": ("notes.txt", io.BytesIO(b"hello"), "text/plain")},
        )
        assert response.status_code == 400


def test_geojson_boundary_upload_matches_existing_ward():
    geojson = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "properties": {"name": "Mandore"},
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [[[73.04, 26.40], [73.05, 26.40], [73.05, 26.41], [73.04, 26.41], [73.04, 26.40]]],
                },
            },
            {
                "type": "Feature",
                "properties": {"name": "Nonexistent Ward XYZ"},
                "geometry": {"type": "Polygon", "coordinates": [[[0, 0], [0, 1], [1, 1], [0, 0]]]},
            },
        ],
    }
    import json

    with TestClient(app) as client:
        response = client.post(
            "/api/upload/ward-boundaries-geojson",
            files={"file": ("boundaries.geojson", io.BytesIO(json.dumps(geojson).encode()), "application/geo+json")},
        )
        assert response.status_code == 200
        payload = response.json()
        assert payload["matched"] == 1
        assert payload["unmatched"] == 1

        wards = client.get("/api/cities").json()
        city_id = wards[0]["id"]
        dashboard = client.get(f"/api/cities/{city_id}/dashboard").json()
        mandore = next(w for w in dashboard["wards"] if w["name"] == "Mandore")
        assert "73.04" in mandore["geometry_geojson"] or "73.05" in mandore["geometry_geojson"]
