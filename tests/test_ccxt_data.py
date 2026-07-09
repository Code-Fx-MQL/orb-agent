"""Testes do provider CCXT e fetch_multi_tf_data."""

import pytest

from orb_agent.config.settings import settings
from orb_agent.providers.ccxt_provider import ohlcv_to_candles
from orb_agent.providers.symbols import PRIMARY_PAIRS, resolve_pair_market
from orb_agent.tools.data import fetch_multi_tf_data


def test_primary_pairs_constant():
    assert "EURUSD" in PRIMARY_PAIRS
    assert "XAUUSD" in PRIMARY_PAIRS


def test_pair_market_mapping():
    eur = resolve_pair_market("EURUSD")
    assert eur.exchange_id == "kraken"
    assert eur.symbol == "EUR/USD"

    xau = resolve_pair_market("XAUUSD")
    assert xau.exchange_id == "kraken"
    assert xau.symbol == "XAUT/USD"

    gbpjpy = resolve_pair_market("GBPJPY")
    assert gbpjpy.stub_only is True


def test_ohlcv_to_candles():
    raw = [[1700000000000, 1.08, 1.09, 1.07, 1.085, 1000.0]]
    candles = ohlcv_to_candles(raw)
    assert len(candles) == 1
    assert candles[0]["close"] == 1.085
    assert candles[0]["timestamp"] == 1700000000000


def test_ohlcv_drops_flat_candles():
    raw = [
        [1700000000000, 1.08, 1.08, 1.08, 1.08, 0.0],
        [1700003600000, 1.08, 1.09, 1.07, 1.085, 1000.0],
    ]
    candles = ohlcv_to_candles(raw)
    assert len(candles) == 1


def test_fetch_stub_mode_orb_timeframes():
    result = fetch_multi_tf_data.invoke(
        {"pair": "EURUSD", "timeframes": ["1d", "1h", "15m"], "source": "stub"}
    )
    assert result["source"] == "stub"
    assert result["candle_counts"]["1d"] == settings.ccxt_ohlcv_limit
    assert result["candle_counts"]["1h"] == settings.ccxt_ohlcv_limit
    candle = result["timeframes"]["15m"][-1]
    assert all(k in candle for k in ("open", "high", "low", "close", "timestamp"))


def test_fetch_stub_only_pair():
    result = fetch_multi_tf_data.invoke(
        {"pair": "GBPJPY", "timeframes": ["1d", "1h", "15m"], "source": "ccxt"}
    )
    assert result["source"] == "stub"
    assert "sem feed" in (result.get("note") or "").lower()


@pytest.mark.integration
@pytest.mark.parametrize(
    "pair,exchange",
    [
        ("EURUSD", "kraken"),
        ("XAUUSD", "kraken"),
        ("GBPUSD", "kraken"),
    ],
)
def test_fetch_ccxt_primary_pairs(pair, exchange):
    result = fetch_multi_tf_data.invoke(
        {"pair": pair, "timeframes": ["1d", "1h", "15m"], "source": "ccxt"}
    )
    assert result["source"] == "ccxt"
    assert result["exchange"] == exchange
    assert result["candle_counts"]["1d"] >= 30
    candle = result["timeframes"]["1h"][-1]
    assert all(k in candle for k in ("open", "high", "low", "close", "timestamp"))