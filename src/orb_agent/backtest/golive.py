"""Exporta snapshot de backtest para checklist go-live."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from orb_agent.config.settings import settings


def backtest_golive_path() -> Path:
    return Path("data") / "backtest_golive.json"


def save_backtest_golive(results: dict[str, Any]) -> Path:
    path = backtest_golive_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "pairs": results.get("pairs", settings.pairs_list),
        "candle_limit": results.get("candle_limit"),
        "results": results.get("results", results),
        "totals": results.get("totals"),
        "summary": results.get("summary"),
    }
    path.write_text(json.dumps(payload, indent=2, default=str), encoding="utf-8")
    return path