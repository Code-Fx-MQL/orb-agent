"""Sincronizacao opcional com Mem0 Platform (cloud)."""

from __future__ import annotations

from typing import Any

import structlog

from orb_agent.config.settings import settings

logger = structlog.get_logger(__name__)

_sync: "Mem0Sync | None" = None


class Mem0Sync:
    def __init__(self, api_key: str, user_id: str) -> None:
        self._user_id = user_id
        self._client: Any = None
        try:
            from mem0 import MemoryClient

            self._client = MemoryClient(api_key=api_key)
        except ImportError:
            logger.warning("mem0_not_installed", hint='pip install -e ".[memory]"')
        except Exception as exc:
            logger.warning("mem0_init_failed", error=str(exc))

    @property
    def available(self) -> bool:
        return self._client is not None

    def sync_setup(self, entry: dict[str, Any]) -> dict[str, Any]:
        if not self.available:
            return {"synced": False, "reason": "Mem0 indisponivel"}
        pair = entry.get("pair", "")
        direction = entry.get("direction", "")
        conf = entry.get("confidence", 0)
        trade = entry.get("trade_params") or {}
        content = (
            f"ORB setup {pair} {direction} conf={conf:.0%} "
            f"entry={trade.get('entry')} sl={trade.get('stop_loss')} tp={trade.get('take_profit')} "
            f"rr=1:{trade.get('risk_reward', 0)} id={entry.get('id')}"
        )
        messages = [
            {"role": "user", "content": content},
            {"role": "assistant", "content": f"Setup ORB registrado para {pair}."},
        ]
        try:
            result = self._client.add(messages, user_id=self._user_id)
            return {"synced": True, "mem0_result": result}
        except Exception as exc:
            logger.warning("mem0_sync_setup_failed", error=str(exc))
            return {"synced": False, "reason": str(exc)}


def get_mem0_sync() -> Mem0Sync | None:
    global _sync
    if not settings.mem0_enabled or not settings.mem0_api_key:
        return None
    if _sync is None:
        _sync = Mem0Sync(settings.mem0_api_key, settings.mem0_user_id)
    return _sync if _sync.available else None


def reset_mem0_sync() -> None:
    global _sync
    _sync = None