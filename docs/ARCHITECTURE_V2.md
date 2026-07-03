# Architecture V2

## Overview

```
┌─────────────────────────────────────────────────────────────┐
│  Frontend — React + TypeScript + Vite                        │
│  MapLibre GL · TanStack Query · Recharts · Radix · Tailwind  │
└───────────────────────────┬─────────────────────────────────┘
                            │  typed REST (/api/*)
┌───────────────────────────▼─────────────────────────────────┐
│  Backend — FastAPI + Pydantic v2                             │
│  routers/  → services.py (business logic) → risk_engine.py   │
│                                          └→ interventions.py  │
│  providers/ (weather · satellite · urban_features · geocoding)│
└───────────────────────────┬─────────────────────────────────┘
                            │  SQLAlchemy 2
┌───────────────────────────▼─────────────────────────────────┐
│  SQLite (demo, default)  |  PostgreSQL + PostGIS (production) │
│  13 tables · Alembic migrations for Postgres                 │
└─────────────────────────────────────────────────────────────┘
```

## Key design decisions and tradeoffs

### Snapshot-based ward state
`Ward` holds only stable identity/location. Feature values live in
`ward_feature_snapshots` (one row per import/refresh) and scores in
`heat_risk_scores` (one row per computation). "Current" state = latest snapshot
+ latest score. **Why:** this is what makes freshness badges, history, and
timeseries endpoints possible without piling mutable columns onto `Ward`. **Cost:**
"latest per ward" is a per-ward query at this scale; at real city scale it should
become a window-function query (flagged in `services.py`).

### Geometry as GeoJSON text, not native PostGIS columns
Ward polygons are stored as GeoJSON text on both SQLite and Postgres. **Why:**
identical behavior on both backends, no hard `geoalchemy2` dependency, trivial
to serve straight to MapLibre. **Cost:** no server-side spatial queries
(within/intersects). **Upgrade path:** migrate `ward_geometries.geometry_geojson`
to a PostGIS `geometry(MultiPolygon, 4326)` column with a GiST index when
spatial querying is needed; the PostGIS image is already in docker-compose.

### Transparent formula over trained ML
See `MODEL_CARD.md`. The additive formula gives exact per-feature attribution
for free, which is both more honest and more useful than a black box on this
data volume.

### Provider adapter pattern
Every provider returns a `ProviderResult` with an explicit mode. The API and
frontend render identical provenance UI regardless of provider. It is
structurally impossible for a provider to return a value without a mode, which
is what enforces "never show fake live data."

### Caching
In-process TTL cache (per provider). **Upgrade path:** `CACHE_URL` +
Redis for multi-worker deployments (Redis service already in docker-compose
behind the `with-cache` profile).

### Legacy compatibility
The original V1 endpoints (`/api/wards`, `/api/summary`, `/api/simulate`,
`/api/data/upload`) are preserved in `routers/legacy.py`, backed by the new
schema, so the original static dashboard and any existing integrations keep
working. New `/api/wards/{id}` uses the richer V2 shape (confirmed no path
collision — the old static frontend never called that path).

## What is verified vs. what needs your environment

- **Verified here:** backend boots, 19/19 tests pass, all endpoints return real
  responses, CSV/GeoJSON round-trip, frontend type-checks and builds, backend
  serves the built SPA, Alembic baseline applies and creates all 13 tables.
- **Not verifiable in the build sandbox:** real live external API fetches
  (network restricted), `docker compose up` (no Docker daemon), and on-screen
  visual QA (no headless browser reachable). Run these locally.
