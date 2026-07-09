from typing import Any

from langchain_core.tools import tool

from orb_agent.config.orb_rules import (
    DEFAULT_BREAKOUT_MODE,
    LTF_LOOKBACK,
    MIN_OR_RANGE_FOREX,
    MIN_OR_RANGE_GOLD,
    MIN_RISK_REWARD,
    MIN_SETUP_CONFIDENCE,
    ORB_SESSION_CANDLES,
    REQUIRE_RETEST,
    RETEST_TOLERANCE_RATIO,
    BreakoutMode,
)
from orb_agent.config.settings import settings
from orb_agent.models.schemas import ORBSetup, SetupDirection


def _min_range_ok(pair: str, or_high: float, or_low: float) -> bool:
    size = or_high - or_low
    if "XAU" in pair.upper():
        return size >= MIN_OR_RANGE_GOLD
    return size >= MIN_OR_RANGE_FOREX


def compute_daily_bias(htf_candles: list[dict[str, Any]]) -> SetupDirection | None:
    """HTF (1D): bias pelo fecho vs abertura e continuacao do movimento."""
    if len(htf_candles) < 2:
        return None

    last = htf_candles[-1]
    prev = htf_candles[-2]
    last_close = float(last["close"])
    last_open = float(last["open"])
    prev_close = float(prev["close"])

    if last_close > last_open and last_close > prev_close:
        return SetupDirection.BULLISH
    if last_close < last_open and last_close < prev_close:
        return SetupDirection.BEARISH
    return None


def compute_opening_range(
    mtf_candles: list[dict[str, Any]],
    pair: str,
    session_candles: int = ORB_SESSION_CANDLES,
) -> dict[str, Any] | None:
    """MTF (1H): high/low da primeira hora (N velas) da sessao."""
    if len(mtf_candles) < session_candles:
        return None

    session = mtf_candles[:session_candles]
    or_high = max(float(c["high"]) for c in session)
    or_low = min(float(c["low"]) for c in session)

    if or_high <= or_low:
        return None
    if not _min_range_ok(pair, or_high, or_low):
        return None

    return {
        "or_high": or_high,
        "or_low": or_low,
        "range_size": or_high - or_low,
        "session_candles": session_candles,
    }


def _retest_tolerance(or_high: float, or_low: float) -> float:
    return (or_high - or_low) * RETEST_TOLERANCE_RATIO


def find_ltf_entry(
    ltf_candles: list[dict[str, Any]],
    or_high: float,
    or_low: float,
    direction: SetupDirection,
    *,
    require_retest: bool = REQUIRE_RETEST,
    breakout_mode: BreakoutMode = DEFAULT_BREAKOUT_MODE,
) -> dict[str, Any] | None:
    """LTF (15m): breakout do OR + reteste opcional ao boundary."""
    if len(ltf_candles) < 2:
        return None

    window = ltf_candles[-LTF_LOOKBACK:] if len(ltf_candles) > LTF_LOOKBACK else ltf_candles
    tolerance = _retest_tolerance(or_high, or_low)
    use_retest = require_retest and breakout_mode == BreakoutMode.RETEST

    if direction == SetupDirection.BULLISH:
        breakout_idx = None
        for i, candle in enumerate(window):
            if float(candle["close"]) > or_high:
                breakout_idx = i
                break
        if breakout_idx is None:
            return None

        if not use_retest:
            c = window[breakout_idx]
            return {
                "entry": float(c["close"]),
                "breakout_level": or_high,
                "stop_reference": or_low,
                "pattern": "immediate_breakout",
                "confidence": 0.62,
            }

        for j in range(breakout_idx + 1, len(window)):
            c = window[j]
            low = float(c["low"])
            close = float(c["close"])
            if low <= or_high + tolerance and close > or_high:
                return {
                    "entry": close,
                    "breakout_level": or_high,
                    "stop_reference": or_low,
                    "pattern": "breakout_retest",
                    "confidence": 0.74,
                }
        return None

    breakout_idx = None
    for i, candle in enumerate(window):
        if float(candle["close"]) < or_low:
            breakout_idx = i
            break
    if breakout_idx is None:
        return None

    if not use_retest:
        c = window[breakout_idx]
        return {
            "entry": float(c["close"]),
            "breakout_level": or_low,
            "stop_reference": or_high,
            "pattern": "immediate_breakout",
            "confidence": 0.62,
        }

    for j in range(breakout_idx + 1, len(window)):
        c = window[j]
        high = float(c["high"])
        close = float(c["close"])
        if high >= or_low - tolerance and close < or_low:
            return {
                "entry": close,
                "breakout_level": or_low,
                "stop_reference": or_high,
                "pattern": "breakout_retest",
                "confidence": 0.74,
            }
    return None


def _trade_levels(
    direction: SetupDirection,
    entry: float,
    or_high: float,
    or_low: float,
) -> tuple[float, float] | None:
    if direction == SetupDirection.BULLISH:
        sl = or_low
        risk = entry - sl
        if risk <= 0:
            return None
        tp = entry + risk * MIN_RISK_REWARD
        return sl, tp

    sl = or_high
    risk = sl - entry
    if risk <= 0:
        return None
    tp = entry - risk * MIN_RISK_REWARD
    return sl, tp


def _bias_confidence_boost(htf_candles: list[dict[str, Any]]) -> float:
    last = htf_candles[-1]
    body = abs(float(last["close"]) - float(last["open"]))
    full_range = float(last["high"]) - float(last["low"])
    if full_range <= 0:
        return 0.0
    if body / full_range >= 0.5:
        return 0.08
    return 0.0


def evaluate_orb_setup(
    pair: str,
    htf_candles: list[dict[str, Any]],
    mtf_candles: list[dict[str, Any]],
    ltf_candles: list[dict[str, Any]],
    *,
    htf_timeframe: str = "1d",
    mtf_timeframe: str = "1h",
    ltf_timeframe: str = "15m",
    session_candles: int = ORB_SESSION_CANDLES,
    require_retest: bool = REQUIRE_RETEST,
    breakout_mode: BreakoutMode = DEFAULT_BREAKOUT_MODE,
) -> dict[str, Any]:
    """Avalia setup ORB top-down: 1D bias -> 1H OR -> 15m entrada."""
    pair = pair.upper()

    bias = compute_daily_bias(htf_candles)
    if bias is None:
        return {
            "found": False,
            "pair": pair,
            "reason": "Sem bias diario claro (HTF neutro)",
        }

    opening = compute_opening_range(mtf_candles, pair, session_candles)
    if opening is None:
        return {
            "found": False,
            "pair": pair,
            "reason": "Opening Range invalido ou range demasiado pequeno no MTF",
            "htf_direction": bias.value,
        }

    or_high = opening["or_high"]
    or_low = opening["or_low"]

    entry_signal = find_ltf_entry(
        ltf_candles,
        or_high,
        or_low,
        bias,
        require_retest=require_retest,
        breakout_mode=breakout_mode,
    )
    if entry_signal is None:
        waiting = (
            "Aguardar reteste LTF apos breakout do OR"
            if require_retest and breakout_mode == BreakoutMode.RETEST
            else "Aguardar breakout LTF do Opening Range"
        )
        return {
            "found": False,
            "pair": pair,
            "reason": waiting,
            "htf_direction": bias.value,
            "or_high": or_high,
            "or_low": or_low,
        }

    levels = _trade_levels(bias, entry_signal["entry"], or_high, or_low)
    if levels is None:
        return {
            "found": False,
            "pair": pair,
            "reason": "Parametros de trade invalidos (R:R ou entry/SL)",
            "htf_direction": bias.value,
        }

    sl, tp = levels
    confidence = min(
        0.95,
        entry_signal["confidence"] + _bias_confidence_boost(htf_candles),
    )
    if confidence < MIN_SETUP_CONFIDENCE:
        return {
            "found": False,
            "pair": pair,
            "reason": f"Confianca abaixo do minimo ({MIN_SETUP_CONFIDENCE})",
        }

    setup = ORBSetup(
        pair=pair,
        direction=bias,
        htf_timeframe=htf_timeframe,
        mtf_timeframe=mtf_timeframe,
        ltf_timeframe=ltf_timeframe,
        or_high=or_high,
        or_low=or_low,
        entry=entry_signal["entry"],
        stop_loss=sl,
        take_profit=tp,
        confidence=round(confidence, 3),
        metadata={
            "pattern": entry_signal["pattern"],
            "breakout_level": entry_signal["breakout_level"],
            "top_down": f"{htf_timeframe}->{mtf_timeframe}->{ltf_timeframe}",
            "session_candles": session_candles,
            "breakout_mode": breakout_mode.value,
            "require_retest": require_retest,
        },
    )

    return {"found": True, "pair": pair, "setup": setup.model_dump(mode="json")}


@tool
def detect_orb_setup(
    pair: str,
    htf_candles: list,
    mtf_candles: list,
    ltf_candles: list,
    htf_timeframe: str = "1d",
    mtf_timeframe: str = "1h",
    ltf_timeframe: str = "15m",
    breakout_mode: str | None = None,
    require_retest: bool | None = None,
) -> dict:
    """Detecta setup ORB com top-down 1D -> 1H -> 15m.

    1. HTF: bias direcional do dia
    2. MTF: Opening Range (primeira hora)
    3. LTF: breakout + reteste do boundary
    """
    mode = BreakoutMode(breakout_mode or settings.orb_breakout_mode)
    retest = settings.orb_require_retest if require_retest is None else require_retest

    return evaluate_orb_setup(
        pair,
        htf_candles,
        mtf_candles,
        ltf_candles,
        htf_timeframe=htf_timeframe,
        mtf_timeframe=mtf_timeframe,
        ltf_timeframe=ltf_timeframe,
        session_candles=settings.orb_session_candles,
        require_retest=retest,
        breakout_mode=mode,
    )