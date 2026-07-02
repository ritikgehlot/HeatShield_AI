# HeatShield AI — Urban Heat Mitigation Decision Platform

A full-stack hackathon prototype that turns ward-level urban features into a heat-risk dashboard and compares cooling interventions before field implementation.

> **Important:** This repository runs using seeded demo data. The included risk model is a reproducible prototype, not a validated physical or policy model. Import validated satellite and municipal data before making real-world claims or decisions.

## What is included

- Responsive UI/UX dashboard with an interactive ward heat layer
- FastAPI REST backend with automatic Swagger API docs at `/docs`
- SQLite database by default; PostgreSQL support through Docker
- Random Forest–based prototype heat-risk model
- Explainable risk drivers and rule-based intervention recommendations
- “What-if” simulator for cool roofs, tree canopy and shade assets
- CSV data upload API and template download
- Unit/API tests
- Dockerfile and `docker-compose.yml`

## Project structure

```text
heatshield-ai/
├── backend/
│   ├── main.py              # FastAPI routes + static frontend
│   ├── risk_engine.py       # ML risk model and scenario logic
│   ├── models.py            # SQLAlchemy database models
│   ├── seed.py              # One-click demo dataset
│   ├── static/              # Dashboard frontend
│   └── tests/               # API tests
├── data/                    # CSV contract and sample file
├── docs/                    # Architecture + demo script
├── scripts/import_csv.py    # CLI importer
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

## Option A: Run locally with SQLite (recommended for hackathon demo)

SQLite is included with Python, so no database installation is required.

```bash
# 1) Open a terminal in the project folder
python -m venv .venv

# Windows PowerShell
.\.venv\Scripts\Activate.ps1

# macOS/Linux
# source .venv/bin/activate

# 2) Install dependencies
pip install -r requirements.txt

# 3) Start the application
uvicorn backend.main:app --reload
```

Open `http://127.0.0.1:8000` in your browser.

## Option B: Run with PostgreSQL using Docker

```bash
docker compose up --build
```

Open `http://localhost:8000`.

## Database connection

- Default local connection: `sqlite:///./heatshield.db`
- Docker PostgreSQL connection: `postgresql+psycopg://heatshield:heatshield@db:5432/heatshield`

Set a custom connection in `.env` or your terminal environment:

```bash
# Windows PowerShell
$env:DATABASE_URL="postgresql+psycopg://USER:PASSWORD@HOST:5432/DATABASE"

# macOS/Linux
export DATABASE_URL="postgresql+psycopg://USER:PASSWORD@HOST:5432/DATABASE"
```

## Import real ward data

1. Download the template from `http://127.0.0.1:8000/api/data/template`, or use `data/sample_city_features.csv`.
2. Add one row per ward.
3. Upload it from the dashboard, or run:

```bash
python scripts/import_csv.py data/sample_city_features.csv
```

## Run tests

```bash
pytest -q
```

## Push to GitHub

```bash
git init
git add .
git commit -m "Initial HeatShield AI prototype"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/heatshield-ai.git
git push -u origin main
```

## Suggested hackathon demo storyline

1. Choose a high-risk ward.
2. Explain its heat drivers: high land-surface temperature, low green cover and dense built-up area.
3. Use the what-if controls to compare cool roofs, tree canopy and shade assets.
4. Show projected risk reduction and the generated action brief.
5. Explain how a city can replace the demo data through the CSV pipeline.

## Next upgrades for a real deployment

- Integrate validated satellite processing (Landsat/Sentinel + Google Earth Engine).
- Add ward boundaries and real base maps through GIS services.
- Train on multi-season, weather-station and health-impact data.
- Add role-based access, audit logs and secure CORS policy.
- Calibrate interventions with local pilots and cost data.
