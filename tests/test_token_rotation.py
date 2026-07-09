from orb_agent.guardrails.token_rotation import generate_live_token, rotate_live_token


def test_generate_token():
    token = generate_live_token()
    assert len(token) >= 20


def test_rotate_token_force(tmp_path, monkeypatch):
    env_file = tmp_path / ".env"
    env_file.write_text("ORB_MODE=live\nORB_LIVE_APPROVAL_TOKEN=old-token\n", encoding="utf-8")
    monkeypatch.setattr("orb_agent.guardrails.token_rotation.settings.live_approval_token", "old-token")
    monkeypatch.setattr("orb_agent.guardrails.token_rotation.settings.audit_dir", str(tmp_path))

    result = rotate_live_token(current_token="old-token", env_path=env_file)
    assert result["rotated"] is True
    assert "ORB_LIVE_APPROVAL_TOKEN=" in env_file.read_text(encoding="utf-8")
    assert result["new_token"] != "old-token"


def test_rotate_token_wrong_current(tmp_path, monkeypatch):
    env_file = tmp_path / ".env"
    env_file.write_text("ORB_LIVE_APPROVAL_TOKEN=secret\n", encoding="utf-8")
    monkeypatch.setattr("orb_agent.guardrails.token_rotation.settings.live_approval_token", "secret")

    result = rotate_live_token(current_token="wrong", env_path=env_file)
    assert result["rotated"] is False