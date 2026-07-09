"""Serializacao de payloads para webhooks n8n."""

from __future__ import annotations

from typing import Any


def _backtest_summary(backtest: dict[str, Any] | None) -> dict[str, Any] | None:
    if not backtest:
        return None
    return {
        "total_trades": backtest.get("total_trades", 0),
        "win_rate": backtest.get("win_rate"),
        "profit_factor": backtest.get("profit_factor"),
        "avg_rr": backtest.get("avg_rr"),
        "max_drawdown": backtest.get("max_drawdown"),
        "meets_kpi": backtest.get("meets_kpi", False),
        "notes": backtest.get("notes"),
        "data_source": backtest.get("data_source"),
        "exchange": backtest.get("exchange"),
    }


def _confluences_summary(confluences: dict[str, Any] | None) -> dict[str, Any] | None:
    if not confluences:
        return None
    return {
        "strength": confluences.get("strength"),
        "confluence_count": confluences.get("confluence_count"),
        "confidence_boost": confluences.get("confidence_boost"),
        "confluences": confluences.get("confluences", []),
    }


def _setup_summary(setup: dict[str, Any] | None) -> dict[str, Any] | None:
    if not setup:
        return None
    meta = setup.get("metadata") or {}
    return {
        "direction": setup.get("direction"),
        "confidence": setup.get("confidence"),
        "or_high": setup.get("or_high"),
        "or_low": setup.get("or_low"),
        "entry": setup.get("entry"),
        "stop_loss": setup.get("stop_loss"),
        "take_profit": setup.get("take_profit"),
        "htf_timeframe": setup.get("htf_timeframe"),
        "mtf_timeframe": setup.get("mtf_timeframe"),
        "ltf_timeframe": setup.get("ltf_timeframe"),
        "breakout_mode": meta.get("breakout_mode"),
        "retest_confirmed": meta.get("retest_confirmed"),
    }


def build_setup_found_data(pair: str, result: dict[str, Any]) -> dict[str, Any]:
    """Payload enriquecido para IA no n8n (event_type=setup_found)."""
    trade = result.get("trade_params") or {}
    setup = result.get("setup") or {}
    risk = result.get("risk_check") or {}

    return {
        "pair": pair,
        "setup_id": result.get("setup_id"),
        "direction": setup.get("direction"),
        "confidence": setup.get("confidence"),
        "entry": trade.get("entry"),
        "stop_loss": trade.get("stop_loss"),
        "take_profit": trade.get("take_profit"),
        "risk_reward": trade.get("risk_reward"),
        "position_size_lots": trade.get("position_size_lots"),
        "risk_percent": trade.get("risk_percent"),
        "data_source": result.get("data_source"),
        "exchange": result.get("exchange"),
        "setup": _setup_summary(setup),
        "confluences": _confluences_summary(result.get("confluences")),
        "backtest": _backtest_summary(result.get("backtest")),
        "risk_check": {
            "approved": risk.get("approved", risk.get("allowed")),
            "reason": risk.get("reason"),
        },
        "explanation_full": result.get("explanation"),
    }