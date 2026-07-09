"""Testes do pipeline com dados stub."""

from orb_agent.config.settings import settings
from orb_agent.pipeline.analyze import run_pair_analysis


def test_run_pair_analysis_stub_has_candles(monkeypatch):
    monkeypatch.setattr(settings, "data_source", "stub")
    result = run_pair_analysis("EURUSD")
    assert result["pair"] == "EURUSD"
    assert result["data_source"] == "stub"
    assert "detection" in result
    assert "found" in result["detection"]


def test_run_pair_analysis_auto_mode_uses_stub_when_offline(monkeypatch):
    monkeypatch.setattr(settings, "data_source", "auto")

    def _fail_ccxt(*_args, **_kwargs):
        raise RuntimeError("offline")

    monkeypatch.setattr("orb_agent.tools.data._fetch_ccxt", _fail_ccxt)
    result = run_pair_analysis("EURUSD")
    assert result["data_source"] == "stub"
    assert "detection" in result