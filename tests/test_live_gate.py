from orb_agent.config.settings import OperationMode, settings
from orb_agent.guardrails.live_gate import (
    is_live_trading_allowed,
    live_gate_status,
    set_live_session_token,
)


def test_live_blocked_without_approval(monkeypatch):
    monkeypatch.setattr(settings, "mode", OperationMode.LIVE)
    monkeypatch.setattr(settings, "live_approved", False)
    monkeypatch.setattr(settings, "live_approval_token", "secret")
    set_live_session_token("secret")
    allowed, reason = is_live_trading_allowed()
    assert allowed is False
    assert "aprovacao" in reason.lower() or "aprovação" in reason.lower()


def test_live_blocked_without_token(monkeypatch):
    monkeypatch.setattr(settings, "mode", OperationMode.LIVE)
    monkeypatch.setattr(settings, "live_approved", True)
    monkeypatch.setattr(settings, "live_approval_token", "secret")
    set_live_session_token(None)
    allowed, _ = is_live_trading_allowed()
    assert allowed is False


def test_live_allowed_with_full_gate(monkeypatch):
    monkeypatch.setattr(settings, "mode", OperationMode.LIVE)
    monkeypatch.setattr(settings, "live_approved", True)
    monkeypatch.setattr(settings, "live_approval_token", "secret-token")
    set_live_session_token("secret-token")
    allowed, reason = is_live_trading_allowed()
    assert allowed is True
    assert reason == "Live trading autorizado"


def test_live_gate_status(monkeypatch):
    monkeypatch.setattr(settings, "mode", OperationMode.ANALYSIS)
    status = live_gate_status()
    assert status["allowed"] is False
    assert status["mode"] == "analysis"