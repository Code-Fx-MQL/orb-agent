"""Metricas agregadas — memoria, paper, audit."""

from __future__ import annotations

from typing import Any

from orb_agent.audit.logger import get_audit_logger
from orb_agent.config.settings import settings
from orb_agent.memory.store import get_memory
from orb_agent.paper.store import get_paper_store


def estimate_drawdown(closed: list[dict[str, Any]]) -> float:
    cumulative = 0.0
    peak = 0.0
    max_dd = 0.0
    for pos in closed:
        cumulative += float(pos.get("pnl_percent", 0))
        peak = max(peak, cumulative)
        max_dd = max(max_dd, peak - cumulative)
    return round(max_dd, 4)


def _aggregate_win_rate(stats: dict[str, Any]) -> float:
    total_wins = 0
    total_trades = 0
    for pair_stats in stats.values():
        if isinstance(pair_stats, dict):
            total_wins += pair_stats.get("wins", 0)
            total_trades += pair_stats.get("total", 0)
    return round(total_wins / total_trades, 4) if total_trades > 0 else 0.0


def collect_metrics() -> dict[str, Any]:
    memory = get_memory().summary()
    paper = get_paper_store().summary()
    audit = get_audit_logger().summary()
    paper_closed = get_paper_store().get_closed()
    paper_stats = paper.get("stats", {})
    paper_wr = _aggregate_win_rate(paper_stats)

    return {
        "mode": settings.mode.value,
        "pairs": settings.pairs_list,
        "memory": {
            "total_setups": memory.get("total_entries", 0),
        },
        "paper": {
            "open_positions": paper.get("open_positions", 0),
            "closed_positions": paper.get("closed_positions", 0),
            "win_rate": paper_wr,
            "max_drawdown_pct": estimate_drawdown(paper_closed),
            "by_pair": paper_stats,
        },
        "audit": {
            "event_counts": audit.get("event_counts", {}),
            "total_recent": audit.get("total_logged", 0),
        },
        "kpis": {
            "open_paper_positions": paper.get("open_positions", 0),
            "paper_win_rate": paper_wr,
            "paper_max_drawdown_pct": estimate_drawdown(paper_closed),
            "memory_setups": memory.get("total_entries", 0),
            "audit_events": audit.get("total_logged", 0),
        },
    }