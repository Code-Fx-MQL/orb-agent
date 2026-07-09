#!/usr/bin/env python3
"""Testa health, webhooks e scan com env de producao (mesmo stack EasyPanel)."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import httpx

PROD_URL = os.environ.get(
    "ORB_PROD_URL",
    "https://fullscopetrade-harness-orb-agent.0ikuso.easypanel.host",
)


def _load_env_file(path: Path) -> None:
    if not path.exists():
        return
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, val = line.partition("=")
        key, val = key.strip(), val.strip()
        if key and key not in os.environ:
            os.environ[key] = val


def _check_health() -> dict:
    url = f"{PROD_URL.rstrip('/')}/_stcore/health"
    r = httpx.get(url, timeout=30)
    return {"url": url, "status": r.status_code, "body": r.text.strip(), "ok": r.status_code == 200 and r.text.strip() == "ok"}


def _run_ops_with_prod_env() -> dict:
    root = Path(__file__).resolve().parents[1]
    _load_env_file(root / "deploy" / "easypanel" / ".env.production")

    from orb_agent.alerts.dispatcher import dispatch_alert
    from orb_agent.config.settings import settings
    from orb_agent.tools.analyze import analyze_all_primary_pairs

    wh = dispatch_alert(
        "test_ping",
        "Teste producao ORB",
        f"Ping do teste producao — {PROD_URL}",
        level="success",
        data={"source": "test-production-ops", "prod_url": PROD_URL},
    )

    scan = analyze_all_primary_pairs.invoke({})
    dispatch_scan = dispatch_alert(
        "scan_complete",
        "Scan ORB producao",
        scan.get("summary", ""),
        level="info",
        data={
            "pairs_scanned": list(scan.get("results", {}).keys()),
            "setups_found": [p for p, r in scan.get("results", {}).items() if r.get("found")],
            "prod_url": PROD_URL,
        },
    )

    return {
        "mode": settings.mode.value,
        "webhook_enabled": settings.webhook_enabled,
        "webhook_url": settings.webhook_url,
        "telegram_enabled": settings.telegram_enabled,
        "test_ping": wh,
        "scan_summary": scan.get("summary"),
        "scan_complete_webhook": dispatch_scan,
        "pairs": {
            p: {
                "found": r.get("found"),
                "source": r.get("data_source"),
                "reason": r.get("reason"),
            }
            for p, r in scan.get("results", {}).items()
        },
    }


def main() -> int:
    print(f"=== Teste producao ORB ===\nURL: {PROD_URL}\n")

    health = _check_health()
    print("[1] Health")
    print(json.dumps(health, indent=2))

    print("\n[2] Webhook + scan (env producao)")
    try:
        ops = _run_ops_with_prod_env()
        print(json.dumps(ops, indent=2, default=str))
    except Exception as exc:
        print(json.dumps({"error": str(exc)}, indent=2))
        return 1

    ok = health.get("ok") and ops.get("test_ping", {}).get("sent")
    print("\n=== Resultado ===")
    print("OK" if ok else "FALHA")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())