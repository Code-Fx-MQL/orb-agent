from typing import Any

from langchain_core.tools import tool

from orb_agent.backtest.engine import run_orb_backtest_engine
from orb_agent.backtest.golive import save_backtest_golive
from orb_agent.config.settings import settings
from orb_agent.tools.data import fetch_backtest_multi_tf


def _run_backtest_for_pair(pair: str, candle_limit: int | None = None) -> dict[str, Any]:
    pair = pair.upper()
    limit = candle_limit or settings.backtest_candle_limit
    timeframes = [settings.default_htf, settings.default_mtf, settings.default_ltf]

    data = fetch_backtest_multi_tf(pair, timeframes, candle_limit=limit)
    htf = data["timeframes"][settings.default_htf]
    mtf = data["timeframes"][settings.default_mtf]
    ltf = data["timeframes"][settings.default_ltf]

    if not ltf:
        raise RuntimeError(f"Sem candles LTF para backtest de {pair}")

    result = run_orb_backtest_engine(pair, htf, mtf, ltf)
    result["data_source"] = data.get("source", "ccxt")
    result["candles_used"] = {
        settings.default_htf: len(htf),
        settings.default_mtf: len(mtf),
        settings.default_ltf: len(ltf),
    }
    if data.get("note"):
        result["data_note"] = data["note"]
    if data.get("exchange"):
        result["exchange"] = data["exchange"]
    return result


@tool
def run_orb_backtest(pair: str, candle_limit: int | None = None) -> dict:
    """Executa backtest ORB walk-forward com dados historicos."""
    return _run_backtest_for_pair(pair, candle_limit)


@tool
def run_backtest_all_pairs(
    pairs: list[str] | None = None,
    candle_limit: int | None = None,
    save_golive: bool = False,
) -> dict[str, Any]:
    """Backtest ORB em multiplos pares e agrega KPIs."""
    targets = [p.upper() for p in (pairs or settings.pairs_list)]
    limit = candle_limit or settings.backtest_candle_limit
    results: dict[str, Any] = {}
    totals = {
        "total_trades": 0,
        "wins": 0,
        "losses": 0,
        "gross_profit": 0.0,
        "gross_loss": 0.0,
        "pairs_meeting_kpi": 0,
    }

    for pair in targets:
        try:
            bt = _run_backtest_for_pair(pair, limit)
        except Exception as exc:
            bt = {
                "pair": pair,
                "error": str(exc),
                "total_trades": 0,
                "win_rate": 0.0,
                "profit_factor": 0.0,
                "avg_rr": 0.0,
                "max_drawdown": 0.0,
                "meets_kpi": False,
            }
        results[pair] = bt
        if bt.get("error"):
            continue
        totals["total_trades"] += int(bt.get("total_trades", 0))
        if bt.get("meets_kpi"):
            totals["pairs_meeting_kpi"] += 1
        totals["wins"] += int(bt.get("wins", 0))
        totals["losses"] += int(bt.get("losses", 0))
        for t in bt.get("trades_sample") or []:
            rr = float(t.get("rr_achieved", 0) or 0)
            if t.get("outcome") == "win":
                totals["gross_profit"] += max(rr, 0)
            elif t.get("outcome") == "loss":
                totals["gross_loss"] += abs(min(rr, 0))

    decided = totals["wins"] + totals["losses"]
    win_rate = totals["wins"] / decided if decided else 0.0
    profit_factor = (
        totals["gross_profit"] / totals["gross_loss"]
        if totals["gross_loss"] > 0
        else (totals["gross_profit"] if totals["gross_profit"] > 0 else 0.0)
    )

    payload = {
        "pairs": targets,
        "candle_limit": limit,
        "results": results,
        "totals": {
            **totals,
            "win_rate": round(win_rate, 4),
            "profit_factor": round(profit_factor, 2),
        },
        "summary": (
            f"Backtest ORB {len(targets)} pares · {totals['total_trades']} trades · "
            f"WR {win_rate:.1%} · PF {profit_factor:.2f} · "
            f"{totals['pairs_meeting_kpi']} par(es) com KPI"
        ),
    }
    if save_golive:
        save_backtest_golive(payload)
    return payload