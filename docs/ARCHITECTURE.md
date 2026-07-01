# Architecture

```text
Browser UI (HTML/CSS/JS)
          │ REST / JSON
          ▼
FastAPI application
 ├─ Ward API
 ├─ CSV data ingestion API
 ├─ What-if simulator
 └─ Action-brief generator
          │
          ▼
SQLAlchemy ORM ── SQLite (local) / PostgreSQL (Docker)
          │
          ▼
Heat-risk engine
 ├─ RandomForest prototype model
 ├─ transparent feature-driver rules
 └─ cooling scenario calculator
```

## Security note

The hackathon prototype intentionally has no authentication. Add user authentication, audit logging, restricted CORS origins and role-based controls before any public or municipal deployment.
