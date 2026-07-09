"""Testes de calculate_trade_params e confluencias ORB."""

from orb_agent.tools.orb import evaluate_orb_setup
from orb_agent.tools.trade import build_trade_params, identify_confluences


def _candle(open_: float, high: float, low: float, close: float) -> dict:
    return {"open": open_, "high": high, "low": low, "close": close}


def _bullish_setup() -> dict:
    htf = [_candle(100, 101, 99, 100), _candle(100, 106, 99.5, 105)]
    mtf = [_candle(102, 104, 102, 103)]
    ltf = [
        _candle(103, 103.8, 102.5, 103.5),
        _candle(103.5, 104.5, 103.4, 104.2),
        _candle(104.1, 104.3, 103.9, 104.15),
    ]
    result = evaluate_orb_setup("EURUSD", htf, mtf, ltf)
    assert result["found"]
    return result["setup"]


def test_calculate_trade_params_valid():
    setup = _bullish_setup()
    trade = build_trade_params(setup, account_balance=10_000, risk_percent=0.01)
    assert trade["valid"] is True
    assert trade["entry"] == setup["entry"]
    assert trade["risk_reward"] >= 1.0
    assert trade["position_size_lots"] > 0


def test_calculate_trade_params_rejects_bad_rr():
    setup = _bullish_setup()
    setup["take_profit"] = setup["entry"] + 0.01
    trade = build_trade_params(setup)
    assert trade["valid"] is False
    assert "R:R" in trade["reason"]


def test_identify_confluences():
    setup = _bullish_setup()
    conf = identify_confluences.invoke({"setup": setup})
    assert conf["confluence_count"] >= 3
    assert "breakout_com_reteste" in conf["confluences"]