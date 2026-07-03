"""Satellite provider adapters.

Satellite imagery is never "live" in the second-by-second sense — the UI must
always say "latest available scene" with an explicit observation date, never
imply real-time capture. See Phase 3-C of the spec this was built against.

DemoSatelliteProvider returns clearly-labeled synthetic scene metadata (fake
scene IDs, explicit demo message) so the UI has something to render before any
real credentials exist. GoogleEarthEngineProvider and CopernicusProvider
define the real integration contract but require credentials this session
does not have — without them they report NOT_CONFIGURED, never a fabricated
scene.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

from ..config import settings
from .provider_base import ProviderBase, ProviderMode, ProviderResult

# Deterministic pseudo-realistic demo scene — same "acquisition" every time
# demo mode is used, so nobody mistakes it for a fresh live pull.
DEMO_SCENE = {
    "scene_id": "DEMO-LANDSAT8-JODHPUR-000000",
    "lst_c": 49.6,
    "ndvi": 0.17,
    "ndbi": 0.71,
    "cloud_cover_pct": 4.0,
    "processing_status": "demo_synthetic",
}


class DemoSatelliteProvider(ProviderBase):
    provider_key = "satellite"
    provider_name = "Demo satellite scene (synthetic)"

    def status(self) -> ProviderResult:
        observed_at = datetime.now(timezone.utc) - timedelta(days=3)
        return ProviderResult(
            provider_key=self.provider_key,
            provider_name=self.provider_name,
            mode=ProviderMode.DEMO,
            data=dict(DEMO_SCENE),
            source="Synthetic demo scene — not a real satellite acquisition",
            observed_at=observed_at,
            message=(
                "Demo mode: this is a labeled synthetic scene for layout/testing, "
                "not a real Landsat/Sentinel acquisition."
            ),
        )


class GoogleEarthEngineProvider(ProviderBase):
    provider_key = "satellite"
    provider_name = "Google Earth Engine"

    def status(self) -> ProviderResult:
        if not settings.satellite_live_configured or settings.satellite_provider != "gee":
            return ProviderResult(
                provider_key=self.provider_key,
                provider_name=self.provider_name,
                mode=ProviderMode.NOT_CONFIGURED,
                message=(
                    "Satellite connection not configured. Set SATELLITE_PROVIDER=gee, "
                    "GEE_PROJECT_ID, GEE_SERVICE_ACCOUNT_EMAIL and GEE_CREDENTIALS_PATH "
                    "to enable Google Earth Engine."
                ),
            )
        try:
            return self._fetch_latest_scene()
        except Exception as exc:  # auth failure, quota, network, etc.
            return ProviderResult(
                provider_key=self.provider_key,
                provider_name=self.provider_name,
                mode=ProviderMode.ERROR,
                message="Google Earth Engine call failed.",
                error=str(exc),
            )

    def _fetch_latest_scene(self, latitude: float | None = None, longitude: float | None = None) -> ProviderResult:
        """Real GEE integration contract. Requires the `earthengine-api` package
        and valid service-account credentials, neither of which exist in this
        sandbox, so this path is written but has not been executed against a
        real Earth Engine project — verify it on your own machine once
        credentials are in place, and treat the shape below as a starting
        point rather than a guarantee of the exact Earth Engine API surface.
        """
        import ee  # noqa: F401  # earthengine-api; not installed in this sandbox

        ee.Initialize(project=settings.gee_project_id)
        # Pseudocode-level outline of the real query, intentionally not
        # claimed as tested:
        #   collection = ee.ImageCollection("LANDSAT/LC08/C02/T1_L2")
        #     .filterBounds(ee.Geometry.Point(longitude, latitude))
        #     .sort("system:time_start", False)
        #   scene = collection.first()
        #   ... derive LST from thermal band, NDVI/NDBI from optical bands ...
        raise NotImplementedError(
            "GEE query logic is scaffolded but not implemented against a real "
            "project in this session — see the docstring for the intended shape."
        )


class CopernicusProvider(ProviderBase):
    provider_key = "satellite"
    provider_name = "Copernicus / Sentinel"

    def status(self) -> ProviderResult:
        if not settings.satellite_live_configured or settings.satellite_provider != "copernicus":
            return ProviderResult(
                provider_key=self.provider_key,
                provider_name=self.provider_name,
                mode=ProviderMode.NOT_CONFIGURED,
                message=(
                    "Satellite connection not configured. Set SATELLITE_PROVIDER=copernicus, "
                    "COPERNICUS_CLIENT_ID and COPERNICUS_CLIENT_SECRET to enable Sentinel access."
                ),
            )
        return ProviderResult(
            provider_key=self.provider_key,
            provider_name=self.provider_name,
            mode=ProviderMode.ERROR,
            message="Copernicus OAuth/Process API integration is not implemented yet.",
            error="not_implemented",
        )


def get_satellite_provider() -> ProviderBase:
    if settings.satellite_provider == "gee":
        return GoogleEarthEngineProvider()
    if settings.satellite_provider == "copernicus":
        return CopernicusProvider()
    return DemoSatelliteProvider()
