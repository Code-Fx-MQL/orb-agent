"""Cache OHLCV em disco com TTL — reduz carga CCXT entre scans."""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

from orb_agent.config.settings import settings


def _cache_dir() -> Path:
    return Path(settings.memory_dir).parent / "cache" / "ohlcv"


def _cache_path(pair: str, timeframe: str, limit: int) -> Path:
    key = f"{pair.upper()}_{timeframe}_{limit}.json"
    return _cache_dir() / key


def get_cached(pair: str, timeframe: str, limit: int) -> list[dict[str, Any]] | None:
    if not settings.cache_enabled:
        return None
    path = _cache_path(pair, timeframe, limit)
    if not path.exists():
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None
    age_sec = time.time() - float(payload.get("cached_at", 0))
    if age_sec > settings.cache_ttl_seconds:
        return None
    candles = payload.get("candles")
    return list(candles) if candles else None


def set_cached(pair: str, timeframe: str, limit: int, candles: list[dict[str, Any]]) -> None:
    if not settings.cache_enabled:
        return
    path = _cache_path(pair, timeframe, limit)
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "pair": pair.upper(),
        "timeframe": timeframe,
        "limit": limit,
        "cached_at": time.time(),
        "candles": candles,
    }
    path.write_text(json.dumps(payload, default=str), encoding="utf-8")


def cache_stats() -> dict[str, Any]:
    cache_root = _cache_dir()
    if not cache_root.exists():
        return {"files": 0, "enabled": settings.cache_enabled}
    files = list(cache_root.glob("*.json"))
    return {
        "enabled": settings.cache_enabled,
        "ttl_seconds": settings.cache_ttl_seconds,
        "files": len(files),
        "path": str(cache_root),
    }