# --- Stage 1: build the React frontend ---
FROM node:20-slim AS frontend
WORKDIR /frontend
COPY frontend/package.json frontend/package-lock.json* ./
RUN npm install
COPY frontend/ ./
RUN npm run build

# --- Stage 2: Python backend, serving the built frontend ---
FROM python:3.12-slim
WORKDIR /app

# Use PostGIS image for the db service; here the app only needs psycopg (in requirements).
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ ./backend/
COPY alembic/ ./alembic/
COPY alembic.ini ./
COPY data/ ./data/
COPY scripts/ ./scripts/

# Bring in the built SPA so uvicorn serves it at /
COPY --from=frontend /frontend/dist ./frontend/dist

ENV APP_ENV=production
EXPOSE 8000
# Note: run `alembic upgrade head` once against Postgres before/at first boot.
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
