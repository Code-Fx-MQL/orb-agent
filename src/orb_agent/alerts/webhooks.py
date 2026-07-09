"""Webhooks — n8n e Discord (Telegram na Fase 8)."""

from __future__ import annotations

import math
from datetime import UTC, datetime
from typing import Any

import httpx
import structlog

from orb_agent.config.settings import settings

logger = structlog.get_logger(__name__)

LEVEL_EMOJI = {
    "info": "i",
    "success": "OK",
    "warning": "!",
    "error": "X",
    "trade": "$",
}


def _sanitize_for_json(obj: Any) -> Any:
    if isinstance(obj, float):
        if math.isnan(obj) or math.isinf(obj):
            return None
        return obj
    if isinstance(obj, dict):
        return {k: _sanitize_for_json(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_sanitize_for_json(v) for v in obj]
    return obj


def _format_message(title: str, body: str, level: str) -> str:
    emoji = LEVEL_EMOJI.get(level, "*")
    return f"{emoji} ORB Agent — {title}\n{body}"


def send_n8n_webhook(
    event_type: str,
    title: str,
    body: str,
    level: str = "info",
    data: dict[str, Any] | None = None,
) -> dict[str, Any]:
    url = settings.webhook_url
    if not url:
        return {"sent": False, "channel": "n8n", "reason": "WEBHOOK_URL nao configurada"}

    payload = {
        "app": settings.webhook_app_id,
        "source": settings.webhook_app_id,
        "event_type": event_type,
        "level": level,
        "title": title,
        "body": body,
        "message": _format_message(title, body, level),
        "timestamp": datetime.now(UTC).isoformat(),
        "mode": settings.mode.value,
        "data": _sanitize_for_json(data or {}),
    }

    try:
        resp = httpx.post(url, json=_sanitize_for_json(payload), timeout=15)
        ok = resp.status_code in (200, 201, 202, 204)
        return {
            "sent": ok,
            "channel": "n8n",
            "status": resp.status_code,
            "event_type": event_type,
        }
    except httpx.HTTPError as exc:
        logger.warning("n8n_webhook_failed", error=str(exc), event_type=event_type)
        return {"sent": False, "channel": "n8n", "reason": str(exc), "event_type": event_type}


def send_discord(message: str) -> dict[str, Any]:
    url = settings.discord_webhook_url
    if not url:
        return {"sent": False, "channel": "discord", "reason": "URL nao configurada"}
    try:
        resp = httpx.post(url, json={"content": message[:2000]}, timeout=10)
        return {"sent": resp.status_code in (200, 204), "channel": "discord", "status": resp.status_code}
    except httpx.HTTPError as exc:
        logger.warning("discord_webhook_failed", error=str(exc))
        return {"sent": False, "channel": "discord", "reason": str(exc)}


def webhook_status() -> dict[str, Any]:
    configured = bool(settings.webhook_url)
    return {
        "enabled": settings.webhook_enabled,
        "configured": configured,
        "ready": settings.webhook_enabled and configured,
    }


def send_webhook(
    event_type: str,
    title: str,
    body: str,
    level: str = "info",
    data: dict[str, Any] | None = None,
) -> dict[str, Any]:
    if not settings.webhook_enabled:
        return {"sent": False, "reason": "WEBHOOK_ENABLED=false", "results": []}

    message = _format_message(title, body, level)
    results = [
        send_n8n_webhook(event_type, title, body, level=level, data=data),
        send_discord(message),
    ]
    any_sent = any(r.get("sent") for r in results)
    return {"sent": any_sent, "event_type": event_type, "results": results}