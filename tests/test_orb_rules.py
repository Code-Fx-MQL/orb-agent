"""Testes unitarios das regras ORB (funcoes puras)."""

from orb_agent.config.orb_rules import BreakoutMode
from orb_agent.models.schemas import SetupDirection
from orb_agent.tools.orb import (
    compute_daily_bias,
    compute_opening_range,
    evaluate_orb_setup,
    find_ltf_entry,
)


def _candle(open_: float, high: float, low: float, close: float) -> dict:
    return {"open": open_, "high": high, "low": low, "close": close}


def test_compute_daily_bias_bullish():
    htf = [
        _candle(100, 101, 99, 100),
        _candle(100, 106, 99.5, 105),
    ]
    assert compute_daily_bias(htf) == SetupDirection.BULLISH


def test_compute_daily_bias_bearish():
    htf = [
        _candle(105, 106, 104, 105),
        _candle(105, 105.5, 99, 100),
    ]
    assert compute_daily_bias(htf) == SetupDirection.BEARISH


def test_compute_daily_bias_neutral():
    htf = [
        _candle(100, 101, 99, 100),
        _candle(100.5, 101, 99, 100),
    ]
    assert compute_daily_bias(htf) is None


def test_compute_opening_range_from_first_hour():
    mtf = [
        _candle(102, 104, 102, 103),
        _candle(103, 105, 102.5, 104),
    ]
    opening = compute_opening_range(mtf, "EURUSD", session_candles=1)
    assert opening is not None
    assert opening["or_high"] == 104
    assert opening["or_low"] == 102


def test_find_ltf_entry_bullish_breakout_retest():
    ltf = [
        _candle(103, 103.8, 102.5, 103.5),
        _candle(103.5, 104.5, 103.4, 104.2),
        _candle(104.1, 104.3, 103.9, 104.15),
    ]
    entry = find_ltf_entry(ltf, or_high=104.0, or_low=102.0, direction=SetupDirection.BULLISH)
    assert entry is not None
    assert entry["pattern"] == "breakout_retest"
    assert entry["entry"] == 104.15


def test_find_ltf_entry_bearish_breakout_retest():
    ltf = [
        _candle(107, 107.5, 106.5, 107),
        _candle(107, 107.2, 105.5, 105.8),
        _candle(106, 106.3, 105.7, 105.9),
    ]
    entry = find_ltf_entry(ltf, or_high=108.0, or_low=106.0, direction=SetupDirection.BEARISH)
    assert entry is not None
    assert entry["pattern"] == "breakout_retest"


def test_evaluate_orb_setup_full_bullish_stack():
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
    result = evaluate_orb_setup("EURUSD", htf, mtf, ltf)
    assert result["found"] is True
    setup = result["setup"]
    assert setup["direction"] == "bullish"
    assert setup["or_high"] == 104
    assert setup["or_low"] == 102
    assert setup["entry"] == 104.15
    assert setup["stop_loss"] == 102
    assert setup["confidence"] >= 0.5


def test_evaluate_orb_setup_rejects_misaligned_ltf():
    htf = [
        _candle(100, 101, 99, 100),
        _candle(100, 106, 99.5, 105),
    ]
    mtf = [_candle(102, 104, 102, 103)]
    ltf = [_candle(103, 103.5, 102.8, 103.2)]
    result = evaluate_orb_setup("EURUSD", htf, mtf, ltf)
    assert result["found"] is False
    assert "Aguardar" in result["reason"]


def test_immediate_breakout_mode():
    htf = [
        _candle(100, 101, 99, 100),
        _candle(100, 106, 99.5, 105),
    ]
    mtf = [_candle(102, 104, 102, 103)]
    ltf = [
        _candle(103, 103.8, 102.5, 103.5),
        _candle(103.5, 104.5, 103.4, 104.2),
    ]
    result = evaluate_orb_setup(
        "EURUSD",
        htf,
        mtf,
        ltf,
        require_retest=False,
        breakout_mode=BreakoutMode.IMMEDIATE,
    )
    assert result["found"] is True
    assert result["setup"]["metadata"]["pattern"] == "immediate_breakout"