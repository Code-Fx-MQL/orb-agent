from langchain_core.tools import tool

@tool
def fetch_multi_tf_data(pair: str, timeframes: list[str], source: str = "auto") -> dict:
    """OHLCV multi-timeframe (stub)."""
    return {
        "pair": pair.upper(),
        "source": "stub",
        "timeframes": {tf: [] for tf in timeframes},
    }