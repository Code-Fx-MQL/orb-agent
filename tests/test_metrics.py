from orb_agent.metrics.collector import collect_metrics, estimate_drawdown
from orb_agent.paper.store import PaperStore


def test_estimate_drawdown():
    closed = [
        {"pnl_percent": 2.0},
        {"pnl_percent": -3.0},
        {"pnl_percent": -1.0},
    ]
    assert estimate_drawdown(closed) >= 3.0


def test_collect_metrics_includes_audit(tmp_path, monkeypatch):
    mem_dir = str(tmp_path / "mem")
    audit_dir = str(tmp_path / "audit")
    monkeypatch.setattr("orb_agent.memory.store.settings.memory_dir", mem_dir)
    monkeypatch.setattr("orb_agent.paper.store.settings.memory_dir", mem_dir)
    monkeypatch.setattr("orb_agent.audit.logger.settings.audit_dir", audit_dir)
    monkeypatch.setattr("orb_agent.paper.store._paper", None)
    monkeypatch.setattr("orb_agent.memory.store._memory", None)
    monkeypatch.setattr("orb_agent.audit.logger._audit", None)

    paper = PaperStore()
    paper.open_position("EURUSD", {
        "direction": "bullish", "entry": 1.10, "stop_loss": 1.09,
        "take_profit": 1.12, "risk_reward": 2, "position_size_lots": 0.1,
    })
    paper.check_exits("EURUSD", 1.12)

    metrics = collect_metrics()
    assert metrics["paper"]["closed_positions"] >= 1
    assert "audit" in metrics
    assert "kpis" in metrics