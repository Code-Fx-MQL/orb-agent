"""Testes do engine de backtest ORB walk-forward."""

from orb_agent.backtest.engine import _simulate_trade, run_orb_backtest_engine
from orb_agent.models.schemas import SetupDirection
from orb_agent.tools.backtest import _run_backtest_for_pair


def _c(o: float, h: float, low_v: float, cl: float, ts: int) -> dict:
    return {"open": o, "high": h, "low": low_v, "close": cl, "volume": 100.0, "timestamp": ts}


def _build_orb_series(sessions: int = 12) -> tuple[list, list, list]:
    htf: list[dict] = []
    mtf: list[dict] = []
    ltf: list[dict] = []
    for s in range(sessions):
        day = 1_700_000_000_000 + s * 86_400_000
        scale = s * 0.01
        htf.append(_c(100 + scale, 101 + scale, 99 + scale, 100 + scale, day - 86_400_000))
        htf.append(_c(100 + scale, 106 + scale, 99.5 + scale, 105 + scale, day))
        or_h, or_l = 104 + scale, 102 + scale
        mtf.append(_c(102 + scale, or_h, or_l, 103 + scale, day))
        t0 = day
        ltf.extend(
            [
                _c(103 + scale, 103.8 + scale, 102.5 + scale, 103.5 + scale, t0 + 900_000),
                _c(103.5 + scale, 104.5 + scale, 103.4 + scale, 104.2 + scale, t0 + 1_800_000),
                _c(104.1 + scale, 104.3 + scale, 103.9 + scale, 104.15 + scale, t0 + 2_700_000),
                _c(104.15 + scale, 106.5 + scale, 104.0 + scale, 106.3 + scale, t0 + 3_600_000),
            ]
        )
    return htf, mtf, ltf


def test_simulate_trade_win():
    future = [
        _c(104.15, 106.5, 104.0, 106.0, 1),
        _c(106.0, 106.8, 105.9, 106.5, 2),
    ]
    result = _simulate_trade(future, SetupDirection.BULLISH, 104.15, 102.0, 106.3)
    assert result["outcome"] == "win"


def test_simulate_trade_loss():
    future = [_c(104.0, 104.2, 101.5, 102.0, 1)]
    result = _simulate_trade(future, SetupDirection.BULLISH, 104.15, 102.0, 106.3)
    assert result["outcome"] == "loss"


def test_backtest_engine_walk_forward():
    htf, mtf, ltf = _build_orb_series(sessions=15)
    result = run_orb_backtest_engine("EURUSD", htf, mtf, ltf)
    assert result["total_trades"] >= 1
    assert "win_rate" in result
    assert result["wins"] + result["losses"] >= 1


def test_run_backtest_for_pair_stub(monkeypatch):
    monkeypatch.setattr("orb_agent.config.settings.settings.data_source", "stub")
    monkeypatch.setattr("orb_agent.config.settings.settings.backtest_candle_limit", 120)
    result = _run_backtest_for_pair("EURUSD", candle_limit=120)
    assert result["pair"] == "EURUSD"
    assert "total_trades" in result
    assert result["data_source"] == "stub"