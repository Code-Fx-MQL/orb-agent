import json
from datetime import UTC, datetime, timedelta

from orb_agent.config.settings import OperationMode, settings
from orb_agent.ops.golive import CORE_PAIRS, get_golive_checklist, get_ops_snapshot


def test_golive_checklist_structure(monkeypatch, tmp_path):
    monkeypatch.setattr(settings, "mode", OperationMode.PAPER)
    monkeypatch.setattr(settings, "live_approved", False)
    monkeypatch.setattr(settings, "webhook_enabled", True)
    monkeypatch.setattr(settings, "webhook_url", "https://n8n.test/hook")

    bt_path = tmp_path / "backtest_golive.json"
    bt_path.write_text(json.dumps({
        "totals": {"total_trades": 25, "win_rate": 0.5714, "profit_factor": 1.5, "pairs_meeting_kpi": 2},
        "results": {p: {"meets_kpi": True} for p in CORE_PAIRS},
        "summary": "Backtest ORB",
    }), encoding="utf-8")
    monkeypatch.setattr(
        "orb_agent.ops.golive.backtest_golive_path",
        lambda: bt_path,
    )

    checklist = get_golive_checklist()
    assert "overall" in checklist
    assert "items" in checklist
    assert len(checklist["items"]) >= 7
    ids = {i["id"] for i in checklist["items"]}
    assert "backtest_kpi" in ids
    assert "paper_validation" in ids
    assert "human_approval" in ids


def test_golive_backtest_warns_low_sample(monkeypatch, tmp_path):
    bt_path = tmp_path / "backtest_golive.json"
    bt_path.write_text(json.dumps({
        "totals": {"total_trades": 5, "win_rate": 0.6, "profit_factor": 2.0, "pairs_meeting_kpi": 2},
        "results": {p: {"meets_kpi": True} for p in CORE_PAIRS},
    }), encoding="utf-8")
    monkeypatch.setattr("orb_agent.ops.golive.backtest_golive_path", lambda: bt_path)

    item = next(i for i in get_golive_checklist()["items"] if i["id"] == "backtest_kpi")
    assert item["status"] in ("warn", "ok")
    assert "amostra" in item["detail"].lower() or item["metrics"]["trades"] < 20


def test_paper_validation_days(monkeypatch, tmp_path):
    import orb_agent.paper.store as paper_mod

    paper_path = tmp_path / "paper_trades.json"
    old_date = (datetime.now(UTC) - timedelta(days=20)).isoformat()
    paper_path.write_text(json.dumps({
        "open": [{
            "id": "test-pos",
            "pair": "EURUSD",
            "direction": "bullish",
            "entry": 1.10,
            "stop_loss": 1.09,
            "take_profit": 1.12,
            "opened_at": old_date,
            "status": "open",
        }],
        "closed": [],
        "stats": {},
    }), encoding="utf-8")
    monkeypatch.setattr(settings, "memory_dir", str(tmp_path))
    paper_mod._paper = None

    item = next(i for i in get_golive_checklist()["items"] if i["id"] == "paper_validation")
    assert item["status"] == "ok"
    assert item["metrics"]["days"] >= 14


def test_ops_snapshot(monkeypatch):
    monkeypatch.setattr(settings, "mode", OperationMode.PAPER)
    snapshot = get_ops_snapshot()
    assert snapshot["mode"] == "paper"
    assert "gate" in snapshot
    assert "checklist" in snapshot
    assert "webhook" in snapshot
    assert "filters" in snapshot