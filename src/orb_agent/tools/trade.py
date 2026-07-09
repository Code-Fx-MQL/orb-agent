from typing import Any

from langchain_core.tools import tool

from orb_agent.config.orb_rules import MIN_RISK_REWARD
from orb_agent.config.settings import settings
from orb_agent.models.schemas import SetupDirection, TradeParams


def _pip_risk_and_reward(
    direction: SetupDirection,
    entry: float,
    stop_loss: float,
    take_profit: float,
) -> tuple[float, float]:
    if direction == SetupDirection.BULLISH:
        pip_risk = entry - stop_loss
        pip_reward = take_profit - entry
    else:
        pip_risk = stop_loss - entry
        pip_reward = entry - take_profit
    return pip_risk, pip_reward


def build_trade_params(
    setup: dict[str, Any],
    *,
    account_balance: float = 10_000.0,
    risk_percent: float | None = None,
) -> dict[str, Any]:
    """Calcula e valida parametros de trade a partir do setup ORB."""
    risk = risk_percent if risk_percent is not None else settings.max_risk_per_trade
    risk = min(risk, settings.max_risk_per_trade)

    direction = SetupDirection(setup["direction"])
    entry = float(setup["entry"])
    stop_loss = float(setup["stop_loss"])
    take_profit = float(setup["take_profit"])

    pip_risk, pip_reward = _pip_risk_and_reward(direction, entry, stop_loss, take_profit)

    if pip_risk <= 0:
        return {"valid": False, "reason": "Stop loss invalido (risco zero ou negativo)"}

    rr = pip_reward / pip_risk
    if rr < MIN_RISK_REWARD:
        return {
            "valid": False,
            "reason": f"R:R {rr:.2f} abaixo do minimo 1:{MIN_RISK_REWARD}",
        }

    risk_amount = account_balance * risk
    position_size = risk_amount / pip_risk
    lots = round(position_size / 100_000, 4)

    params = TradeParams(
        pair=setup["pair"],
        direction=direction,
        entry=round(entry, 5),
        stop_loss=round(stop_loss, 5),
        take_profit=round(take_profit, 5),
        risk_reward=round(rr, 2),
        position_size_lots=lots,
        risk_percent=risk,
    )
    result = params.model_dump(mode="json")
    result["valid"] = True
    return result


@tool
def calculate_trade_params(
    setup: dict,
    account_balance: float = 10_000.0,
    risk_percent: float | None = None,
) -> dict:
    """Calcula entry, SL, TP validados e position sizing para setup ORB."""
    return build_trade_params(
        setup,
        account_balance=account_balance,
        risk_percent=risk_percent,
    )


@tool
def identify_confluences(setup: dict) -> dict:
    """Lista confluencias do setup ORB detectado."""
    confluences: list[str] = []
    meta = setup.get("metadata") or {}

    confluences.append("top_down_1d_1h_15m")
    confluences.append(f"bias_{setup.get('direction', '')}")

    pattern = meta.get("pattern")
    if pattern == "breakout_retest":
        confluences.append("breakout_com_reteste")
    elif pattern == "immediate_breakout":
        confluences.append("breakout_imediato")

    if setup.get("confidence", 0) >= 0.7:
        confluences.append("confianca_alta")

    or_size = float(setup.get("or_high", 0)) - float(setup.get("or_low", 0))
    if or_size > 0:
        confluences.append("opening_range_definido")

    strength = "strong" if len(confluences) >= 4 else "moderate" if len(confluences) >= 3 else "weak"

    return {
        "pair": setup.get("pair"),
        "confluences": confluences,
        "confluence_count": len(confluences),
        "strength": strength,
    }