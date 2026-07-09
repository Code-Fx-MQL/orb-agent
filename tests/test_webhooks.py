from unittest.mock import MagicMock, patch

from orb_agent.alerts.webhooks import send_n8n_webhook, send_webhook


def test_webhook_disabled(monkeypatch):
    monkeypatch.setattr("orb_agent.alerts.webhooks.settings.webhook_enabled", False)
    result = send_webhook("test_event", "Title", "body")
    assert result["sent"] is False


def test_n8n_payload_has_event_type(monkeypatch):
    monkeypatch.setattr("orb_agent.alerts.webhooks.settings.webhook_url", "https://n8n.test/hook")
    monkeypatch.setattr("orb_agent.alerts.webhooks.settings.webhook_app_id", "orb-agent")
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    with patch("orb_agent.alerts.webhooks.httpx.post", return_value=mock_resp) as mock_post:
        result = send_n8n_webhook(
            "paper_alert",
            "Paper EURUSD",
            "TP atingido",
            level="success",
            data={"pair": "EURUSD", "type": "tp_hit"},
        )
    assert result["sent"] is True
    assert result["event_type"] == "paper_alert"
    payload = mock_post.call_args[1]["json"]
    assert payload["app"] == "orb-agent"
    assert payload["event_type"] == "paper_alert"
    assert payload["data"]["pair"] == "EURUSD"