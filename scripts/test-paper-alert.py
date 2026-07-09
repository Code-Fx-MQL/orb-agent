#!/usr/bin/env python3
"""Envia alertas paper_alert de teste (TP + SL) via n8n e Telegram."""

from __future__ import annotations

import json

from orb_agent.alerts.dispatcher import dispatch_alert


def main() -> int:
    alerts = [
        {
            "type": "tp_hit",
            "pair": "EURUSD",
            "message": "Take Profit em EURUSD @ 1.14830 [TESTE paper_alert]",
        },
        {
            "type": "sl_hit",
            "pair": "XAUUSD",
            "message": "Stop Loss em XAUUSD @ 4150.4 [TESTE paper_alert]",
        },
    ]
    ok = True
    for alert in alerts:
        level = "success" if alert["type"] == "tp_hit" else "error"
        result = dispatch_alert(
            "paper_alert",
            f"Paper {alert['pair']}",
            alert["message"],
            level=level,
            data=alert,
        )
        print(f"--- {alert['type']} {alert['pair']} ---")
        print(json.dumps(result, indent=2, default=str))
        if not result.get("sent"):
            ok = False
        print()
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())