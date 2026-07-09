from orb_agent.memory.mem0_sync import Mem0Sync, get_mem0_sync, reset_mem0_sync


def test_mem0_unavailable_without_package(monkeypatch):
    monkeypatch.setattr("orb_agent.memory.mem0_sync.settings.mem0_enabled", True)
    monkeypatch.setattr("orb_agent.memory.mem0_sync.settings.mem0_api_key", "test-key")
    reset_mem0_sync()
    client = get_mem0_sync()
    assert client is None


def test_mem0_sync_setup_returns_reason_when_unavailable():
    sync = Mem0Sync("fake-key", "orb-agent")
    result = sync.sync_setup({"pair": "EURUSD", "id": "abc"})
    assert result["synced"] is False