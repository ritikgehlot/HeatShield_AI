# Session Handoff — HeatShield AI V2

Written after actually running the code, not from memory of what was intended.
See also `docs/RESUME_PROGRESS.md`, kept in sync with this file.

## MILESTONE 1 — Core working platform: COMPLETE AND VERIFIED

- Repo audited; one real bug found in the original prototype (CLI script
  `sys.path` issue) and fixed.
- Git: `main` = true unmodified baseline, `feature/live-platform-v2` = all V2 work.
- 13-table schema (`backend/models.py`), transparent hybrid risk engine
  (`backend/risk_engine.py`, replacing the old RandomForest-on-synthetic-data
  wrapper), 4 provider adapters (`backend/providers/`), intervention optimizer
  + what-if simulator (`backend/interventions.py`), 16-ward seed dataset
  (`backend/seed.py`), full V2 API (`backend/routers/`), legacy V1 endpoints
  preserved unchanged (`backend/routers/legacy.py`).
- **Full test suite: 19/19 passing.** App boots cleanly; every endpoint hit
  with real HTTP requests, not assumed working.
- CLI import script bug fixed and re-verified — the exact command
  README documents now works with no `PYTHONPATH` workaround.
- Two real bugs found and fixed *while building* the V2 layer itself: the
  dashboard weather/satellite display used to show a bare "error" tile
  instead of falling back to labeled demo values when live fetch fails with
  nothing cached; and the Data Sources status check used to assert "live"
  for weather based on static config rather than an actual fetch attempt.
  Both fixed so "demo always works" and "never claim fake live status" hold
  in practice, not just in intent.
- Honest limitation, unchanged from the plan: live weather/satellite/OSM HTTP
  calls are written correctly but this sandbox's network can't reach their
  domains, so they're verified via graceful-failure paths here, not a real
  successful live fetch. Verify on your own machine.

## MILESTONE 2 — Premium dashboard UI: IN PROGRESS NEXT

No frontend code exists yet beyond the original static HTML/CSS/JS (kept,
still functional, served as a fallback if `frontend/dist` isn't built).
Building: React + TypeScript + Vite + Tailwind + MapLibre + TanStack Query +
Recharts + Lucide in `frontend/`.

## API keys or datasets still required

Nothing for demo mode. For live modes: `WEATHER_API_KEY` only for the
OpenWeatherMap path (Open-Meteo needs none), GEE service-account credentials
for satellite, Copernicus credentials as an alternative, and an authoritative
Jodhpur ward-boundary GeoJSON if you have one (seeded ones are simplified
placeholders).

## Commands to run the app locally — verified working

```bash
cd heatshield-ai
python -m venv .venv
# Windows PowerShell: .\.venv\Scripts\Activate.ps1
# macOS/Linux:        source .venv/bin/activate
pip install -r requirements.txt
pytest -q                              # 19 passed
uvicorn backend.main:app --reload
```
Then open http://127.0.0.1:8000.
