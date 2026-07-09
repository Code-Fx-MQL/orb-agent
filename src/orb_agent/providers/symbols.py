"""Mapeamento par -> exchange CCXT + simbolo."""

from dataclasses import dataclass

PRIMARY_PAIRS: tuple[str, ...] = (
    "EURUSD",
    "XAUUSD",
    "GBPUSD",
    "USDCAD",
    "USDCHF",
    "US30",
    "NAS100",
)

INDEX_PAIRS: frozenset[str] = frozenset({"US30", "US100", "NAS100", "GER40"})


@dataclass(frozen=True)
class PairMarket:
    exchange_id: str
    symbol: str
    note: str = ""
    priority: int = 99
    stub_only: bool = False


PAIR_MARKETS: dict[str, PairMarket] = {
    "EURUSD": PairMarket("kraken", "EUR/USD", priority=1),
    "XAUUSD": PairMarket("kraken", "XAUT/USD", note="proxy XAUT/USD no Kraken", priority=2),
    "GBPUSD": PairMarket("kraken", "GBP/USD", priority=3),
    "USDCAD": PairMarket("kraken", "USD/CAD", priority=4),
    "USDCHF": PairMarket("kraken", "USD/CHF", priority=5),
    "US30": PairMarket("gate", "US30/USDT:USDT", note="Dow Jones CFD", priority=6),
    "NAS100": PairMarket("gate", "NAS100/USDT:USDT", note="Nasdaq 100 CFD", priority=7),
    "US100": PairMarket("gate", "NAS100/USDT:USDT", note="proxy NAS100", priority=8),
    "GER40": PairMarket("gate", "GER40/USDT:USDT", note="DAX CFD", priority=9),
    "GBPJPY": PairMarket("stub", "GBPJPY", note="sem feed CCXT estavel", priority=10, stub_only=True),
    "AUDCAD": PairMarket("stub", "AUDCAD", note="sem feed CCXT estavel", priority=11, stub_only=True),
}

CCXT_TIMEFRAMES: dict[str, str] = {
    "1m": "1m",
    "5m": "5m",
    "15m": "15m",
    "1h": "1h",
    "4h": "4h",
    "1d": "1d",
}

STUB_BASE_PRICES: dict[str, float] = {
    "EURUSD": 1.0850,
    "XAUUSD": 2350.0,
    "GBPUSD": 1.2700,
    "USDCAD": 1.3600,
    "USDCHF": 0.8800,
    "US30": 42000.0,
    "NAS100": 21000.0,
    "US100": 21000.0,
    "GER40": 18000.0,
    "GBPJPY": 195.50,
    "AUDCAD": 0.9000,
}


def resolve_pair_market(pair: str) -> PairMarket:
    from orb_agent.config.pairs_registry import get_pairs_registry

    return get_pairs_registry().resolve_market(pair)


def normalize_timeframe(tf: str) -> str:
    key = tf.strip().lower()
    if key not in CCXT_TIMEFRAMES:
        raise ValueError(f"Timeframe '{tf}' nao suportado. Use: {list(CCXT_TIMEFRAMES)}")
    return CCXT_TIMEFRAMES[key]


def stub_base_price(pair: str) -> float:
    key = pair.upper().replace("/", "").replace("_", "")
    return STUB_BASE_PRICES.get(key, 1.0850)


def is_index_pair(pair: str) -> bool:
    key = pair.upper().replace("/", "").replace("_", "")
    return key in INDEX_PAIRS