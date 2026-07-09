"""Webhooks — n8n, Discord e Telegram."""

from __future__ import annotations

import math
from datetime import UTC, datetime
from typing import Any

import httpx
import structlog

from orb_agent.alerts.telegram_messages import (
    format_generic_message,
    format_paper_alert_message,
    format_scan_complete_message,
    format_setup_found_message,
)
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


def telegram_status() -> dict[str, Any]:
    configured = bool(settings.telegram_bot_token and settings.telegram_chat_id)
    return {
        "enabled": settings.telegram_enabled,
        "configured": configured,
        "ready": settings.telegram_enabled and configured,
        "chat_id_set": bool(settings.telegram_chat_id),
    }


def _telegram_payload_for_event(
    event_type: str,
    title: str,
    body: str,
    level: str,
    data: dict[str, Any] | None,
) -> tuple[str, str | None]:
    if event_type == "setup_found" and data:
        return format_setup_found_message(data), "HTML"
    if event_type == "paper_alert" and data:
        return format_paper_alert_message(data), "HTML"
    if event_type == "scan_complete" and data:
        return format_scan_complete_message(data, body), "HTML"
    return format_generic_message(title, body, level), "HTML"


def send_telegram(message: str, parse_mode: str | None = None) -> dict[str, Any]:
    if not settings.telegram_enabled:
        return {"sent": False, "channel": "telegram", "reason": "TELEGRAM_ENABLED=false"}
    token = settings.telegram_bot_token
    chat_id = settings.telegram_chat_id
    if not token or not chat_id:
        return {"sent": False, "channel": "telegram", "reason": "Token/chat_id nao configurados"}
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload: dict[str, Any] = {"chat_id": chat_id, "text": message[:4096]}
    if parse_mode:
        payload["parse_mode"] = parse_mode
    try:
        resp = httpx.post(url, json=payload, timeout=10)
        resp_data = resp.json()
        return {
            "sent": resp_data.get("ok", False),
            "channel": "telegram",
            "status": resp.status_code,
        }
    except httpx.HTTPError as exc:
        logger.warning("telegram_webhook_failed", error=str(exc))
        return {"sent": False, "channel": "telegram", "reason": str(exc)}


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
    tg_text, tg_mode = _telegram_payload_for_event(event_type, title, body, level, data)
    results = [
        send_n8n_webhook(event_type, title, body, level=level, data=data),
        send_discord(message),
        send_telegram(tg_text, parse_mode=tg_mode),
    ]
    any_sent = any(r.get("sent") for r in results)
    return {"sent": any_sent, "event_type": event_type, "results": results}