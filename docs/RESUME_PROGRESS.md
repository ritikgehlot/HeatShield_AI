# Resume Progress — HeatShield AI V2

This file is a status snapshot, updated honestly at each checkpoint. This is the
**first** version, written immediately after the initial repo audit and before any
V2 implementation work. It will be rewritten at the end of this session with the
real final status — not left describing stale plans as current facts.

## 1. What is already completed

Nothing from the V2 spec yet. This is a fresh start on top of the original
basic/demo project (there is no git history in the uploaded zip, and this session
had done nothing but review two internal reference docs before this audit began).

What *was* already completed, by the original prototype (verified working today):
- FastAPI backend, SQLite by default, 2 tables (Ward, ScenarioRun)
- Seeded 12-ward Jodhpur demo dataset
- 8 working API endpoints (health, wards list/detail, summary, simulate, CSV
  upload/template, recent scenarios)
- A static HTML/CSS/JS dashboard with sliders-based what-if simulator
- 2 passing pytest tests
- Dockerfile + docker-compose.yml for backend + Postgres

## 2. What is partially completed

- CSV import: the parsing/validation logic works, but the documented CLI command
  (`python scripts/import_csv.py ...`) currently fails — see §3.
- Risk explainability: `derive_top_drivers` exists and is reasonable, but the
  underlying score comes from a black-box RF wrapper around a formula rather
  than a documented, transparent formula.

## 3. What is broken or unfinished

- `python scripts/import_csv.py data/sample_city_features.csv`, run exactly as
  README.md instructs, fails with `ModuleNotFoundError: No module named 'backend'`.
  Works only with `PYTHONPATH=.` set manually first.
- Risk scores are miscalibrated: 11 of 12 seeded wards land "High" or above on a
  0–100 scale, one at 99.9 — too little spread to demo Low→Extreme meaningfully.
- No live weather, satellite, or urban-features providers exist at all (not
  broken — simply not built yet; 100% demo/seeded today).
- No React/TypeScript frontend — current UI is static HTML/CSS/JS.
- No PostGIS/ward-polygon support, only point lat/longs and 0–100 display
  coordinates.
- No Alembic migrations (uses `create_all` directly).
- Only 2 of the 12 requested database tables exist.
- No Data Sources status page/endpoint, no ingestion/audit logging.
- No git repository (about to be initialized).

## 4. What should be done next

See `docs/IMPLEMENTATION_PLAN_V2.md` for the full plan. Immediate next steps, in
order: git init + branch, fix the CLI bug, build out the 12-table schema, replace
the risk engine with a transparent formula, build provider adapters, then the
React frontend, then Docker/docs polish.

## 5. Missing API keys, datasets, or environment variables

None are required for demo mode — that's intentional and will stay true. For live
modes, you will need to obtain and set, once the corresponding code exists:

- `WEATHER_API_KEY` + `WEATHER_PROVIDER=openweathermap` — only if you want the
  key-based weather path; the no-key Open-Meteo path needs nothing.
- `SATELLITE_PROVIDER=gee`, `GEE_PROJECT_ID`, `GEE_SERVICE_ACCOUNT_EMAIL`,
  `GEE_CREDENTIALS_PATH` — Google Earth Engine service account credentials.
- `COPERNICUS_CLIENT_ID`, `COPERNICUS_CLIENT_SECRET` — only if you want the
  optional Sentinel/Copernicus path instead of or alongside GEE.
- `MAP_PROVIDER_KEY` — only needed if you choose a tile provider that requires a
  key (e.g. MapTiler); free keyless styles (e.g. OpenFreeMap) work without one.
- Real Jodhpur ward boundary GeoJSON, if you have or can obtain an authoritative
  source — the seeded V2 boundaries are simplified placeholders, not official data.

## 6. Exact commands to run locally (current state, verified)

```bash
cd heatshield-ai
python -m venv .venv

# Windows PowerShell
.\.venv\Scripts\Activate.ps1
# macOS/Linux
# source .venv/bin/activate

pip install -r requirements.txt
pytest -q
uvicorn backend.main:app --reload
```
Then open http://127.0.0.1:8000 — this works today, before any V2 changes.
