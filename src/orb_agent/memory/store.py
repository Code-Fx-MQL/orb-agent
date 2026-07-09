"""Memoria JSON de setups e outcomes."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from uuid import uuid4

from orb_agent.config.settings import settings


def _memory_path() -> Path:
    return Path(settings.memory_dir) / "trade_memory.json"


class TradeMemory:
    def __init__(self) -> None:
        self._path = _memory_path()
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._data = self._load()

    def _load(self) -> dict[str, Any]:
        if self._path.exists():
            return json.loads(self._path.read_text(encoding="utf-8"))
        return {"entries": [], "stats": {}}

    def _save(self) -> None:
        self._path.write_text(json.dumps(self._data, indent=2, default=str), encoding="utf-8")

    def log_setup(
        self,
        pair: str,
        setup: dict[str, Any],
        trade_params: dict[str, Any] | None = None,
        backtest: dict[str, Any] | None = None,
    ) -> str:
        setup_id = str(uuid4())[:8]
        entry = {
            "id": setup_id,
            "pair": pair.upper(),
            "logged_at": datetime.now(UTC).isoformat(),
            "direction": setup.get("direction"),
            "confidence": setup.get("confidence"),
            "trade_params": trade_params,
            "backtest_snapshot": backtest,
            "outcome": None,
            "pnl_percent": None,
        }
        self._data["entries"].append(entry)
        self._save()
        mem0 = self._sync_mem0(entry)
        if mem0:
            entry["mem0_sync"] = mem0
        return setup_id

    def _sync_mem0(self, entry: dict[str, Any]) -> dict[str, Any] | None:
        try:
            from orb_agent.memory.mem0_sync import get_mem0_sync

            client = get_mem0_sync()
            if client:
                return client.sync_setup(entry)
        except Exception:
            return None
        return None

    def log_outcome(self, setup_id: str, outcome: str, pnl_percent: float) -> dict[str, Any] | None:
        for e in self._data["entries"]:
            if e["id"] == setup_id:
                e["outcome"] = outcome
                e["pnl_percent"] = pnl_percent
                e["closed_at"] = datetime.now(UTC).isoformat()
                self._save()
                return e
        return None

    def summary(self) -> dict[str, Any]:
        return {
            "total_entries": len(self._data["entries"]),
            "entries": self._data["entries"][-20:],
        }


_memory: TradeMemory | None = None


def get_memory() -> TradeMemory:
    global _memory
    if _memory is None:
        _memory = TradeMemory()
    return _memory


def reset_memory() -> None:
    global _memory
    _memory = None