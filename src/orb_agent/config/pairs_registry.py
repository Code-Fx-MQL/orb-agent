"""Registo dinamico de pares ativos e mapeamentos CCXT custom."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from orb_agent.config.settings import settings
from orb_agent.providers.symbols import PAIR_MARKETS, PairMarket

_PAIR_KEY_RE = re.compile(r"^[A-Z0-9]{3,12}$")
_BUILTIN_KEYS = frozenset(PAIR_MARKETS.keys())
_SUPPORTED_EXCHANGES = ("kraken", "gate", "lighter", "bitstamp", "phemex", "mexc", "stub")


def _config_path() -> Path:
    return Path(settings.memory_dir) / "pairs_config.json"


def _default_active_pairs() -> list[str]:
    return [p.strip().upper() for p in settings.pairs.split(",") if p.strip()]


class PairsRegistry:
    def __init__(self) -> None:
        self._path = _config_path()
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._data = self._load()

    def _load(self) -> dict[str, Any]:
        if self._path.exists():
            raw = json.loads(self._path.read_text(encoding="utf-8"))
            active = [p.strip().upper() for p in raw.get("active_pairs", []) if p.strip()]
            custom = raw.get("custom_pairs") or {}
            return {
                "active_pairs": active or _default_active_pairs(),
                "custom_pairs": {k.upper(): v for k, v in custom.items()},
            }
        return {"active_pairs": _default_active_pairs(), "custom_pairs": {}}

    def get_active_pairs(self) -> list[str]:
        return list(self._data["active_pairs"])

    def list_known_pairs(self) -> list[str]:
        return sorted(set(_BUILTIN_KEYS) | set(self._data["custom_pairs"]))

    def is_known_pair(self, pair: str) -> bool:
        key = pair.upper().replace("/", "").replace("_", "")
        return key in _BUILTIN_KEYS or key in self._data["custom_pairs"]

    def resolve_market(self, pair: str) -> PairMarket:
        key = pair.upper().replace("/", "").replace("_", "")
        if key in _BUILTIN_KEYS:
            return PAIR_MARKETS[key]
        custom = self._data["custom_pairs"].get(key)
        if custom:
            return PairMarket(
                exchange_id=custom["exchange_id"],
                symbol=custom["symbol"],
                note=custom.get("note", ""),
                priority=int(custom.get("priority", 50)),
                stub_only=bool(custom.get("stub_only", False)),
            )
        supported = ", ".join(self.list_known_pairs())
        raise ValueError(f"Par '{pair}' nao configurado. Disponiveis: {supported}")


_registry: PairsRegistry | None = None


def get_pairs_registry() -> PairsRegistry:
    global _registry
    if _registry is None:
        _registry = PairsRegistry()
    return _registry