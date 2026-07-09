"""Rotacao de tokens live — Fase 7."""

from __future__ import annotations

import json
import re
import secrets
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from orb_agent.config.settings import settings


def _rotation_log_path() -> Path:
    return Path(settings.audit_dir) / "token_rotation.jsonl"


def generate_live_token(length: int = 32) -> str:
    return secrets.token_urlsafe(length)


def rotate_live_token(
    current_token: str | None = None,
    env_path: str | Path = ".env",
    force: bool = False,
) -> dict[str, Any]:
    """Gera novo token e atualiza .env."""
    expected = settings.live_approval_token

    if expected and current_token and current_token != expected and not force:
        return {"rotated": False, "reason": "Token atual incorreto — use --force para override"}

    if expected and not current_token and not force:
        return {"rotated": False, "reason": "Informe --live-token com o token atual"}

    new_token = generate_live_token()
    path = Path(env_path)
    if not path.exists():
        return {"rotated": False, "reason": f"{path} nao encontrado"}

    content = path.read_text(encoding="utf-8")
    if "ORB_LIVE_APPROVAL_TOKEN=" in content:
        content = re.sub(
            r"ORB_LIVE_APPROVAL_TOKEN=.*",
            f"ORB_LIVE_APPROVAL_TOKEN={new_token}",
            content,
        )
    else:
        content += f"\nORB_LIVE_APPROVAL_TOKEN={new_token}\n"

    path.write_text(content, encoding="utf-8")

    log_entry = {
        "timestamp": datetime.now(UTC).isoformat(),
        "action": "token_rotated",
        "old_token_prefix": (expected or "")[:4] + "****" if expected else "none",
        "new_token_prefix": new_token[:4] + "****",
        "forced": force,
    }
    log_path = _rotation_log_path()
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(log_entry) + "\n")

    return {
        "rotated": True,
        "new_token": new_token,
        "message": "Token rotacionado — reinicie processos e use --live-token com o novo token",
        "log_path": str(log_path),
    }