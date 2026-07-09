"""Testes da tool detect_orb_setup."""

from orb_agent.tools.orb import detect_orb_setup


def _candle(open_: float, high: float, low: float, close: float) -> dict:
    return {"open": open_, "high": high, "low": low, "close": close}


def _bullish_stack() -> tuple[list, list, list]:
    htf = [
        _candle(100, 101, 99, 100),
        _candle(100, 106, 99.5, 105),
    ]
    mtf = [_candle(102, 104, 102, 103), _candle(103, 105, 102.5, 104)]
    ltf = [
        _candle(103, 103.8, 102.5, 103.5),
        _candle(103.5, 104.5, 103.4, 104.2),
        _candle(104.1, 104.3, 103.9, 104.15),
    ]
    return htf, mtf, ltf


def test_detect_orb_setup_tool_bullish():
    htf, mtf, ltf = _bullish_stack()
    result = detect_orb_setup.invoke({
        "pair": "EURUSD",
        "htf_candles": htf,
        "mtf_candles": mtf,
        "ltf_candles": ltf,
        "htf_timeframe": "1d",
        "mtf_timeframe": "1h",
        "ltf_timeframe": "15m",
    })
    assert result["found"] is True
    assert result["setup"]["pair"] == "EURUSD"
    assert result["setup"]["direction"] == "bullish"
    assert result["setup"]["htf_timeframe"] == "1d"


def test_detect_orb_setup_tool_returns_reason_when_no_setup():
    result = detect_orb_setup.invoke({
        "pair": "XAUUSD",
        "htf_candles": [_candle(100, 101, 99, 100)],
        "mtf_candles": [],
        "ltf_candles": [],
    })
    assert result["found"] is False
    assert result.get("reason")