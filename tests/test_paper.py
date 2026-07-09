from orb_agent.config.settings import OperationMode
from orb_agent.paper.store import PaperStore


def test_open_and_close_position(tmp_path, monkeypatch):
    monkeypatch.setattr("orb_agent.paper.store.settings.memory_dir", str(tmp_path))
    store = PaperStore()
    trade = {
        "direction": "bullish",
        "entry": 1.10,
        "stop_loss": 1.09,
        "take_profit": 1.12,
        "risk_reward": 2.0,
        "position_size_lots": 0.1,
    }
    opened = store.open_position("EURUSD", trade, setup_id="abc")
    assert opened["opened"] is True

    closed = store.check_exits("EURUSD", 1.12)
    assert len(closed) == 1
    assert closed[0]["outcome"] == "win"


def test_pipeline_opens_paper_in_paper_mode(monkeypatch):
    from unittest.mock import MagicMock

    from orb_agent.pipeline import analyze as pipeline_mod

    detection = {
        "found": True,
        "setup": {
            "pair": "EURUSD",
            "direction": "bullish",
            "or_high": 1.11,
            "or_low": 1.09,
            "entry": 1.105,
            "stop_loss": 1.09,
            "take_profit": 1.12,
            "confidence": 0.8,
            "metadata": {},
        },
    }
    mock_detect = MagicMock()
    mock_detect.invoke = MagicMock(return_value=detection)
    mock_fetch = MagicMock()
    mock_fetch.invoke = MagicMock(return_value={
        "source": "stub",
        "timeframes": {"1d": [], "1h": [], "15m": [{"close": 1.10, "timestamp": 1}]},
    })
    mock_bt = MagicMock()
    mock_bt.invoke = MagicMock(return_value={"total_trades": 0, "win_rate": 0})

    monkeypatch.setattr(pipeline_mod, "detect_orb_setup", mock_detect)
    monkeypatch.setattr(pipeline_mod, "fetch_multi_tf_data", mock_fetch)
    monkeypatch.setattr(pipeline_mod, "run_orb_backtest", mock_bt)
    monkeypatch.setattr(pipeline_mod.settings, "mode", OperationMode.PAPER)

    result = pipeline_mod.run_pair_analysis("EURUSD")
    assert result.get("paper_trade", {}).get("opened") is True