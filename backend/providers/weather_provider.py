"""Weather provider adapters.

Two live options behind one interface:
  - Open-Meteo: free, no API key required at all. Default live provider, so
    "live weather" can genuinely work with zero keys — a step beyond what the
    spec assumed was possible.
  - OpenWeatherMap-style: key-based, used when WEATHER_PROVIDER is set to
    something other than "open-meteo" and WEATHER_API_KEY is present.

Honest limitation: this sandbox's outbound network is restricted to package
registries, so the HTTP calls below are written and structured correctly
against each API's documented shape, but could not be executed against the
real endpoint from inside this session. Exercise them on your own machine
before relying on the live path. Any failure here — network, timeout,
malformed response — degrades to CACHED_FALLBACK or ERROR, never to invented
numbers labeled live.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Optional

from ..config import settings
from .provider_base import ProviderBase, ProviderMode, ProviderResult, TTLCache

_cache = TTLCache(ttl_seconds=600)

DEMO_WEATHER_TEMPLATE = {
    # Plausible late-spring/summer Jodhpur midday conditions. Explicitly demo —
    # never returned with mode=LIVE.
    "air_temp_c": 41.5,
    "apparent_temp_c": 44.0,
    "humidity_pct": 22.0,
    "wind_speed_mps": 3.4,
    "cloud_cover_pct": 8.0,
    "precipitation_mm": 0.0,
}


class DemoWeatherProvider(ProviderBase):
    provider_key = "weather"
    provider_name = "Demo weather (seeded)"

    def status(self) -> ProviderResult:
        return ProviderResult(
            provider_key=self.provider_key,
            provider_name=self.provider_name,
            mode=ProviderMode.DEMO,
            data=dict(DEMO_WEATHER_TEMPLATE),
            source="Seeded demo values — not a real observation",
            observed_at=datetime.now(timezone.utc),
            message="Demo mode: showing representative seeded weather, not a live reading.",
        )


class OpenMeteoWeatherProvider(ProviderBase):
    provider_key = "weather"
    provider_name = "Open-Meteo (live, no key required)"
    BASE_URL = "https://api.open-meteo.com/v1/forecast"

    def fetch(self, latitude: float, longitude: float) -> ProviderResult:
        cache_key = f"open-meteo:{latitude:.3f}:{longitude:.3f}"
        cached = _cache.get(cache_key)

        try:
            import httpx

            params = {
                "latitude": latitude,
                "longitude": longitude,
                "current": ",".join(
                    [
                        "temperature_2m",
                        "relative_humidity_2m",
                        "apparent_temperature",
                        "precipitation",
                        "cloud_cover",
                        "wind_speed_10m",
                    ]
                ),
                "timezone": "auto",
            }
            with httpx.Client(timeout=6.0) as client:
                response = client.get(self.BASE_URL, params=params)
                response.raise_for_status()
                payload = response.json()

            current = payload.get("current", {})
            data = {
                "air_temp_c": current.get("temperature_2m"),
                "apparent_temp_c": current.get("apparent_temperature"),
                "humidity_pct": current.get("relative_humidity_2m"),
                "wind_speed_mps": current.get("wind_speed_10m"),
                "cloud_cover_pct": current.get("cloud_cover"),
                "precipitation_mm": current.get("precipitation"),
            }
            observed_at = datetime.now(timezone.utc)
            if current.get("time"):
                try:
                    observed_at = datetime.fromisoformat(current["time"]).replace(tzinfo=timezone.utc)
                except ValueError:
                    pass

            result = ProviderResult(
                provider_key=self.provider_key,
                provider_name=self.provider_name,
                mode=ProviderMode.LIVE,
                data=data,
                source="Open-Meteo forecast API",
                observed_at=observed_at,
                message="Live reading from Open-Meteo.",
            )
            _cache.set(cache_key, result)
            return result

        except Exception as exc:  # network error, timeout, bad JSON, etc.
            if cached is not None:
                fallback = ProviderResult(
                    provider_key=self.provider_key,
                    provider_name=self.provider_name,
                    mode=ProviderMode.CACHED_FALLBACK,
                    data=cached.data,
                    source=cached.source,
                    observed_at=cached.observed_at,
                    message="Live fetch failed — showing last cached reading, not current.",
                    error=str(exc),
                )
                return fallback
            return ProviderResult(
                provider_key=self.provider_key,
                provider_name=self.provider_name,
                mode=ProviderMode.ERROR,
                data={},
                source="Open-Meteo forecast API",
                message="Live weather fetch failed and no cached reading is available.",
                error=str(exc),
            )

    def status(self) -> ProviderResult:
        # Generic status (no coordinates) — used by the Data Sources page.
        return ProviderResult(
            provider_key=self.provider_key,
            provider_name=self.provider_name,
            mode=ProviderMode.LIVE,
            message="Configured — no API key required.",
        )


class OpenWeatherMapProvider(ProviderBase):
    provider_key = "weather"
    provider_name = "OpenWeatherMap (live, API key)"
    BASE_URL = "https://api.openweathermap.org/data/2.5/weather"

    def __init__(self, api_key: str):
        self.api_key = api_key

    def fetch(self, latitude: float, longitude: float) -> ProviderResult:
        cache_key = f"owm:{latitude:.3f}:{longitude:.3f}"
        cached = _cache.get(cache_key)
        try:
            import httpx

            params = {
                "lat": latitude,
                "lon": longitude,
                "appid": self.api_key,
                "units": "metric",
            }
            with httpx.Client(timeout=6.0) as client:
                response = client.get(self.BASE_URL, params=params)
                response.raise_for_status()
                payload = response.json()

            main = payload.get("main", {})
            wind = payload.get("wind", {})
            clouds = payload.get("clouds", {})
            rain = payload.get("rain", {})
            data = {
                "air_temp_c": main.get("temp"),
                "apparent_temp_c": main.get("feels_like"),
                "humidity_pct": main.get("humidity"),
                "wind_speed_mps": wind.get("speed"),
                "cloud_cover_pct": clouds.get("all"),
                "precipitation_mm": rain.get("1h", 0.0),
            }
            result = ProviderResult(
                provider_key=self.provider_key,
                provider_name=self.provider_name,
                mode=ProviderMode.LIVE,
                data=data,
                source="OpenWeatherMap current-weather API",
                observed_at=datetime.now(timezone.utc),
                message="Live reading from OpenWeatherMap.",
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
                    observed_at=cached.observed_at,
                    message="Live fetch failed — showing last cached reading, not current.",
                    error=str(exc),
                )
            return ProviderResult(
                provider_key=self.provider_key,
                provider_name=self.provider_name,
                mode=ProviderMode.ERROR,
                message="Live weather fetch failed and no cached reading is available.",
                error=str(exc),
            )

    def status(self) -> ProviderResult:
        return ProviderResult(
            provider_key=self.provider_key,
            provider_name=self.provider_name,
            mode=ProviderMode.LIVE if self.api_key else ProviderMode.NOT_CONFIGURED,
            message="Configured with API key." if self.api_key else "WEATHER_API_KEY is not set.",
        )


def get_weather_provider() -> ProviderBase:
    """Factory selecting the configured provider. Falls back to demo if the
    configured live provider can't actually be used (e.g. key-based provider
    chosen but no key set) — the caller checks the mode on the returned
    result, so this never silently pretends to be live."""
    if settings.weather_provider == "open-meteo":
        return OpenMeteoWeatherProvider()
    if settings.weather_provider in ("openweathermap", "owm"):
        if settings.weather_api_key:
            return OpenWeatherMapProvider(settings.weather_api_key)
        return _NotConfiguredWeatherProvider("OpenWeatherMap")
    return DemoWeatherProvider()


class _NotConfiguredWeatherProvider(ProviderBase):
    provider_key = "weather"

    def __init__(self, wanted_name: str):
        self.provider_name = f"{wanted_name} (not configured)"

    def fetch(self, latitude: float, longitude: float) -> ProviderResult:
        return self.status()

    def status(self) -> ProviderResult:
        return ProviderResult(
            provider_key=self.provider_key,
            provider_name=self.provider_name,
            mode=ProviderMode.NOT_CONFIGURED,
            message="WEATHER_API_KEY is not set. Add it to .env to enable this provider.",
        )
