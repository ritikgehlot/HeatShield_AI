"""Urban features provider: OpenStreetMap-derived road/building/green
indicators, supplementing (not replacing) CSV/GeoJSON ward imports.

Uses the public Overpass API (overpass-api.de), which is keyless like
Open-Meteo — so this can be "live" with zero credentials too. Same honest
caveat as the other network-calling adapters: written and structured
correctly against Overpass QL's documented shape, but this sandbox's network
allowlist doesn't include overpass-api.de, so it has not been executed
end-to-end here. Verify on your own machine.
"""
from __future__ import annotations

from datetime import datetime, timezone

from .provider_base import ProviderBase, ProviderMode, ProviderResult, TTLCache

_cache = TTLCache(ttl_seconds=3600)


class DemoUrbanFeaturesProvider(ProviderBase):
    provider_key = "urban_features"
    provider_name = "Demo urban features (seeded/CSV)"

    def status(self) -> ProviderResult:
        return ProviderResult(
            provider_key=self.provider_key,
            provider_name=self.provider_name,
            mode=ProviderMode.DEMO,
            message="Ward built-up/road/green indicators come from seeded demo data or your CSV import.",
        )


class OSMUrbanFeaturesProvider(ProviderBase):
    provider_key = "urban_features"
    provider_name = "OpenStreetMap Overpass (live, no key required)"
    OVERPASS_URL = "https://overpass-api.de/api/interpreter"

    def fetch_for_bbox(self, south: float, west: float, north: float, east: float) -> ProviderResult:
        cache_key = f"osm:{south:.3f}:{west:.3f}:{north:.3f}:{east:.3f}"
        cached = _cache.get(cache_key)
        query = f"""
        [out:json][timeout:25];
        (
          way["highway"]({south},{west},{north},{east});
          way["building"]({south},{west},{north},{east});
          way["leisure"="park"]({south},{west},{north},{east});
          way["landuse"="grass"]({south},{west},{north},{east});
        );
        out count;
        """
        try:
            import httpx

            with httpx.Client(timeout=25.0) as client:
                response = client.post(self.OVERPASS_URL, data={"data": query})
                response.raise_for_status()
                payload = response.json()

            counts = {}
            for element in payload.get("elements", []):
                tags = element.get("tags", {})
                if "total" in tags:
                    counts = tags
                    break

            data = {"raw_element_counts": counts}
            result = ProviderResult(
                provider_key=self.provider_key,
                provider_name=self.provider_name,
                mode=ProviderMode.LIVE,
                data=data,
                source="OpenStreetMap via Overpass API",
                observed_at=datetime.now(timezone.utc),
                message=(
                    "Live OSM feature counts fetched. Converting raw counts into "
                    "road-density/built-up-share numbers needs an area-weighted "
                    "aggregation step — do this before trusting these as ward metrics."
                ),
            )
            _cache.set(cache_key, result)
            return result
        except Exception as exc:
            if cached is not None:
                return ProviderResult(
                    provider_key=self.provider_key,
                    provider_name=self.provider_name,
                    mode=ProviderMode.CACHED_FALLBACK,
                    data=cached.data,
                    source=cached.source,
                    message="Live OSM fetch failed — showing last cached result.",
                    error=str(exc),
                )
            return ProviderResult(
                provider_key=self.provider_key,
                provider_name=self.provider_name,
                mode=ProviderMode.ERROR,
                message="Live OSM fetch failed and no cached result is available.",
                error=str(exc),
            )

    def status(self) -> ProviderResult:
        return ProviderResult(
            provider_key=self.provider_key,
            provider_name=self.provider_name,
            mode=ProviderMode.LIVE,
            message="Configured — no API key required.",
        )


def get_urban_features_provider(live: bool = False) -> ProviderBase:
    return OSMUrbanFeaturesProvider() if live else DemoUrbanFeaturesProvider()
