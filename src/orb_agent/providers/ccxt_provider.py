"""Provider OHLCV via CCXT."""

from __future__ import annotations

import time
from typing import Any

import ccxt
import structlog

from orb_agent.config.settings import settings
from orb_agent.providers.symbols import PairMarket, normalize_timeframe, resolve_pair_market

logger = structlog.get_logger(__name__)

_exchange_cache: dict[str, ccxt.Exchange] = {}
_CCXT_BATCH_SIZE = 720


def _get_exchange(exchange_id: str) -> ccxt.Exchange:
    if exchange_id not in _exchange_cache:
        exchange_class = getattr(ccxt, exchange_id)
        config: dict[str, Any] = {
            "enableRateLimit": True,
            "timeout": settings.ccxt_timeout_ms,
        }
        if settings.ccxt_api_key:
            config["apiKey"] = settings.ccxt_api_key
        if settings.ccxt_api_secret:
            config["secret"] = settings.ccxt_api_secret
        _exchange_cache[exchange_id] = exchange_class(config)
    return _exchange_cache[exchange_id]


def _is_valid_candle(open_: float, high: float, low: float, close: float) -> bool:
    if high < low or high - low <= 0:
        return False
    if open_ == high == low == close:
        return False
    return True


def ohlcv_to_candles(ohlcv: list[list[float]]) -> list[dict[str, Any]]:
    candles: list[dict[str, Any]] = []
    dropped = 0
    for row in ohlcv:
        ts, open_, high, low, close, *rest = row
        o, h, low_v, c = float(open_), float(high), float(low), float(close)
        if not _is_valid_candle(o, h, low_v, c):
            dropped += 1
            continue
        volume = rest[0] if rest else 0.0
        candles.append(
            {
                "timestamp": int(ts),
                "open": o,
                "high": h,
                "low": low_v,
                "close": c,
                "volume": float(volume),
            }
        )
    if dropped:
        logger.warning("ohlcv_dropped_invalid_candles", dropped=dropped, kept=len(candles))
    return candles


def _fetch_ohlcv_paginated(
    exchange: ccxt.Exchange,
    symbol: str,
    timeframe: str,
    total_limit: int,
) -> list[list[float]]:
    if total_limit <= _CCXT_BATCH_SIZE:
        return exchange.fetch_ohlcv(symbol, timeframe, limit=total_limit)

    tf_ms = exchange.parse_timeframe(timeframe) * 1000
    now = exchange.milliseconds()
    since = now - total_limit * tf_ms
    collected: list[list[float]] = []
    seen: set[int] = set()
    pause_s = max(2.0, (exchange.rateLimit or 2000) / 1000)

    while len(collected) < total_limit:
        batch_limit = min(_CCXT_BATCH_SIZE, total_limit - len(collected))
        for attempt in range(4):
            try:
                batch = exchange.fetch_ohlcv(symbol, timeframe, since=since, limit=batch_limit)
                break
            except ccxt.DDoSProtection:
                if attempt == 3:
                    raise
                time.sleep(pause_s * (attempt + 2))
        else:
            batch = []

        if not batch:
            if not collected:
                return exchange.fetch_ohlcv(symbol, timeframe, limit=total_limit) or []
            break

        new_rows = [row for row in batch if int(row[0]) not in seen]
        if not new_rows:
            break

        for row in new_rows:
            seen.add(int(row[0]))
        collected.extend(new_rows)
        since = int(collected[-1][0]) + tf_ms

        if len(new_rows) < batch_limit:
            break
        time.sleep(pause_s)

    collected.sort(key=lambda r: r[0])
    return collected[-total_limit:]


def fetch_ohlcv(
    pair: str,
    timeframe: str,
    limit: int | None = None,
) -> tuple[list[dict[str, Any]], PairMarket]:
    market = resolve_pair_market(pair)
    if market.stub_only:
        raise RuntimeError(f"Par {pair} configurado como stub_only")
    tf = normalize_timeframe(timeframe)
    limit = limit or settings.ccxt_ohlcv_limit

    exchange = _get_exchange(market.exchange_id)
    exchange.load_markets()

    logger.info(
        "fetch_ohlcv",
        pair=pair,
        exchange=market.exchange_id,
        symbol=market.symbol,
        timeframe=tf,
        limit=limit,
    )

    raw = _fetch_ohlcv_paginated(exchange, market.symbol, tf, limit)
    if not raw:
        raise RuntimeError(f"CCXT retornou OHLCV vazio para {pair} {tf}")

    return ohlcv_to_candles(raw), market


def fetch_multi_tf(
    pair: str,
    timeframes: list[str],
    limit: int | None = None,
) -> dict[str, Any]:
    market = resolve_pair_market(pair)
    result: dict[str, Any] = {
        "pair": pair.upper(),
        "source": "ccxt",
        "exchange": market.exchange_id,
        "symbol": market.symbol,
        "timeframes": {},
        "candle_counts": {},
    }
    if market.note:
        result["note"] = market.note

    for tf in timeframes:
        candles, _ = fetch_ohlcv(pair, tf, limit=limit)
        norm_tf = normalize_timeframe(tf)
        result["timeframes"][norm_tf] = candles
        result["candle_counts"][norm_tf] = len(candles)
        if limit and limit > _CCXT_BATCH_SIZE:
            time.sleep(3)

    return result