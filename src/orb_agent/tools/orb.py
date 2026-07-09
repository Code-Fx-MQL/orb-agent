from langchain_core.tools import tool

@tool
def detect_orb_setup(
    pair: str,
    htf_candles: list,
    mtf_candles: list,
    ltf_candles: list,
    htf_timeframe: str = "4h",
    mtf_timeframe: str = "1h",
    ltf_timeframe: str = "15m",
) -> dict:
    """Detector de setup (stub - implementar na Fase 3)."""
    return {"found": False, "reason": "stub: nao implementado", "setup": None}