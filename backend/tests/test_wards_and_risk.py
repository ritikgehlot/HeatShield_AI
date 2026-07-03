from fastapi.testclient import TestClient
from backend.main import app


def _ward_id_by_name(client, name: str) -> int:
    city_id = client.get("/api/cities").json()[0]["id"]
    wards = client.get(f"/api/cities/{city_id}/dashboard").json()["wards"]
    return next(w["id"] for w in wards if w["name"] == name)


def test_ward_detail_has_explainable_score():
    with TestClient(app) as client:
        # "Ratanada" specifically — not the ward test_uploads.py's GeoJSON test
        # overwrites ("Mandore"), so its seeded is_demo_geometry stays True
        # regardless of test execution order.
        ward_id = _ward_id_by_name(client, "Ratanada")
        response = client.get(f"/api/wards/{ward_id}")
        assert response.status_code == 200
        payload = response.json()

        assert payload["score"] is not None
        assert payload["category"] in ("Low", "Moderate", "High", "Severe", "Extreme")
        assert 0 <= payload["confidence"] <= 1
        assert len(payload["top_factors"]) == 3
        assert payload["explanation"]  # non-empty, human-readable
        assert payload["geometry_geojson"] is not None
        assert payload["is_demo_geometry"] is True  # seeded placeholder, honestly labeled


def test_ward_detail_404():
    with TestClient(app) as client:
        response = client.get("/api/wards/999999")
        assert response.status_code == 404


def test_risk_explanation_matches_all_nine_features():
    with TestClient(app) as client:
        ward_id = _ward_id_by_name(client, "Ratanada")
        response = client.get(f"/api/wards/{ward_id}/risk-explanation")
        assert response.status_code == 200
        payload = response.json()
        assert len(payload["all_factors"]) == 9  # every weighted feature, present or missing
        # Contributions from present features should sum to ~the total score
        total_contribution = sum(f["contribution_pts"] for f in payload["all_factors"])
        assert abs(total_contribution - payload["score"]) < 0.5


def test_ward_timeseries_has_at_least_one_point():
    with TestClient(app) as client:
        ward_id = _ward_id_by_name(client, "Ratanada")
        response = client.get(f"/api/wards/{ward_id}/timeseries")
        assert response.status_code == 200
        payload = response.json()
        assert len(payload["points"]) >= 1
