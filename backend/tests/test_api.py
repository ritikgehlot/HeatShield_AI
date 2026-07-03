from fastapi.testclient import TestClient
from backend.main import app


def test_dashboard_endpoints_work():
    with TestClient(app) as client:
        health = client.get("/api/health")
        assert health.status_code == 200
        assert health.json()["status"] == "ok"

        wards = client.get("/api/wards")
        assert wards.status_code == 200
        assert len(wards.json()) >= 10

        summary = client.get("/api/summary")
        assert summary.status_code == 200
        assert summary.json()["total_wards"] >= 10


def test_simulator_returns_comparison():
    with TestClient(app) as client:
        ward = client.get("/api/wards").json()[0]
        response = client.post(
            "/api/simulate",
            json={
                "ward_id": ward["id"],
                "cool_roof_coverage": 40,
                "tree_cover_gain": 10,
                "shade_units": 10,
                "budget_lakh": 20,
            },
        )
        assert response.status_code == 200
        payload = response.json()
        assert payload["projected_score"] <= payload["baseline_score"]
        assert payload["risk_reduction"] >= 0
    with TestClient(app) as client:
        health = client.get("/api/health")
        assert health.status_code == 200
        assert health.json()["status"] == "ok"

        wards = client.get("/api/wards")
        assert wards.status_code == 200
        assert len(wards.json()) >= 10

        summary = client.get("/api/summary")
        assert summary.status_code == 200
        assert summary.json()["total_wards"] >= 10


def test_simulator_returns_comparison():
    with TestClient(app) as client:
        ward = client.get("/api/wards").json()[0]
        response = client.post(
            "/api/simulate",
            json={
                "ward_id": ward["id"],
                "cool_roof_coverage": 40,
                "tree_cover_gain": 10,
                "shade_units": 10,
                "budget_lakh": 20,
            },
        )
        assert response.status_code == 200
        payload = response.json()
        assert payload["projected_score"] <= payload["baseline_score"]
        assert payload["risk_reduction"] >= 0
