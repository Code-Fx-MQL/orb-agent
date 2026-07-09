"""Dispatcher central de alertas ORB."""

from __future__ import annotations

from typing import Any

from orb_agent.alerts.payloads import build_setup_found_data
from orb_agent.alerts.webhooks import send_webhook
from orb_agent.audit.logger import get_audit_logger


def dispatch_alert(
    event_type: str,
    title: str,
    body: str,
    level: str = "info",
    data: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Envia webhook estruturado e registra no audit log."""
    result = send_webhook(event_type, title, body, level=level, data=data)
    get_audit_logger().log("webhook_dispatch", {
        "event_type": event_type,
        "title": title,
        "level": level,
        "sent": result.get("sent"),
        "results": result.get("results", []),
    })
    return result


def notify_paper_alerts(alerts: list[dict[str, Any]]) -> None:
    for alert in alerts:
        level = "success" if alert.get("type") == "tp_hit" else "error"
        dispatch_alert(
            event_type="paper_alert",
            title=f"Paper {alert.get('pair')}",
            body=alert.get("message", ""),
            level=level,
            data=alert,
        )


def notify_scan_complete(results: dict[str, Any]) -> None:
    found = [p for p, r in results.get("results", {}).items() if r.get("found")]
    dispatch_alert(
        event_type="scan_complete",
        title="Scan ORB concluido",
        body=results.get("summary", ""),
        level="success" if found else "info",
        data={
            "pairs_scanned": list(results.get("results", {}).keys()),
            "setups_found": found,
            "results": results.get("results"),
        },
    )


def notify_setup_found(pair: str, result: dict[str, Any]) -> None:
    explanation = result.get("explanation", "") or ""
    dispatch_alert(
        event_type="setup_found",
        title=f"Setup ORB {pair}",
        body=explanation[:1200],
        level="trade",
        data=build_setup_found_data(pair, result),
    )


def notify_live_order(order_result: dict[str, Any], pair: str) -> None:
    if order_result.get("placed"):
        dispatch_alert(
            event_type="live_order",
            title=f"Ordem {pair}",
            body=order_result.get("message", f"Order {order_result.get('order_id')}"),
            level="trade",
            data={"pair": pair, **order_result},
        )
    elif order_result.get("reason"):
        dispatch_alert(
            event_type="live_blocked",
            title=f"Live bloqueado {pair}",
            body=str(order_result["reason"]),
            level="warning",
            data={"pair": pair, **order_result},
        )