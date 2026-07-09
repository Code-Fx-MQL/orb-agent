"""Alertas paper — verificacao SL/TP."""

from __future__ import annotations

from typing import Any

from orb_agent.config.settings import settings
from orb_agent.paper.store import get_paper_store
from orb_agent.tools.data import fetch_multi_tf_data


def get_current_price(pair: str) -> float:
    data = fetch_multi_tf_data.invoke({
        "pair": pair.upper(),
        "timeframes": [settings.default_ltf],
    })
    candles = data["timeframes"][settings.default_ltf]
    if not candles:
        raise ValueError(f"Sem candles para {pair}")
    return float(candles[-1]["close"])


def check_paper_alerts(pair: str | None = None) -> dict[str, Any]:
    store = get_paper_store()
    open_positions = store.summary()["open"]
    if pair:
        open_positions = [p for p in open_positions if p["pair"] == pair.upper()]

    if not open_positions:
        return {
            "checked": 0,
            "alerts": [],
            "closed": [],
            "prices": {},
            "message": "Nenhuma posicao paper aberta",
        }

    pairs = sorted({p["pair"] for p in open_positions})
    prices: dict[str, float] = {}
    errors: dict[str, str] = {}
    for p in pairs:
        try:
            prices[p] = get_current_price(p)
        except (ValueError, KeyError, IndexError) as exc:
            errors[p] = str(exc)

    alerts: list[dict[str, Any]] = []
    closed: list[dict[str, Any]] = []
    for p, price in prices.items():
        for hit in store.check_exits(p, price):
            closed.append(hit)
            alert_type = "tp_hit" if hit.get("outcome") == "win" else "sl_hit"
            label = "Take Profit" if alert_type == "tp_hit" else "Stop Loss"
            alerts.append({
                "type": alert_type,
                "pair": hit["pair"],
                "message": f"{label} em {hit['pair']} @ {hit.get('exit_price')}",
            })

    return {
        "checked": len(open_positions),
        "alerts": alerts,
        "closed": closed,
        "prices": prices,
        "errors": errors,
        "message": f"{len(alerts)} alerta(s), {len(closed)} posicao(oes) fechada(s)",
    }