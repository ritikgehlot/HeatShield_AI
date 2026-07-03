"""Common contract every provider adapter follows.

The one rule that matters more than any other in this module: when live
access fails or isn't configured, adapters return an explicit
NOT_CONFIGURED/ERROR/CACHED_FALLBACK result — they never synthesize a number
and label it live. Demo data is always tagged DEMO and carries its own
message saying so.
"""
from __future__ import annotations

import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional


class ProviderMode(str, Enum):
    DEMO = "demo"
    LIVE = "live"
    CACHED_FALLBACK = "cached_fallback"
    NOT_CONFIGURED = "not_configured"
    ERROR = "error"


@dataclass
class ProviderResult:
    provider_key: str
    provider_name: str
    mode: ProviderMode
    data: dict[str, Any] = field(default_factory=dict)
    source: str = ""
    observed_at: Optional[datetime] = None
    fetched_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    message: str = ""
    error: Optional[str] = None

    @property
    def is_live(self) -> bool:
        return self.mode == ProviderMode.LIVE

    def to_status_dict(self) -> dict[str, Any]:
        return {
            "provider_key": self.provider_key,
            "provider_name": self.provider_name,
            "mode": self.mode.value,
            "connected": self.mode in (ProviderMode.LIVE, ProviderMode.DEMO, ProviderMode.CACHED_FALLBACK),
            "source": self.source,
            "observed_at": self.observed_at.isoformat() if self.observed_at else None,
            "fetched_at": self.fetched_at.isoformat(),
            "message": self.message,
            "last_error": self.error,
        }


class TTLCache:
    """Small in-process cache so repeated dashboard loads don't re-hit a live
    API every request. Not shared across processes — CACHE_URL/Redis is the
    documented upgrade path for multi-worker deployments (see
    docs/ARCHITECTURE_V2.md), not implemented here to keep this session's
    scope honest about what's actually been built and tested.
    """

    def __init__(self, ttl_seconds: int = 600):
        self.ttl_seconds = ttl_seconds
        self._store: dict[str, tuple[float, Any]] = {}

    def get(self, key: str) -> Any | None:
        item = self._store.get(key)
        if not item:
            return None
        expires_at, value = item
        if time.monotonic() > expires_at:
            self._store.pop(key, None)
            return None
        return value

    def set(self, key: str, value: Any) -> None:
        self._store[key] = (time.monotonic() + self.ttl_seconds, value)


class ProviderBase:
    provider_key: str = "base"
    provider_name: str = "Base provider"

    def status(self) -> ProviderResult:
        raise NotImplementedError
