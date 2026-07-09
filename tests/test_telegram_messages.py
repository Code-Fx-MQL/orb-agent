from orb_agent.alerts.telegram_messages import format_setup_found_message
from orb_agent.alerts.webhooks import _telegram_payload_for_event, send_telegram, telegram_status


def test_format_setup_found_message():
    msg = format_setup_found_message({
        "pair": "EURUSD",
        "setup_id": "s1",
        "direction": "bullish",
        "confidence": 0.85,
        "entry": 1.10,
        "stop_loss": 1.09,
        "take_profit": 1.12,
        "risk_reward": 2.0,
        "setup": {"or_high": 1.11, "or_low": 1.09},
        "confluences": {"strength": "strong", "confluence_count": 3},
        "backtest": {"meets_kpi": True},
        "data_source": "ccxt",
        "exchange": "kraken",
    })
    assert "EURUSD" in msg
    assert "strong" in msg
    assert "Backtest KPI" in msg


def test_telegram_payload_setup_found():
    text, mode = _telegram_payload_for_event(
        "setup_found",
        "title",
        "body",
        "trade",
        {"pair": "EURUSD", "setup_id": "x", "confidence": 0.7, "confluences": {}, "backtest": {}},
    )
    assert "EURUSD" in text
    assert mode == "HTML"


def test_telegram_disabled(monkeypatch):
    monkeypatch.setattr("orb_agent.alerts.webhooks.settings.telegram_enabled", False)
    result = send_telegram("test")
    assert result["sent"] is False
    assert "TELEGRAM_ENABLED" in result["reason"]


def test_telegram_status_ready(monkeypatch):
    monkeypatch.setattr("orb_agent.alerts.webhooks.settings.telegram_enabled", True)
    monkeypatch.setattr("orb_agent.alerts.webhooks.settings.telegram_bot_token", "token")
    monkeypatch.setattr("orb_agent.alerts.webhooks.settings.telegram_chat_id", "123")
    status = telegram_status()
    assert status["ready"] is True