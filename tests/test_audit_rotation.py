from orb_agent.audit.rotation import maybe_rotate_audit_log


def test_rotate_when_over_limit(tmp_path, monkeypatch):
    audit_dir = tmp_path / "audit"
    audit_dir.mkdir()
    log_path = audit_dir / "trade_audit.jsonl"
    log_path.write_text("x" * (1024 * 1024 * 2), encoding="utf-8")

    monkeypatch.setattr("orb_agent.audit.rotation.settings.audit_dir", str(audit_dir))
    monkeypatch.setattr("orb_agent.audit.rotation.settings.audit_max_mb", 1.0)

    result = maybe_rotate_audit_log()
    assert result["rotated"] is True
    assert not log_path.exists()
    assert list((audit_dir / "archive").glob("*.jsonl"))


def test_no_rotate_under_limit(tmp_path, monkeypatch):
    audit_dir = tmp_path / "audit"
    audit_dir.mkdir()
    log_path = audit_dir / "trade_audit.jsonl"
    log_path.write_text('{"event":"test"}\n', encoding="utf-8")

    monkeypatch.setattr("orb_agent.audit.rotation.settings.audit_dir", str(audit_dir))
    monkeypatch.setattr("orb_agent.audit.rotation.settings.audit_max_mb", 50.0)

    result = maybe_rotate_audit_log()
    assert result["rotated"] is False
    assert log_path.exists()