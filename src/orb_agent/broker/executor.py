"""Executor de ordens ORB — stub default, CCXT opcional."""

from __future__ import annotations

from typing import Any
from uuid import uuid4

import structlog

from orb_agent.audit.logger import get_audit_logger
from orb_agent.config.settings import settings
from orb_agent.guardrails.live_gate import is_live_trading_allowed
from orb_agent.providers.ccxt_provider import _get_exchange
from orb_agent.providers.symbols import resolve_pair_market

logger = structlog.get_logger(__name__)


class BrokerExecutor:
    """Coloca ordens apenas com live gate aprovado."""

    def place_order(
        self,
        pair: str,
        trade_params: dict[str, Any],
        setup_id: str | None = None,
    ) -> dict[str, Any]:
        audit = get_audit_logger()
        allowed, reason = is_live_trading_allowed()

        if not allowed:
            entry = audit.log("live_blocked", {
                "pair": pair.upper(),
                "setup_id": setup_id,
                "reason": reason,
            })
            result = {
                "placed": False,
                "reason": reason,
                "audit_id": entry["id"],
            }
            from orb_agent.alerts.dispatcher import notify_live_order

            notify_live_order(result, pair)
            return result

        pair = pair.upper()
        if settings.broker_mode == "stub":
            return self._place_stub(pair, trade_params, setup_id)

        return self._place_ccxt(pair, trade_params, setup_id)

    def _place_stub(
        self,
        pair: str,
        trade_params: dict[str, Any],
        setup_id: str | None,
    ) -> dict[str, Any]:
        order_id = f"stub-{uuid4().hex[:8]}"
        audit = get_audit_logger()
        entry = audit.log("live_order_stub", {
            "pair": pair,
            "setup_id": setup_id,
            "order_id": order_id,
            "direction": trade_params.get("direction"),
            "entry": trade_params.get("entry"),
            "stop_loss": trade_params.get("stop_loss"),
            "take_profit": trade_params.get("take_profit"),
            "position_size_lots": trade_params.get("position_size_lots"),
            "broker_mode": "stub",
        })
        logger.info("broker_stub_order", pair=pair, order_id=order_id)
        result = {
            "placed": True,
            "stub": True,
            "order_id": order_id,
            "pair": pair,
            "message": "Ordem simulada (stub) — nenhuma execucao real no broker",
            "audit_id": entry["id"],
        }
        from orb_agent.alerts.dispatcher import notify_live_order

        notify_live_order(result, pair)
        return result

    def _place_ccxt(
        self,
        pair: str,
        trade_params: dict[str, Any],
        setup_id: str | None,
    ) -> dict[str, Any]:
        audit = get_audit_logger()
        try:
            market = resolve_pair_market(pair)
            exchange = _get_exchange(market.exchange_id)
            symbol = market.symbol
            side = "buy" if trade_params.get("direction") == "bullish" else "sell"
            amount = float(trade_params.get("position_size_lots", 0.01))

            if not settings.ccxt_api_key:
                entry = audit.log("live_order_failed", {
                    "pair": pair,
                    "setup_id": setup_id,
                    "reason": "CCXT_API_KEY ausente",
                })
                return {"placed": False, "reason": "CCXT_API_KEY ausente", "audit_id": entry["id"]}

            order = exchange.create_order(symbol, "market", side, amount)
            entry = audit.log("live_order_placed", {
                "pair": pair,
                "setup_id": setup_id,
                "exchange": market.exchange_id,
                "symbol": symbol,
                "side": side,
                "amount": amount,
                "order_id": order.get("id"),
            })
            result = {
                "placed": True,
                "stub": False,
                "order_id": order.get("id"),
                "pair": pair,
                "exchange": market.exchange_id,
                "audit_id": entry["id"],
                "raw": order,
            }
            from orb_agent.alerts.dispatcher import notify_live_order

            notify_live_order(result, pair)
            return result
        except Exception as exc:
            entry = audit.log("live_order_failed", {
                "pair": pair,
                "setup_id": setup_id,
                "error": str(exc),
            })
            logger.warning("broker_ccxt_failed", pair=pair, error=str(exc))
            result = {"placed": False, "reason": str(exc), "audit_id": entry["id"]}
            from orb_agent.alerts.dispatcher import notify_live_order

            notify_live_order(result, pair)
            return result


_executor: BrokerExecutor | None = None


def get_broker_executor() -> BrokerExecutor:
    global _executor
    if _executor is None:
        _executor = BrokerExecutor()
    return _executor


def place_orb_order(
    pair: str,
    trade_params: dict[str, Any],
    setup_id: str | None = None,
) -> dict[str, Any]:
    return get_broker_executor().place_order(pair, trade_params, setup_id=setup_id)