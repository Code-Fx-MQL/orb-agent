from __future__ import annotations

from typing import Any

from orb_agent.audit.logger import get_audit_logger
from orb_agent.config.settings import OperationMode, settings
from orb_agent.memory.store import get_memory
from orb_agent.observability.langsmith import configure_tracing, traced
from orb_agent.paper.alerts import check_paper_alerts
from orb_agent.paper.store import get_paper_store
from orb_agent.tools.backtest import run_orb_backtest
from orb_agent.tools.data import fetch_multi_tf_data
from orb_agent.tools.explain import explain_setup_detalhado
from orb_agent.tools.orb import detect_orb_setup
from orb_agent.tools.risk import check_risk_limits
from orb_agent.tools.trade import calculate_trade_params, identify_confluences


def _candles_for_tf(data: dict, timeframe: str) -> list:
    tfs = data.get("timeframes") or {}
    return list(tfs.get(timeframe) or [])


def _dispatch_paper_alerts(result: dict[str, Any]) -> None:
    if not settings.webhook_enabled:
        return
    alerts = (result.get("paper_alerts") or {}).get("alerts", [])
    if alerts:
        from orb_agent.alerts.dispatcher import notify_paper_alerts

        notify_paper_alerts(alerts)


@traced(name="orb_pair_analysis", run_type="chain")
def run_pair_analysis(pair: str) -> dict[str, Any]:
    """Pipeline ORB: dados -> deteccao -> confluencias -> trade -> risco -> explicacao."""
    configure_tracing()
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

    result: dict[str, Any] = {
        "pair": pair,
        "mode": settings.mode.value,
        "data_source": data.get("source"),
        "exchange": data.get("exchange"),
        "found": detection.get("found", False),
        "reason": detection.get("reason"),
        "setup": None,
        "confluences": None,
        "trade_params": None,
        "risk_check": None,
        "backtest": None,
        "setup_id": None,
        "paper_trade": None,
        "paper_alerts": None,
        "explanation": None,
        "detection": detection,
    }

    try:
        result["backtest"] = run_orb_backtest.invoke({
            "pair": pair,
            "candle_limit": settings.backtest_candle_limit,
        })
    except Exception as exc:
        result["backtest"] = {"pair": pair, "error": str(exc), "total_trades": 0}

    if not detection.get("found"):
        result["explanation"] = f"Analise {pair}: {detection.get('reason', 'sem setup')}"
        result["paper_alerts"] = check_paper_alerts(pair)
        get_audit_logger().log("analysis_no_setup", {
            "pair": pair,
            "reason": detection.get("reason"),
        })
        _dispatch_paper_alerts(result)
        return result

    setup = detection["setup"]
    conf = identify_confluences.invoke({"setup": setup})
    result["confluences"] = conf

    trade = calculate_trade_params.invoke({"setup": setup})
    if not trade.get("valid", True):
        result.update({
            "setup": setup,
            "reason": trade.get("reason"),
            "found": False,
            "explanation": f"Setup {pair} detectado mas trade rejeitado: {trade.get('reason')}",
            "paper_alerts": check_paper_alerts(pair),
        })
        get_audit_logger().log("setup_filtered", {
            "pair": pair,
            "reason": trade.get("reason"),
        })
        _dispatch_paper_alerts(result)
        return result

    risk = check_risk_limits.invoke({
        "trade_params": trade,
        "mode": settings.mode.value,
        "pair": pair,
    })

    explanation = explain_setup_detalhado.invoke({"setup": setup, "trade": trade})

    result.update({
        "setup": setup,
        "trade_params": trade,
        "risk_check": risk,
        "explanation": explanation,
        "found": True,
        "reason": None if risk.get("approved") else risk.get("reason"),
    })

    paper_result = None
    if not risk.get("approved"):
        result["found"] = False
        result["explanation"] = f"Setup {pair} bloqueado por risco: {risk.get('reason')}"
        get_audit_logger().log("risk_blocked", {
            "pair": pair,
            "reason": risk.get("reason"),
        })
    else:
        result["setup_id"] = get_memory().log_setup(
            pair, setup, trade, result.get("backtest"),
        )
        if settings.mode == OperationMode.PAPER:
            paper_result = get_paper_store().open_position(pair, trade, setup_id=result["setup_id"])
            get_audit_logger().log("paper_open", {
                "pair": pair,
                "setup_id": result["setup_id"],
                "result": paper_result,
            })

        get_audit_logger().log("setup_detected", {
            "pair": pair,
            "setup_id": result.get("setup_id"),
            "direction": setup.get("direction"),
            "confidence": setup.get("confidence"),
            "risk_approved": risk.get("approved"),
            "mode": settings.mode.value,
        })

        if settings.webhook_enabled:
            from orb_agent.alerts.dispatcher import notify_setup_found

            notify_setup_found(pair, result)

    result["paper_trade"] = paper_result
    result["paper_alerts"] = check_paper_alerts(pair)
    _dispatch_paper_alerts(result)
    return result