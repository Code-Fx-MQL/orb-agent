#!/usr/bin/env python3
"""Gera deploy/easypanel/.env.production a partir de variaveis de ambiente (CI/CD)."""

from __future__ import annotations

import os
from pathlib import Path

PROD_KEYS = [
    "PORT",
    "ORB_MODE",
    "ORB_PAIRS",
    "ORB_DATA_SOURCE",
    "ORB_REQUIRE_RETEST",
    "ORB_BREAKOUT_MODE",
    "ORB_BLOCK_NEWS",
    "ORB_WEBHOOK_ENABLED",
    "ORB_WEBHOOK_URL",
    "ORB_WEBHOOK_APP_ID",
    "ORB_TELEGRAM_ENABLED",
    "ORB_TELEGRAM_BOT_TOKEN",
    "ORB_TELEGRAM_CHAT_ID",
    "ORB_LIVE_APPROVED",
    "ORB_LIVE_APPROVAL_TOKEN",
    "ORB_BROKER_MODE",
    "ORB_LANGSMITH_TRACING",
    "ORB_LANGSMITH_API_KEY",
    "ORB_LANGSMITH_PROJECT",
    "ORB_UI_PASSWORD",
    "ORB_UI_AUTO_REFRESH_ENABLED",
    "ORB_UI_AUTO_REFRESH_SECONDS",
]

DEFAULTS = {
    "PORT": "8501",
    "ORB_MODE": "paper",
    "ORB_PAIRS": "XAUUSD,EURUSD",
    "ORB_DATA_SOURCE": "auto",
    "ORB_REQUIRE_RETEST": "true",
    "ORB_BREAKOUT_MODE": "retest",
    "ORB_BLOCK_NEWS": "true",
    "ORB_WEBHOOK_ENABLED": "true",
    "ORB_WEBHOOK_APP_ID": "orb-agent",
    "ORB_TELEGRAM_ENABLED": "false",
    "ORB_LIVE_APPROVED": "false",
    "ORB_BROKER_MODE": "stub",
    "ORB_LANGSMITH_TRACING": "false",
    "ORB_LANGSMITH_PROJECT": "orb-agent",
    "ORB_UI_AUTO_REFRESH_ENABLED": "true",
    "ORB_UI_AUTO_REFRESH_SECONDS": "300",
}

SECRET_MAP = {
    "ORB_WEBHOOK_URL": "WEBHOOK_URL",
    "ORB_TELEGRAM_BOT_TOKEN": "TELEGRAM_BOT_TOKEN",
    "ORB_TELEGRAM_CHAT_ID": "TELEGRAM_CHAT_ID",
    "ORB_UI_PASSWORD": "ORB_UI_PASSWORD",
    "ORB_LIVE_APPROVAL_TOKEN": "ORB_LIVE_APPROVAL_TOKEN",
    "ORB_LANGSMITH_API_KEY": "LANGSMITH_API_KEY",
}


def _value_for(key: str) -> str:
    if key in os.environ and os.environ[key]:
        return os.environ[key]
    alt = SECRET_MAP.get(key)
    if alt and alt in os.environ and os.environ[alt]:
        return os.environ[alt]
    return DEFAULTS.get(key, "")


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    out = root / "deploy" / "easypanel" / ".env.production"
    out.parent.mkdir(parents=True, exist_ok=True)

    lines = ["# ORB Agent - gerado por CI/CD", ""]
    for key in PROD_KEYS:
        lines.append(f"{key}={_value_for(key)}")
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Gerado: {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())