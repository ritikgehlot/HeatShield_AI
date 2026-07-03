"""Abstract base classes for external data providers.

Each provider exposes connect(), refresh(), and get_status() so the
application can uniformly manage diverse data sources.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional


@dataclass
class ProviderStatus:
    """Standardised status returned by every provider."""
    provider_name: str
    provider_type: str  # weather, satellite, urban
    is_connected: bool
    mode: str  # demo, live
    last_success_at: Optional[datetime] = None
    last_error_at: Optional[datetime] = None
    last_error_message: Optional[str] = None
    data_freshness_minutes: Optional[float] = None
    extra: dict[str, Any] = field(default_factory=dict)


class BaseProvider(ABC):
    """Root interface for all external-data providers."""

    @abstractmethod
    def connect(self) -> bool:
        """Attempt to connect / authenticate.  Returns True on success."""
        ...

    @abstractmethod
    def refresh(self) -> dict[str, Any]:
        """Fetch the latest batch of data from the source."""
        ...

    @abstractmethod
    def get_status(self) -> ProviderStatus:
        """Return current connection & data-freshness status."""
        ...


class WeatherProvider(BaseProvider):
    """Interface for weather observation providers."""

    @abstractmethod
    def get_current_weather(self, lat: float, lon: float) -> dict[str, Any]:
        """Return current weather for a location."""
        ...


class SatelliteProvider(BaseProvider):
    """Interface for satellite / remote-sensing providers."""

    @abstractmethod
    def get_lst(self, lat: float, lon: float, date: Optional[str] = None) -> dict[str, Any]:
        """Return land-surface temperature for a location."""
        ...

    @abstractmethod
    def get_ndvi(self, lat: float, lon: float, date: Optional[str] = None) -> dict[str, Any]:
        """Return NDVI for a location."""
        ...


class UrbanFeaturesProvider(BaseProvider):
    """Interface for urban morphology / feature providers."""

    @abstractmethod
    def get_features(self, lat: float, lon: float, radius_m: float = 500) -> dict[str, Any]:
        """Return built-up %, road density, etc. for an area."""
        ...
