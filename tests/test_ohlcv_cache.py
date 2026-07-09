import time

from orb_agent.providers.ohlcv_cache import cache_stats, get_cached, set_cached


def test_cache_roundtrip(tmp_path, monkeypatch):
    monkeypatch.setattr("orb_agent.providers.ohlcv_cache.settings.memory_dir", str(tmp_path / "memory"))
    monkeypatch.setattr("orb_agent.providers.ohlcv_cache.settings.cache_enabled", True)
    monkeypatch.setattr("orb_agent.providers.ohlcv_cache.settings.cache_ttl_seconds", 300)

    candles = [{"timestamp": 1, "open": 1.0, "high": 1.1, "low": 0.9, "close": 1.05, "volume": 100}]
    set_cached("EURUSD", "15m", 100, candles)
    loaded = get_cached("EURUSD", "15m", 100)
    assert loaded is not None
    assert len(loaded) == 1
    assert cache_stats()["files"] >= 1


def test_cache_expires(tmp_path, monkeypatch):
    monkeypatch.setattr("orb_agent.providers.ohlcv_cache.settings.memory_dir", str(tmp_path / "memory"))
    monkeypatch.setattr("orb_agent.providers.ohlcv_cache.settings.cache_enabled", True)
    monkeypatch.setattr("orb_agent.providers.ohlcv_cache.settings.cache_ttl_seconds", 1)

    candles = [{"timestamp": 1, "open": 1.0, "high": 1.1, "low": 0.9, "close": 1.05, "volume": 100}]
    set_cached("EURUSD", "1h", 50, candles)
    time.sleep(1.1)
    assert get_cached("EURUSD", "1h", 50) is None