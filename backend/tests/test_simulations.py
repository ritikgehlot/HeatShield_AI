from fastapi.testclient import TestClient
from backend.main import app


def test_create_and_fetch_simulation():
    with TestClient(app) as client:
        city_id = client.get("/api/cities").json()[0]["id"]
        ward_id = client.get(f"/api/cities/{city_id}/dashboard").json()["wards"][0]["id"]

        create_response = client.post(
            "/api/simulations",
            json={
                "ward_id": ward_id,
                "budget_inr_lakh": 25,
                "roof_treatment_pct": 30,
                "tree_canopy_target_pct": 12,
                "shade_structures": 15,
                "infra_focus": "mixed",
            },
        )
        assert create_response.status_code == 200
        created = create_response.json()

        # Core "never over-promise" checks.
        assert created["projected_score"] <= created["baseline_score"]
        assert created["risk_reduction_pts"] >= 0
        lo, hi = created["risk_reduction_range_pts"]
        assert lo <= created["risk_reduction_pts"] <= hi
        assert len(created["assumptions"]) >= 1

        fetch_response = client.get(f"/api/simulations/{created['id']}")
        assert fetch_response.status_code == 200
        fetched = fetch_response.json()
        assert fetched["ward_id"] == ward_id
        assert fetched["baseline_score"] == created["baseline_score"]


def test_simulation_unknown_ward_404():
    with TestClient(app) as client:
        response = client.post(
            "/api/simulations",
            json={"ward_id": 999999, "budget_inr_lakh": 10, "roof_treatment_pct": 10, "tree_canopy_target_pct": 5, "shade_structures": 5},
        )
        assert response.status_code == 404


def test_simulation_not_found():
    with TestClient(app) as client:
        response = client.get("/api/simulations/999999")
        assert response.status_code == 404
