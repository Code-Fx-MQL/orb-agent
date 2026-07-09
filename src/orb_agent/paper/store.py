"""Paper trading — posicoes simuladas em JSON."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from uuid import uuid4

from orb_agent.config.settings import settings


def _paper_path() -> Path:
    return Path(settings.memory_dir) / "paper_trades.json"


class PaperStore:
    def __init__(self) -> None:
        self._path = _paper_path()
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._data = self._load()

    def _load(self) -> dict[str, Any]:
        if self._path.exists():
            return json.loads(self._path.read_text(encoding="utf-8"))
        return {"open": [], "closed": [], "stats": {}}

    def _save(self) -> None:
        self._path.write_text(json.dumps(self._data, indent=2, default=str), encoding="utf-8")

    def open_position(
        self,
        pair: str,
        trade_params: dict[str, Any],
        setup_id: str | None = None,
    ) -> dict[str, Any]:
        pair = pair.upper()
        if any(p["pair"] == pair for p in self._data["open"]):
            return {"opened": False, "reason": f"Ja existe posicao aberta em {pair}"}

        position = {
            "id": str(uuid4())[:8],
            "setup_id": setup_id,
            "pair": pair,
            "direction": trade_params.get("direction"),
            "entry": trade_params.get("entry"),
            "stop_loss": trade_params.get("stop_loss"),
            "take_profit": trade_params.get("take_profit"),
            "risk_reward": trade_params.get("risk_reward"),
            "position_size_lots": trade_params.get("position_size_lots"),
            "opened_at": datetime.now(UTC).isoformat(),
            "status": "open",
        }
        self._data["open"].append(position)
        self._save()
        return {"opened": True, "position": position}

    def close_position(
        self,
        position_id: str,
        outcome: str,
        exit_price: float,
        pnl_percent: float,
    ) -> dict[str, Any] | None:
        for i, pos in enumerate(self._data["open"]):
            if pos["id"] == position_id:
                closed = {
                    **pos,
                    "status": "closed",
                    "outcome": outcome,
                    "exit_price": exit_price,
                    "pnl_percent": pnl_percent,
                    "closed_at": datetime.now(UTC).isoformat(),
                }
                self._data["open"].pop(i)
                self._data["closed"].append(closed)
                self._update_stats(closed)
                self._save()
                return closed
        return None

    def check_exits(self, pair: str, current_price: float) -> list[dict[str, Any]]:
        closed: list[dict[str, Any]] = []
        for pos in list(self._data["open"]):
            if pos["pair"] != pair.upper():
                continue
            direction = pos.get("direction", "")
            sl_raw, tp_raw, entry_raw = pos.get("stop_loss"), pos.get("take_profit"), pos.get("entry")
            if sl_raw is None or tp_raw is None or entry_raw is None:
                continue
            sl, tp, entry = float(sl_raw), float(tp_raw), float(entry_raw)

            if direction == "bullish":
                hit_tp = current_price >= tp
                hit_sl = current_price <= sl
            else:
                hit_tp = current_price <= tp
                hit_sl = current_price >= sl

            if hit_tp:
                pnl = abs(tp - entry) / entry * 100
                result = self.close_position(pos["id"], "win", tp, round(pnl, 4))
                if result:
                    closed.append(result)
            elif hit_sl:
                pnl = -abs(entry - sl) / entry * 100
                result = self.close_position(pos["id"], "loss", sl, round(pnl, 4))
                if result:
                    closed.append(result)
        return closed

    def _update_stats(self, entry: dict[str, Any]) -> None:
        pair = entry["pair"]
        stats = self._data["stats"].setdefault(pair, {
            "total": 0, "wins": 0, "losses": 0, "total_pnl": 0.0,
        })
        stats["total"] += 1
        if entry.get("outcome") == "win":
            stats["wins"] += 1
        elif entry.get("outcome") == "loss":
            stats["losses"] += 1
        stats["total_pnl"] = round(stats.get("total_pnl", 0) + entry.get("pnl_percent", 0), 4)
        if stats["total"] > 0:
            stats["win_rate"] = round(stats["wins"] / stats["total"], 4)

    def get_closed(self) -> list[dict[str, Any]]:
        return list(self._data["closed"])

    def summary(self) -> dict[str, Any]:
        return {
            "open_positions": len(self._data["open"]),
            "closed_positions": len(self._data["closed"]),
            "open": self._data["open"],
            "recent_closed": self._data["closed"][-5:],
            "stats": self._data["stats"],
        }


_paper: PaperStore | None = None


def get_paper_store() -> PaperStore:
    global _paper
    if _paper is None:
        _paper = PaperStore()
    return _paper


def reset_paper_store() -> None:
    global _paper
    _paper = None