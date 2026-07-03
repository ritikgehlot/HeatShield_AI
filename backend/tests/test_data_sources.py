from fastapi.testclient import TestClient
from backend.main import app


def test_data_sources_status_covers_all_four_providers():
    with TestClient(app) as client:
        response = client.get("/api/data-sources/status")
        assert response.status_code == 200
        rows = response.json()
        keys = {r["provider_key"] for r in rows}
        assert keys == {"weather", "satellite", "urban_features", "geocoding"}
        for row in rows:
            assert row["mode"] in ("demo", "live", "cached_fallback", "not_configured", "error")
            # connected/mode must agree: NOT_CONFIGURED or ERROR is never reported "connected".
            if row["mode"] in ("not_configured", "error"):
                assert row["connected"] is False


def test_satellite_defaults_to_demo_without_gee_credentials():
    with TestClient(app) as client:
        rows = client.get("/api/data-sources/status").json()
        satellite = next(r for r in rows if r["provider_key"] == "satellite")
        # No GEE_* env vars are set in this test environment, so this must be
        # demo, never a fabricated "live" scene.
        assert satellite["mode"] == "demo"
