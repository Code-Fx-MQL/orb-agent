"""Metricas agregadas — memoria, paper, backtest."""

from __future__ import annotations

from typing import Any

from orb_agent.config.settings import settings
from orb_agent.memory.store import get_memory
from orb_agent.paper.store import get_paper_store


def _paper_drawdown(closed: list[dict[str, Any]]) -> float:
    cumulative = 0.0
    peak = 0.0
    max_dd = 0.0
    for pos in closed:
        cumulative += float(pos.get("pnl_percent", 0))
        peak = max(peak, cumulative)
        max_dd = max(max_dd, peak - cumulative)
    return round(max_dd, 4)


def collect_metrics() -> dict[str, Any]:
    memory = get_memory().summary()
    paper = get_paper_store().summary()
    paper_closed = get_paper_store().get_closed()

    paper_stats = paper.get("stats", {})
    paper_wr = 0.0
    if paper_stats:
        totals = sum(s.get("total", 0) for s in paper_stats.values())
        wins = sum(s.get("wins", 0) for s in paper_stats.values())
        paper_wr = round(wins / totals, 4) if totals else 0.0

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
            "max_drawdown_pct": _paper_drawdown(paper_closed),
            "by_pair": paper_stats,
        },
        "kpis": {
            "open_paper_positions": paper.get("open_positions", 0),
            "paper_win_rate": paper_wr,
            "paper_max_drawdown_pct": _paper_drawdown(paper_closed),
            "memory_setups": memory.get("total_entries", 0),
        },
    }