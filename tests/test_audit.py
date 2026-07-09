from orb_agent.audit.logger import AuditLogger


def test_audit_log_and_recent(tmp_path, monkeypatch):
    monkeypatch.setattr("orb_agent.audit.logger.settings.audit_dir", str(tmp_path))
    audit = AuditLogger()
    audit.log("risk_check", {"pair": "EURUSD", "approved": True})
    audit.log("setup_detected", {"pair": "EURUSD", "direction": "bullish"})

    recent = audit.recent(limit=5)
    assert len(recent) == 2
    assert recent[0]["event"] == "setup_detected"

    filtered = audit.recent(limit=5, event="risk_check")
    assert len(filtered) == 1
    assert filtered[0]["details"]["pair"] == "EURUSD"