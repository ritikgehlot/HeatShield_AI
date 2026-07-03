"""Geocoding provider: resolves city/ward names to coordinates.

Demo mode uses a small static registry (good enough for the seeded cities this
project ships with). Live mode uses OpenStreetMap Nominatim, which is keyless
but requires a descriptive User-Agent per its usage policy — set here, not
left to a default. Same sandbox caveat as the other adapters: nominatim's
domain is outside this environment's network allowlist, so this is written
correctly against Nominatim's documented API but not executed here.
"""
from __future__ import annotations

from datetime import datetime, timezone

from .provider_base import ProviderBase, ProviderMode, ProviderResult

DEMO_REGISTRY = {
    "jodhpur": {"latitude": 26.2389, "longitude": 73.0243, "display_name": "Jodhpur, Rajasthan, India"},
}


class DemoGeocodingProvider(ProviderBase):
    provider_key = "geocoding"
    provider_name = "Demo geocoding (static registry)"

    def resolve(self, place_name: str) -> ProviderResult:
        hit = DEMO_REGISTRY.get(place_name.strip().lower())
        if not hit:
            return ProviderResult(
                provider_key=self.provider_key,
                provider_name=self.provider_name,
                mode=ProviderMode.DEMO,
                message=f"'{place_name}' is not in the small demo registry — try live geocoding or add it manually.",
            )
        return ProviderResult(
            provider_key=self.provider_key,
            provider_name=self.provider_name,
            mode=ProviderMode.DEMO,
            data=hit,
            source="Static demo registry",
            observed_at=datetime.now(timezone.utc),
            message="Demo mode: resolved from a small built-in list, not a live geocoder.",
        )

    def status(self) -> ProviderResult:
        return ProviderResult(
            provider_key=self.provider_key,
            provider_name=self.provider_name,
            mode=ProviderMode.DEMO,
            message="Static registry covers seeded cities only.",
        )


class NominatimGeocodingProvider(ProviderBase):
    provider_key = "geocoding"
    provider_name = "OpenStreetMap Nominatim (live, no key required)"
    BASE_URL = "https://nominatim.openstreetmap.org/search"

    def resolve(self, place_name: str) -> ProviderResult:
        try:
            import httpx

            headers = {"User-Agent": "HeatShieldAI/2.0 (hackathon urban-heat dashboard)"}
            params = {"q": place_name, "format": "json", "limit": 1}
            with httpx.Client(timeout=6.0, headers=headers) as client:
                response = client.get(self.BASE_URL, params=params)
                response.raise_for_status()
                results = response.json()

            if not results:
                return ProviderResult(
                    provider_key=self.provider_key,
                    provider_name=self.provider_name,
                    mode=ProviderMode.LIVE,
                    message=f"No live geocoding match found for '{place_name}'.",
                )
            top = results[0]
            data = {
                "latitude": float(top["lat"]),
                "longitude": float(top["lon"]),
                "display_name": top.get("display_name", place_name),
            }
            return ProviderResult(
                provider_key=self.provider_key,
                provider_name=self.provider_name,
                mode=ProviderMode.LIVE,
                data=data,
                source="OpenStreetMap Nominatim",
                observed_at=datetime.now(timezone.utc),
                message="Live geocoding match from Nominatim.",
            )
        except Exception as exc:
            return ProviderResult(
                provider_key=self.provider_key,
                provider_name=self.provider_name,
                mode=ProviderMode.ERROR,
                message="Live geocoding failed.",
                error=str(exc),
            )

    def status(self) -> ProviderResult:
        return ProviderResult(
            provider_key=self.provider_key,
            provider_name=self.provider_name,
            mode=ProviderMode.LIVE,
            message="Configured — no API key required. Please respect Nominatim's usage policy for heavy use.",
        )


def get_geocoding_provider(live: bool = False) -> ProviderBase:
    return NominatimGeocodingProvider() if live else DemoGeocodingProvider()
