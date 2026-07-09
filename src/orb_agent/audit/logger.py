"""Audit log append-only — JSONL local."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from uuid import uuid4

from orb_agent.config.settings import settings


def _audit_path() -> Path:
    return Path(settings.audit_dir) / "trade_audit.jsonl"


class AuditLogger:
    """Registra decisoes de trading para compliance e debugging."""

    def __init__(self) -> None:
        self._path = _audit_path()
        self._path.parent.mkdir(parents=True, exist_ok=True)

    def log(self, event: str, details: dict[str, Any] | None = None) -> dict[str, Any]:
        entry = {
            "id": str(uuid4())[:12],
            "timestamp": datetime.now(UTC).isoformat(),
            "event": event,
            "mode": settings.mode.value,
            "details": details or {},
        }
        with self._path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(entry, default=str) + "\n")
        return entry

    def recent(self, limit: int = 20, event: str | None = None) -> list[dict[str, Any]]:
        if not self._path.exists():
            return []
        lines = self._path.read_text(encoding="utf-8").strip().splitlines()
        entries: list[dict[str, Any]] = []
        for line in reversed(lines):
            if not line.strip():
                continue
            try:
                entry = json.loads(line)
            except json.JSONDecodeError:
                continue
            if event and entry.get("event") != event:
                continue
            entries.append(entry)
            if len(entries) >= limit:
                break
        return entries

    def summary(self) -> dict[str, Any]:
        recent = self.recent(limit=100)
        counts: dict[str, int] = {}
        for entry in recent:
            ev = entry.get("event", "unknown")
            counts[ev] = counts.get(ev, 0) + 1
        return {
            "total_logged": len(recent),
            "event_counts": counts,
            "recent": self.recent(limit=10),
            "path": str(self._path),
        }


_audit: AuditLogger | None = None


def get_audit_logger() -> AuditLogger:
    global _audit
    if _audit is None:
        _audit = AuditLogger()
    return _audit


def reset_audit_logger() -> None:
    global _audit
    _audit = None