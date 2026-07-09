import os

from orb_agent.config.settings import settings
from orb_agent.observability.langsmith import configure_tracing, is_tracing_enabled, traced


def test_tracing_disabled_by_default():
    assert is_tracing_enabled() is False


def test_configure_tracing_sets_env(monkeypatch):
    monkeypatch.setattr(settings, "langsmith_tracing", True)
    monkeypatch.setattr(settings, "langsmith_api_key", "test-key")
    monkeypatch.setattr(settings, "langsmith_project", "orb-test")
    monkeypatch.setattr("orb_agent.observability.langsmith._configured", False)

    assert configure_tracing() is True
    assert os.environ.get("LANGSMITH_TRACING") == "true"
    assert os.environ.get("LANGSMITH_API_KEY") == "test-key"
    assert os.environ.get("LANGSMITH_PROJECT") == "orb-test"


def test_traced_decorator_noop_without_key():
    @traced(name="test_fn")
    def sample(x: int) -> int:
        return x * 2

    assert sample(3) == 6