#!/usr/bin/env python3
"""Envia alerta setup_found de teste (n8n IA review + Telegram)."""

from __future__ import annotations

import json

from orb_agent.alerts.dispatcher import dispatch_alert
from orb_agent.alerts.payloads import build_setup_found_data


def _mock_result() -> dict:
    return {
        "setup_id": "test-orb-manual",
        "data_source": "ccxt",
        "exchange": "kraken",
        "setup": {
            "direction": "bullish",
            "confidence": 0.78,
            "or_high": 1.14580,
            "or_low": 1.14210,
            "metadata": {"breakout_mode": "retest", "retest_confirmed": True},
        },
        "trade_params": {
            "entry": 1.14520,
            "stop_loss": 1.14210,
            "take_profit": 1.14830,
            "risk_reward": 1.0,
            "position_size_lots": 0.10,
            "risk_percent": 1.0,
        },
        "confluences": {
            "strength": "moderate",
            "confluence_count": 2,
            "confluences": ["htf_bias_bullish", "or_breakout_retest"],
        },
        "backtest": {
            "total_trades": 15,
            "win_rate": 0.5,
            "profit_factor": 1.0,
            "meets_kpi": False,
        },
        "risk_check": {"approved": True},
        "explanation": (
            "EURUSD ORB bullish: teste manual setup_found. "
            "Nao e trade real — validar fluxo n8n + Telegram."
        ),
    }


def main() -> int:
    mock = _mock_result()
    data = build_setup_found_data("EURUSD", mock)
    result = dispatch_alert(
        "setup_found",
        "Setup ORB EURUSD (teste)",
        mock["explanation"],
        level="trade",
        data=data,
    )
    print(json.dumps(result, indent=2, default=str))
    return 0 if result.get("sent") else 1


if __name__ == "__main__":
    raise SystemExit(main())