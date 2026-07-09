from orb_agent.config.settings import settings
from orb_agent.tools.data import fetch_multi_tf_data
from orb_agent.tools.orb import detect_orb_setup


def _candles_for_tf(data: dict, timeframe: str) -> list:
    tfs = data.get("timeframes") or {}
    return list(tfs.get(timeframe) or [])


def run_pair_analysis(pair: str) -> dict:
    pair = pair.upper()
    tfs = [settings.default_htf, settings.default_mtf, settings.default_ltf]
    data = fetch_multi_tf_data.invoke({
        "pair": pair,
        "timeframes": tfs,
        "source": settings.data_source,
    })

    htf_candles = _candles_for_tf(data, settings.default_htf)
    mtf_candles = _candles_for_tf(data, settings.default_mtf)
    ltf_candles = _candles_for_tf(data, settings.default_ltf)

    detection = detect_orb_setup.invoke({
        "pair": pair,
        "htf_candles": htf_candles,
        "mtf_candles": mtf_candles,
        "ltf_candles": ltf_candles,
        "htf_timeframe": settings.default_htf,
        "mtf_timeframe": settings.default_mtf,
        "ltf_timeframe": settings.default_ltf,
    })
    return {
        "pair": pair,
        "mode": settings.mode.value,
        "data_source": data.get("source"),
        "detection": detection,
    }