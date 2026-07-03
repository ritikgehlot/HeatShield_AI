"""Central environment configuration.

Single place that reads env vars, so nothing else in the codebase calls
``os.getenv`` directly for a secret. Never logs a raw key value — only whether
a variable is set, which is what lets the app report provider status honestly
without leaking credentials into logs.
"""
from __future__ import annotations

import logging
import os
from dataclasses import dataclass, field

logger = logging.getLogger("heatshield.config")


def _get(name: str, default: str = "") -> str:
    return os.getenv(name, default)


@dataclass(frozen=True)
class Settings:
    app_env: str = field(default_factory=lambda: _get("APP_ENV", "development"))
    database_url: str = field(default_factory=lambda: _get("DATABASE_URL", "sqlite:///./heatshield.db"))
    frontend_url: str = field(default_factory=lambda: _get("FRONTEND_URL", "http://localhost:5173"))

    weather_provider: str = field(default_factory=lambda: _get("WEATHER_PROVIDER", "open-meteo"))
    weather_api_key: str = field(default_factory=lambda: _get("WEATHER_API_KEY"))

    satellite_provider: str = field(default_factory=lambda: _get("SATELLITE_PROVIDER", "none"))
    gee_project_id: str = field(default_factory=lambda: _get("GEE_PROJECT_ID"))
    gee_service_account_email: str = field(default_factory=lambda: _get("GEE_SERVICE_ACCOUNT_EMAIL"))
    gee_credentials_path: str = field(default_factory=lambda: _get("GEE_CREDENTIALS_PATH"))
    copernicus_client_id: str = field(default_factory=lambda: _get("COPERNICUS_CLIENT_ID"))
    copernicus_client_secret: str = field(default_factory=lambda: _get("COPERNICUS_CLIENT_SECRET"))

    map_provider_key: str = field(default_factory=lambda: _get("MAP_PROVIDER_KEY"))
    cache_url: str = field(default_factory=lambda: _get("CACHE_URL"))

    @property
    def is_postgres(self) -> bool:
        return self.database_url.startswith("postgresql")

    @property
    def weather_live_configured(self) -> bool:
        # Open-Meteo needs no key; OpenWeatherMap-style providers need one.
        if self.weather_provider in ("open-meteo", "", "demo"):
            return self.weather_provider == "open-meteo"
        return bool(self.weather_api_key)

    @property
    def satellite_live_configured(self) -> bool:
        if self.satellite_provider == "gee":
            return bool(self.gee_project_id and self.gee_service_account_email and self.gee_credentials_path)
        if self.satellite_provider == "copernicus":
            return bool(self.copernicus_client_id and self.copernicus_client_secret)
        return False


settings = Settings()


def log_startup_config() -> None:
    """Logs which providers are live/demo/not-configured. Never logs key values."""
    logger.info("APP_ENV=%s | DATABASE_URL dialect=%s", settings.app_env, "postgres" if settings.is_postgres else "sqlite")
    logger.info(
        "weather_provider=%s configured=%s",
        settings.weather_provider,
        settings.weather_live_configured,
    )
    logger.info(
        "satellite_provider=%s configured=%s",
        settings.satellite_provider,
        settings.satellite_live_configured,
    )
    if settings.app_env == "production" and settings.database_url.startswith("sqlite"):
        logger.warning("Running with SQLite in APP_ENV=production — use PostgreSQL for real deployments.")
