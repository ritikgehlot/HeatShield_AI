# Data Sources

Every important value in HeatShield AI carries a provenance badge: source,
mode (demo / live / cached / not-configured / error), observation timestamp,
and where applicable confidence. This document describes each provider.

## The five modes

- **demo** — seeded or sample data, clearly labelled. Works with zero keys.
- **live** — a real, current fetch from an external provider succeeded.
- **cached_fallback** — a previous live value, shown because the latest live
  fetch failed. Labelled as potentially stale.
- **not_configured** — a live provider was selected but credentials are missing.
  Shows a clear message, never fabricated values.
- **error** — a live fetch failed and nothing is cached.

## Weather (`backend/providers/weather_provider.py`)

| Provider | Key required? | Notes |
|---|---|---|
| Open-Meteo (default) | **No** | Keyless live weather. `WEATHER_PROVIDER=open-meteo` |
| OpenWeatherMap | Yes | `WEATHER_PROVIDER=openweathermap`, `WEATHER_API_KEY=...` |

Fetches air temp, apparent temp, humidity, wind, cloud cover, precipitation.
Responses are cached (10 min TTL) so repeated dashboard loads don't re-hit the API.

## Satellite (`backend/providers/satellite_provider.py`)

| Provider | Config | Notes |
|---|---|---|
| Demo | (default) | Labelled synthetic scene. `SATELLITE_PROVIDER=none` |
| Google Earth Engine | `SATELLITE_PROVIDER=gee` + `GEE_PROJECT_ID`, `GEE_SERVICE_ACCOUNT_EMAIL`, `GEE_CREDENTIALS_PATH` | Landsat/Sentinel LST, NDVI, NDBI |
| Copernicus/Sentinel | `SATELLITE_PROVIDER=copernicus` + `COPERNICUS_CLIENT_ID`, `COPERNICUS_CLIENT_SECRET` | Optional alternative |

**Satellite data is never "live" second-by-second.** The UI always says
"latest available scene" with the true observation date, cloud cover, scene ID,
and processing status. Without credentials it shows "Satellite connection not
configured", never invented values.

## Urban features (`backend/providers/urban_features_provider.py`)

OpenStreetMap via the Overpass API (keyless). Supplements CSV/GeoJSON imports
with road/building/green indicators. Raw element counts still need an
area-weighted aggregation step before they become trustworthy ward metrics —
this is flagged in the provider's own response message.

## Geocoding (`backend/providers/geocoding_provider.py`)

Demo: a small static registry (seeded cities). Live: OpenStreetMap Nominatim
(keyless, with a required descriptive User-Agent per their usage policy).

## City feature imports

- **CSV** (V1 or V2 contract, auto-detected) via the Data Sources page or
  `POST /api/upload/ward-features-csv`. See `data/templates/README.md`.
- **GeoJSON** ward boundaries via `POST /api/upload/ward-boundaries-geojson`.
  Matched to wards by name; unmatched features are reported, not silently dropped.

## Honest testing caveat

The live weather/satellite/OSM/geocoding HTTP calls are written against each
API's documented shape, but were developed in a sandbox whose outbound network
reaches only package registries. They are verified via their graceful-failure
paths (timeouts, cached fallback, not-configured), **not** via a real successful
live fetch. Verify the live paths on your own machine once you add credentials.
