#!/usr/bin/env python3
"""Scan agendado — analisa pares prioritarios e dispara webhooks."""

from orb_agent.alerts.dispatcher import notify_paper_alerts, notify_scan_complete, notify_setup_found
from orb_agent.config.settings import settings
from orb_agent.paper.alerts import check_paper_alerts
from orb_agent.tools.analyze import analyze_all_primary_pairs


def main() -> int:
    result = analyze_all_primary_pairs.invoke({})
    notify_scan_complete(result)

    for pair, data in result.get("results", {}).items():
        if data.get("found"):
            notify_setup_found(pair, data)

    paper = check_paper_alerts()
    alerts = paper.get("alerts", [])
    if alerts:
        notify_paper_alerts(alerts)

    print(result.get("summary", ""))
    print(paper.get("message", ""))
    print(f"mode={settings.mode.value}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())