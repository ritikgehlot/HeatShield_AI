# HeatShield AI — Live Urban Heat Intelligence Platform

**Team ARS** · Primary demo city: **mandore,Jodhpur, Rajasthan,342004**

Ward-by-ward urban heat risk, explained transparently, with costed cooling
interventions municipal teams can act on. Runs in **demo mode with zero API
keys**. Every value shows its source, timestamp, freshness, and confidence —
and demo/cached data is never presented as live.

![status](https://img.shields.io/badge/backend_tests-19_passing-brightgreen) ![demo](https://img.shields.io/badge/demo_mode-zero_keys-blue)

---

## Quick start (demo mode, zero keys)

### Windows (PowerShell + VS Code)
```powershell
cd heatshield-ai
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
pytest -q                          # optional: 19 tests should pass
uvicorn backend.main:app --reload
```
Then open **http://127.0.0.1:8000** — the backend serves the pre-built React app.

> If PowerShell blocks the activate script, run once:
> `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`

### macOS / Linux
```bash
cd heatshield-ai
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pytest -q
uvicorn backend.main:app --reload
```

That's the whole demo. No keys, no external services required.

---

## Frontend development (hot reload)

The repo ships a **pre-built** frontend so the backend works out of the box. To
work on the UI with live reload:

```bash
cd frontend
npm install
npm run dev            # http://localhost:5173, proxies /api to :8000
```
Keep the backend (`uvicorn`) running in another terminal. To rebuild the bundle
the backend serves: `npm run build` (outputs to `frontend/dist`).

---

## Configuring live data (optional)

Copy `.env.example` to `.env` and fill in only what you need. **Never commit `.env`.**

```bash
cp .env.example .env
```

| Capability | Variables | Notes |
|---|---|---|
| Live weather (keyless) | `WEATHER_PROVIDER=open-meteo` | Default. No key needed. |
| Live weather (OpenWeatherMap) | `WEATHER_PROVIDER=openweathermap`, `WEATHER_API_KEY` | |
| Satellite (Google Earth Engine) | `SATELLITE_PROVIDER=gee`, `GEE_PROJECT_ID`, `GEE_SERVICE_ACCOUNT_EMAIL`, `GEE_CREDENTIALS_PATH` | Also `pip install earthengine-api` |
| Satellite (Copernicus) | `SATELLITE_PROVIDER=copernicus`, `COPERNICUS_CLIENT_ID`, `COPERNICUS_CLIENT_SECRET` | Alternative to GEE |
| Map tiles | `MAP_PROVIDER_KEY` (+ `VITE_MAP_PROVIDER_KEY` for the build) | Optional; keyless dark basemap used otherwise |
| Redis cache | `CACHE_URL` | Optional; in-process cache used otherwise |

See **[docs/DATA_SOURCES.md](docs/DATA_SOURCES.md)** for details on each provider
and the demo/live/not-configured behavior.

---

## PostgreSQL + PostGIS (production)

SQLite is the zero-setup default. For production:

```bash
# set in .env
DATABASE_URL=postgresql+psycopg://heatshield:heatshield@localhost:5432/heatshield
# then create the schema via migrations
alembic upgrade head
uvicorn backend.main:app
```

---

## Docker

Brings up PostGIS + the app (frontend built into the image). Requires Docker Desktop.

```bash
docker compose up --build
# optional Redis cache:
docker compose --profile with-cache up --build
```
The app runs migrations then starts at **http://localhost:8000**.

> Note: the Docker files are written and reviewed but were not run inside the
> build environment (no Docker daemon there). Validate `docker compose up` on
> your machine.

---

## Uploading ward data

- **CSV** (V1 or V2 format, auto-detected) and **GeoJSON boundaries** via the
  in-app **Data Sources** page, or the API.
- Download a template from that page, or use the samples:
  `data/sample_jodhpur_wards_v2.csv`, `data/sample_jodhpur_boundaries.geojson`.
- Column reference: **[data/templates/README.md](data/templates/README.md)**.
- CLI import: `python scripts/import_csv.py data/sample_jodhpur_wards_v2.csv`

---

## Testing & build

```bash
pytest -q                          # backend: 19 tests
cd frontend && npm run build       # frontend: type-check + production build
```

---

## API

Interactive docs at **http://127.0.0.1:8000/docs** when running. Key endpoints:

```
GET  /api/health
GET  /api/cities
GET  /api/cities/{city_id}/dashboard
GET  /api/wards/{ward_id}
GET  /api/wards/{ward_id}/timeseries
GET  /api/wards/{ward_id}/risk-explanation
POST /api/refresh/weather   POST /api/refresh/satellite
POST /api/upload/ward-features-csv
POST /api/upload/ward-boundaries-geojson
POST /api/simulations       GET /api/simulations/{id}
GET  /api/data-sources/status
GET  /api/reports/ward/{ward_id}
GET  /api/data/template?version=v2
```
Legacy V1 endpoints (`/api/wards`, `/api/summary`, `/api/simulate`,
`/api/data/upload`) remain available for backward compatibility.

---

## Documentation

- [docs/ARCHITECTURE_V2.md](docs/ARCHITECTURE_V2.md) — system design & tradeoffs
- [docs/MODEL_CARD.md](docs/MODEL_CARD.md) — scoring model, assumptions, ethics
- [docs/DATA_SOURCES.md](docs/DATA_SOURCES.md) — providers & modes
- [docs/DEMO_SCRIPT_V2.md](docs/DEMO_SCRIPT_V2.md) — judge walkthrough + QA checklist
- [docs/IMPLEMENTATION_PLAN_V2.md](docs/IMPLEMENTATION_PLAN_V2.md) — the build plan
- [docs/SESSION_HANDOFF.md](docs/SESSION_HANDOFF.md) — current status

---

## Push to GitHub

```bash
git remote add origin https://github.com/<you>/heatshield-ai.git
git push -u origin main
git push origin feature/live-platform-v2
```
`.gitignore` already excludes `.env`, `*.db`, `node_modules`, and credential files.

---

## Honesty notes

- Demo/seeded values (weather, satellite scene, ward features, boundaries) are
  **labelled demo** and are not real observations. Seeded ward boundaries are
  simplified placeholders, not official municipal boundaries.
- Live external API calls are implemented against documented API shapes but were
  developed where outbound network was restricted — verify live paths locally.
- This is **decision support**, not automated policy. See the Model Card.
