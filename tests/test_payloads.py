from orb_agent.alerts.payloads import build_setup_found_data


def test_build_setup_found_data_enriched():
    data = build_setup_found_data("EURUSD", {
        "setup_id": "s1",
        "setup": {
            "direction": "bullish",
            "confidence": 0.77,
            "or_high": 1.11,
            "or_low": 1.09,
            "metadata": {},
        },
        "trade_params": {"entry": 1.10, "stop_loss": 1.09, "take_profit": 1.12, "risk_reward": 2.0},
        "confluences": {"strength": "strong", "confluence_count": 3, "confluences": ["bias"]},
        "backtest": {"total_trades": 5, "win_rate": 0.6, "meets_kpi": True},
        "risk_check": {"approved": True},
        "explanation": "Explicacao completa",
    })
    assert data["pair"] == "EURUSD"
    assert data["setup"]["or_high"] == 1.11
    assert data["backtest"]["meets_kpi"] is True
    assert data["explanation_full"] == "Explicacao completa"