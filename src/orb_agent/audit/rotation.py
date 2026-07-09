"""Rotacao do audit log quando excede tamanho maximo."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

from orb_agent.audit.logger import _audit_path
from orb_agent.config.settings import settings


def maybe_rotate_audit_log() -> dict[str, object]:
    path = _audit_path()
    if not path.exists():
        return {"rotated": False, "reason": "audit log ausente"}

    size_mb = path.stat().st_size / (1024 * 1024)
    if size_mb < settings.audit_max_mb:
        return {"rotated": False, "size_mb": round(size_mb, 2), "max_mb": settings.audit_max_mb}

    archive_dir = Path(settings.audit_dir) / "archive"
    archive_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
    archive_path = archive_dir / f"trade_audit_{stamp}.jsonl"
    path.rename(archive_path)

    return {
        "rotated": True,
        "size_mb": round(size_mb, 2),
        "archive": str(archive_path),
    }