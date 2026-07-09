from orb_agent.memory.store import TradeMemory


def test_log_setup_and_outcome(tmp_path, monkeypatch):
    monkeypatch.setattr("orb_agent.memory.store.settings.memory_dir", str(tmp_path))
    mem = TradeMemory()
    setup = {"direction": "bullish", "confidence": 0.8}
    trade = {"entry": 1.1, "stop_loss": 1.09, "take_profit": 1.12}
    setup_id = mem.log_setup("EURUSD", setup, trade, {"win_rate": 0.6})
    assert len(setup_id) == 8
    updated = mem.log_outcome(setup_id, "win", 0.01)
    assert updated is not None
    assert updated["outcome"] == "win"