from typing import Any, Literal

import pandas as pd
import structlog
from langchain_core.tools import tool

from orb_agent.config.settings import settings
from orb_agent.providers.symbols import (
    is_index_pair,
    normalize_timeframe,
    resolve_pair_market,
    stub_base_price,
)

logger = structlog.get_logger(__name__)

_STUB_TF_FREQ: dict[str, str] = {
    "1m": "1min",
    "5m": "5min",
    "15m": "15min",
    "1h": "1h",
    "4h": "4h",
    "1d": "1D",
}


def _stub_tick(pair: str, base: float) -> float:
    p = pair.upper()
    if "XAU" in p:
        return 0.10
    if is_index_pair(p) or base >= 1000:
        return max(base * 0.0001, 1.0)
    if "JPY" in p:
        return 0.01
    return 0.0001


def _generate_stub_candles(
    pair: str,
    periods: int = 100,
    timeframe: str = "15m",
) -> list[dict[str, Any]]:
    norm = normalize_timeframe(timeframe)
    freq = _STUB_TF_FREQ.get(norm, "15min")
    idx = pd.date_range(end=pd.Timestamp.now("UTC"), periods=periods, freq=freq)
    base = stub_base_price(pair)
    tick = _stub_tick(pair, base)
    noise = pd.Series(range(periods)) * tick
    df = pd.DataFrame(
        {
            "open": base + noise,
            "high": base + noise + tick * 10,
            "low": base + noise - tick * 10,
            "close": base + noise + tick * 5,
            "volume": [1000.0] * periods,
        },
        index=idx,
    )
    records = df.reset_index(names="timestamp").to_dict(orient="records")
    for row in records:
        ts = row.pop("timestamp")
        row["timestamp"] = int(pd.Timestamp(ts).timestamp() * 1000)
    return records


def _fetch_stub(
    pair: str,
    timeframes: list[str],
    candle_limit: int | None = None,
) -> dict[str, Any]:
    result: dict[str, Any] = {
        "pair": pair.upper(),
        "source": "stub",
        "timeframes": {},
        "candle_counts": {},
        "note": "Dados simulados — ORB_DATA_SOURCE=stub",
    }
    periods = candle_limit or settings.ccxt_ohlcv_limit
    for tf in timeframes:
        norm = normalize_timeframe(tf)
        candles = _generate_stub_candles(pair, periods=periods, timeframe=norm)
        result["timeframes"][norm] = candles
        result["candle_counts"][norm] = len(candles)
    return result


def _fetch_ccxt(pair: str, timeframes: list[str]) -> dict[str, Any]:
    from orb_agent.providers.ccxt_provider import fetch_multi_tf

    return fetch_multi_tf(pair, timeframes, limit=settings.ccxt_ohlcv_limit)


@tool
def fetch_multi_tf_data(
    pair: str,
    timeframes: list[str],
    source: Literal["auto", "ccxt", "stub"] | None = None,
) -> dict[str, Any]:
    """Busca OHLCV multi-timeframe para analise ORB.

    Args:
        pair: Par (EURUSD, XAUUSD, etc.).
        timeframes: Lista de TFs (ex: ["1d", "1h", "15m"]).
        source: auto (CCXT com fallback stub), ccxt (real), stub (simulado).
    """
    mode = source or settings.data_source
    market = resolve_pair_market(pair)

    if market.stub_only or mode == "stub":
        result = _fetch_stub(pair, timeframes, candle_limit=settings.ccxt_ohlcv_limit)
        if market.stub_only:
            result["note"] = market.note or "Dados simulados — par sem feed CCXT"
        return result

    if mode == "ccxt":
        return _fetch_ccxt(pair, timeframes)

    try:
        return _fetch_ccxt(pair, timeframes)
    except Exception as exc:
        logger.warning("ccxt_fallback_stub", pair=pair, error=str(exc))
        result = _fetch_stub(pair, timeframes)
        result["fallback_reason"] = str(exc)
        result["note"] = f"Fallback stub apos falha CCXT: {exc}"
        return result