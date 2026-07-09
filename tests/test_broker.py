from orb_agent.broker.executor import BrokerExecutor
from orb_agent.config.settings import OperationMode, settings
from orb_agent.guardrails.live_gate import set_live_session_token


def _trade_params() -> dict:
    return {
        "direction": "bullish",
        "entry": 1.10,
        "stop_loss": 1.09,
        "take_profit": 1.12,
        "risk_reward": 2.0,
        "position_size_lots": 0.01,
        "risk_percent": 0.01,
    }


def test_broker_blocked_without_gate(monkeypatch, tmp_path):
    monkeypatch.setattr(settings, "mode", OperationMode.LIVE)
    monkeypatch.setattr(settings, "live_approved", False)
    monkeypatch.setattr("orb_agent.audit.logger.settings.audit_dir", str(tmp_path))
    set_live_session_token(None)

    result = BrokerExecutor().place_order("EURUSD", _trade_params(), setup_id="abc")
    assert result["placed"] is False
    assert "aprovacao" in result["reason"].lower() or "aprovação" in result["reason"].lower()


def test_broker_stub_order(monkeypatch, tmp_path):
    monkeypatch.setattr(settings, "mode", OperationMode.LIVE)
    monkeypatch.setattr(settings, "live_approved", True)
    monkeypatch.setattr(settings, "live_approval_token", "tok123")
    monkeypatch.setattr(settings, "broker_mode", "stub")
    monkeypatch.setattr("orb_agent.audit.logger.settings.audit_dir", str(tmp_path))
    set_live_session_token("tok123")

    result = BrokerExecutor().place_order("EURUSD", _trade_params(), setup_id="abc")
    assert result["placed"] is True
    assert result["stub"] is True
    assert result["order_id"].startswith("stub-")