"""Testes do pipeline com dados stub e stack sintetico."""

from orb_agent.config.settings import settings
from orb_agent.pipeline.analyze import run_pair_analysis
from orb_agent.tools.orb import evaluate_orb_setup


def _candle(open_: float, high: float, low: float, close: float) -> dict:
    return {"open": open_, "high": high, "low": low, "close": close}


def test_run_pair_analysis_stub_has_candles(monkeypatch):
    monkeypatch.setattr(settings, "data_source", "stub")
    result = run_pair_analysis("EURUSD")
    assert result["pair"] == "EURUSD"
    assert result["data_source"] == "stub"
    assert "found" in result
    assert "trade_params" in result


def test_run_pair_analysis_auto_mode_uses_stub_when_offline(monkeypatch):
    monkeypatch.setattr(settings, "data_source", "auto")

    def _fail_ccxt(*_args, **_kwargs):
        raise RuntimeError("offline")

    monkeypatch.setattr("orb_agent.tools.data._fetch_ccxt", _fail_ccxt)
    result = run_pair_analysis("EURUSD")
    assert result["data_source"] == "stub"
    assert "found" in result


def test_pipeline_full_stack_with_synthetic_setup(monkeypatch):
    htf = [_candle(100, 101, 99, 100), _candle(100, 106, 99.5, 105)]
    mtf = [_candle(102, 104, 102, 103)]
    ltf = [
        _candle(103, 103.8, 102.5, 103.5),
        _candle(103.5, 104.5, 103.4, 104.2),
        _candle(104.1, 104.3, 103.9, 104.15),
    ]

    from unittest.mock import MagicMock

    detection = evaluate_orb_setup("EURUSD", htf, mtf, ltf)
    mock_detect = MagicMock()
    mock_detect.invoke = MagicMock(return_value=detection)

    mock_fetch = MagicMock(
        return_value={
            "pair": "EURUSD",
            "source": "stub",
            "timeframes": {
                settings.default_htf: htf,
                settings.default_mtf: mtf,
                settings.default_ltf: ltf,
            },
        }
    )
    mock_fetch.invoke = mock_fetch

    monkeypatch.setattr("orb_agent.pipeline.analyze.detect_orb_setup", mock_detect)
    monkeypatch.setattr("orb_agent.pipeline.analyze.fetch_multi_tf_data", mock_fetch)

    result = run_pair_analysis("EURUSD")
    assert result["found"] is True
    assert result["trade_params"]["valid"] is True
    assert result["risk_check"]["approved"] is True
    assert result["confluences"]["strength"] in ("moderate", "strong")
    assert "Setup ORB" in result["explanation"]
    assert result.get("setup_id")
    assert result.get("backtest") is not None