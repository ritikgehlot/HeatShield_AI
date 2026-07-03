from fastapi.testclient import TestClient
from backend.main import app


def test_cities_list_has_jodhpur():
    with TestClient(app) as client:
        response = client.get("/api/cities")
        assert response.status_code == 200
        cities = response.json()
        assert any(c["name"] == "Jodhpur" for c in cities)
        jodhpur = next(c for c in cities if c["name"] == "Jodhpur")
        assert jodhpur["ward_count"] >= 15  # spec requires >= 15 seeded wards


def test_dashboard_has_kpis_and_wards():
    with TestClient(app) as client:
        city_id = client.get("/api/cities").json()[0]["id"]
        response = client.get(f"/api/cities/{city_id}/dashboard")
        assert response.status_code == 200
        payload = response.json()

        assert payload["kpis"]["total_wards"] >= 15
        assert 0 <= payload["kpis"]["city_heat_risk"] <= 100
        assert len(payload["wards"]) == payload["kpis"]["total_wards"]

        # Every value that matters must carry a mode/source badge — never
        # bare numbers with no provenance.
        assert payload["weather"]["badge"]["mode"] in ("demo", "live", "cached_fallback", "error", "not_configured")
        assert payload["satellite"]["badge"]["mode"] in ("demo", "live", "cached_fallback", "error", "not_configured")

        # Score spread check: guards against the old model's failure mode
        # (11/12 wards clustered at "High" or above).
        categories = {w["category"] for w in payload["wards"]}
        assert len(categories) >= 3, f"expected a real spread of risk categories, got only {categories}"


def test_dashboard_404_for_unknown_city():
    with TestClient(app) as client:
        response = client.get("/api/cities/999999/dashboard")
        assert response.status_code == 404
