# HeatShield AI — Implementation Plan V2

Status: written after a real audit of the uploaded repo (extracted, dependencies
installed, tests executed, server started, endpoints curled, CLI script run).
Nothing in this document describes work that hasn't happened yet as if it had.

## 1. Current architecture summary (verified)

```
heatshield-ai/
├── backend/
│   ├── main.py         FastAPI app, 8 routes, mounts static/ at "/"
│   ├── db.py            SQLite by default (DATABASE_URL env), SQLAlchemy 2 engine
│   ├── models.py         2 tables: Ward, ScenarioRun
│   ├── schemas.py        Pydantic v2 response/request models
│   ├── risk_engine.py     RandomForestRegressor trained at import time on
│   │                      synthetic data generated from a hand-written formula
│   ├── seed.py            12 hard-coded Jodhpur wards, seeded on startup
│   ├── services.py        CSV import + serialization helpers
│   ├── static/            Hand-written HTML/CSS/JS dashboard (not React)
│   └── tests/test_api.py  2 tests, both pass
├── data/                  V1 CSV contract + 1 sample row
├── scripts/import_csv.py  CLI importer (buggy path, see below)
├── docs/                  ARCHITECTURE.md, DEMO_SCRIPT.md (V1)
├── Dockerfile, docker-compose.yml   app + postgres, no frontend container
└── requirements.txt
```

**Verified working:** `pip install`, `pytest` (2/2 pass), `uvicorn` boot, `/api/health`,
`/api/summary`, `/api/wards`, static `/`, `/api/data/template` all return HTTP 200.
Demo mode requires zero API keys today because there is no external-provider code
at all yet — everything is seeded or CSV-derived.

**Verified broken:** `python scripts/import_csv.py <file>`, exactly as documented in
README.md, raises `ModuleNotFoundError: No module named 'backend'` because the
script never adds the project root to `sys.path` and isn't invoked as a module. It
only works with `PYTHONPATH=.` set manually. Fixing this is P0.

**Verified but concerning:** the risk model is a `RandomForestRegressor` fit at
every process startup to 3,500 synthetic rows generated from a linear formula
(`risk_engine.py::_synthetic_training_data`). It isn't learning from real
observations — it's a black-box wrapper around a formula, and it's miscalibrated:
11/12 seeded wards land at "High" risk or above out of a possible Low/Medium/High
range (the current build only has 3 levels, not the 5 the new spec wants), with one
ward at 99.9/100. This directly conflicts with Phase 5's "do not train fake ML on
tiny/demo data" instruction and needs to be replaced with a transparent formula.

## 2. Existing files to retain (as logic, even where the file itself changes)

- `backend/risk_engine.py` — the *rule-based* pieces (`derive_top_drivers`,
  `recommendations`) are sound and reusable; the RF wrapper is replaced.
- `backend/seed.py` — the 12 ward lat/longs and feature values are decent demo
  material; extended with more wards and richer fields, not thrown away.
- `backend/services.py` CSV parsing/validation logic — extended for the V2 column
  set, kept for V1 backward compatibility as instructed.
- `data/sample_city_features.csv` + `data/README.md` — kept as the V1 contract
  reference, alongside new V2 templates.
- Color tokens from `backend/static/styles.css` (`#f97316` orange, `#fbbf24` amber,
  `#ef4444` red, `#22a85a` green, `#0b1729`/`#122137` navy) — carried into the new
  Tailwind theme so the visual identity evolves instead of being replaced outright.
- `docker-compose.yml` app+db shape — extended with a frontend service and optional
  Redis, not rewritten from scratch.
- Test patterns in `backend/tests/test_api.py` — extended, not discarded.

## 3. Files to upgrade

- `backend/main.py` → split into `backend/routers/*.py` for the full endpoint list
  in Phase 8; old endpoints kept as working aliases.
- `backend/models.py` → grows from 2 tables to the 12-table schema in §4.
- `backend/risk_engine.py` → RF-on-synthetic-formula replaced with an explainable
  weighted hybrid formula (see `docs/MODEL_CARD.md`).
- `scripts/import_csv.py` → fix the `sys.path` bug; support both V1 and V2 CSV
  columns.
- `README.md`, `docs/ARCHITECTURE.md`, `docs/DEMO_SCRIPT.md` → superseded by V2
  versions once the new architecture is real, not before.
- `docker-compose.yml`, `Dockerfile`, `.env.example` → extended for the frontend
  container, Redis (optional), and the new provider env vars.

## 4. Database migration plan

SQLite demo mode keeps using `Base.metadata.create_all` for zero-friction local
boot (no Alembic version drift to manage for a throwaway demo DB). PostgreSQL mode
gets a real Alembic baseline migration. New tables:

`cities, wards, ward_geometries, weather_observations, satellite_scenes,
ward_feature_snapshots, heat_risk_scores, intervention_catalog,
intervention_simulations, ingestion_runs, data_source_status, audit_logs`

Key design choice: `wards` stops being the single mutable row it is today.
Feature values move to `ward_feature_snapshots` (one row per CSV import / OSM
refresh / manual edit), and `heat_risk_scores` stores one row per computed score.
"Current" ward state = latest snapshot + latest score. This is what makes
freshness/history/timeseries endpoints possible without bolting on more mutable
columns — it's a bigger change than the original 2-table design, so it's called
out explicitly rather than done silently.

Ward geometry is stored as GeoJSON text in `ward_geometries.geometry_geojson` on
both SQLite and Postgres (works everywhere, no `geoalchemy2` hard dependency).
Documented as an upgrade path to native `geometry()` columns + spatial indexes for
real production scale, rather than implemented now — see Risks.

## 5. API integration plan

Implements the endpoint list from Phase 8. Existing `/api/wards`, `/api/wards/{id}`,
`/api/summary`, `/api/simulate`, `/api/data/upload`, `/api/data/template` stay live
as aliases so nothing that already works gets silently broken.

## 6. UI/UX redesign plan

Current frontend is static HTML/CSS/JS with a CSS-only fake map (honestly labeled
"Prototype geometry" in its own footnote). Replaced with React + TypeScript + Vite
+ Tailwind + MapLibre GL + TanStack Query + Recharts + Lucide, per Phase 2, since
the current implementation predates and doesn't match the specified stack. Visual
direction: dark navy base carried forward from the existing sidebar color
(`#0b1729`), extended to the whole app (today only the sidebar is dark, the main
canvas is light), amber/orange heat scale, green vegetation/mitigation scale —
detailed token system in the frontend work itself, not duplicated here.

Note on `shadcn/ui`: the shadcn CLI fetches component source from a registry
domain my sandboxed build environment can't reach. Functionally-equivalent
accessible components are hand-built on Radix primitives (installed from npm,
which is reachable) styled to the same token system, rather than skipped.

## 7. Data-source strategy

- **Demo:** works today, zero keys, clearly badged.
- **Weather (live):** defaults to Open-Meteo, which needs no API key at all, so
  live weather can work out of the box; OpenWeatherMap supported as a
  key-based alternative via `WEATHER_PROVIDER`. Important limitation: my sandbox's
  outbound network is restricted to package registries, so I can write and unit
  test this adapter with mocked HTTP responses, but I cannot make a real network
  call to a weather API from inside this session to prove it end-to-end — that
  needs to be verified on your machine, and I'll say so again in the final summary
  rather than implying it was.
- **Satellite (live):** Google Earth Engine adapter built against the documented
  env vars, but I have no credentials to test against. Without them it must report
  "Satellite connection not configured" — never fabricated scene data.
- **City features:** GeoJSON ward boundary upload + V2 CSV import; OpenStreetMap
  road/building/green indicators are scoped as a documented stub (real Overpass
  API calls need outbound access this sandbox doesn't have to verify), not faked.

## 8. Testing plan

Expand `backend/tests/test_api.py` into a suite covering health, cities, dashboard,
ward detail, risk-explanation, data-source status, CSV upload (valid + invalid),
and simulation create/read. Run for real before calling anything done. Frontend:
`npm run build` must succeed as the compile-correctness bar; no headless-browser
screenshot tool is available in this environment, so visual QA is described in
`docs/DEMO_SCRIPT_V2.md` for you to run locally rather than claimed as done here.

## 9. Deployment plan

Docker Compose: `db` (postgres+postgis), `app` (backend), `frontend` (built static
served or dev container), optional `redis`. I can write and validate these files
for correctness, but this sandbox has no Docker daemon, so `docker compose up`
itself is untested here — flagged clearly in the final summary, not glossed over.

## 10. Risks and assumptions

- No GeoJSON ward boundaries exist for Jodhpur in this repo or my training data
  with verified accuracy, so V2 seed geometries are deliberately simplified
  polygons around each ward's existing lat/long, clearly not official municipal
  boundaries. Real boundaries should replace them before any real decision-making.
- PostGIS-native geometry columns are deferred (see §4) in favor of portable
  GeoJSON text, to keep SQLite and Postgres behaving identically without a hard
  `geoalchemy2` dependency.
- Live weather/satellite code paths are written and unit-tested with mocks, not
  proven against real external endpoints, because this sandbox can't reach them.
- Given the size of this spec (full 12-table schema, 4 provider adapters, explainable
  risk engine, intervention optimizer, 6-page premium UI, 15 endpoints, Docker infra,
  5 docs — realistically multi-day work for a team), this session prioritizes a
  genuinely complete and tested demo-mode path over shallow coverage of every bullet.
  Anything not finished is itemized honestly in `docs/RESUME_PROGRESS.md`, not implied
  to be done.
