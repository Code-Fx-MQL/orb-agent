#!/usr/bin/env python3
"""Envia alerta de teste via webhook n8n configurado no .env."""

from orb_agent.alerts.webhooks import send_webhook
from orb_agent.config.settings import settings

if __name__ == "__main__":
    print(f"ORB_WEBHOOK_ENABLED={settings.webhook_enabled}")
    print(f"ORB_WEBHOOK_URL={settings.webhook_url or 'nao'}")
    print(f"APP_ID={settings.webhook_app_id}")
    result = send_webhook(
        event_type="test_ping",
        title="Teste ORB Agent",
        body="Webhook configurado — alerta de teste do harness.",
        level="success",
        data={"test": True, "note": "event_type=test_ping para routing n8n"},
    )
    print(f"Enviado: {result.get('sent')}")
    print(f"event_type: {result.get('event_type')}")
    for item in result.get("results", []):
        ch = item.get("channel", "?")
        print(f"  {ch}: sent={item.get('sent')} {item.get('reason', item.get('status', ''))}")