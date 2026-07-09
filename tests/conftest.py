import pytest

from orb_agent.audit.logger import reset_audit_logger
from orb_agent.config import settings as settings_mod
from orb_agent.guardrails.live_gate import set_live_session_token
from orb_agent.memory.mem0_sync import reset_mem0_sync
from orb_agent.memory.store import reset_memory
from orb_agent.paper.store import reset_paper_store
from orb_agent.tools.risk import reset_risk_tracker


@pytest.fixture(autouse=True)
def _isolated_runtime(tmp_path, monkeypatch):
    mem_dir = tmp_path / "memory"
    audit_dir = tmp_path / "audit"
    monkeypatch.setattr(settings_mod.settings, "memory_dir", str(mem_dir))
    monkeypatch.setattr(settings_mod.settings, "audit_dir", str(audit_dir))
    monkeypatch.setattr(settings_mod.settings, "data_source", "stub")
    monkeypatch.setattr(settings_mod.settings, "backtest_candle_limit", 80)
    monkeypatch.setattr(settings_mod.settings, "webhook_enabled", False)
    monkeypatch.setattr(settings_mod.settings, "cache_enabled", False)
    monkeypatch.setattr(settings_mod.settings, "mem0_enabled", False)
    reset_risk_tracker()
    reset_mem0_sync()
    reset_memory()
    reset_paper_store()
    reset_audit_logger()
    set_live_session_token(None)
    yield
    reset_risk_tracker()
    reset_mem0_sync()
    reset_memory()
    reset_paper_store()
    reset_audit_logger()
    set_live_session_token(None)