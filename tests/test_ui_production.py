from orb_agent.config.settings import settings
from orb_agent.ui.production import _format_refresh_time, _status_class


def test_status_class_mapping():
    assert _status_class("ok") == "ok"
    assert _status_class("fail") == "fail"
    assert _status_class("unknown") == "info"


def test_format_refresh_time():
    assert _format_refresh_time(None) == "—"
    formatted = _format_refresh_time("2026-07-09T12:30:45+00:00")
    assert ":" in formatted


def test_production_settings_defaults(monkeypatch):
    monkeypatch.setattr(settings, "ui_auto_refresh_enabled", True)
    monkeypatch.setattr(settings, "ui_auto_refresh_seconds", 300)
    assert settings.ui_auto_refresh_enabled is True
    assert settings.ui_auto_refresh_seconds == 300