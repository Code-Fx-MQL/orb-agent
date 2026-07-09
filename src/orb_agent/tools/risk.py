from typing import Any

from langchain_core.tools import tool

from orb_agent.config.settings import OperationMode, settings
from orb_agent.guardrails.limits import RiskTracker
from orb_agent.models.schemas import RiskCheckResult

_tracker = RiskTracker()


def get_risk_tracker() -> RiskTracker:
    return _tracker


def reset_risk_tracker() -> None:
    global _tracker
    _tracker = RiskTracker()


@tool
def check_risk_limits(
    trade_params: dict[str, Any],
    mode: str = "analysis",
    pair: str = "",
) -> dict:
    """Valida limites de risco por trade, diario e semanal."""
    op_mode = OperationMode(mode)
    risk_percent = float(trade_params.get("risk_percent", settings.max_risk_per_trade))

    if op_mode == OperationMode.LIVE:
        if not settings.live_approved:
            return RiskCheckResult(
                approved=False,
                reason="Live bloqueado — ORB_LIVE_APPROVED=false",
                risk_percent=risk_percent,
                daily_risk_used=_tracker.daily_risk_used,
                weekly_risk_used=_tracker.weekly_risk_used,
            ).model_dump(mode="json")

    ok, reason = _tracker.can_take_trade(risk_percent)
    if not ok:
        return RiskCheckResult(
            approved=False,
            reason=reason,
            risk_percent=risk_percent,
            daily_risk_used=_tracker.daily_risk_used,
            weekly_risk_used=_tracker.weekly_risk_used,
        ).model_dump(mode="json")

    if op_mode in (OperationMode.PAPER, OperationMode.LIVE):
        _tracker.record_trade_risk(risk_percent)

    return RiskCheckResult(
        approved=True,
        reason=None,
        risk_percent=risk_percent,
        daily_risk_used=_tracker.daily_risk_used,
        weekly_risk_used=_tracker.weekly_risk_used,
    ).model_dump(mode="json")