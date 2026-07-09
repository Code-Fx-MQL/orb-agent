import pytest

from orb_agent.config import settings as settings_mod
from orb_agent.memory.store import reset_memory
from orb_agent.tools.risk import reset_risk_tracker


@pytest.fixture(autouse=True)
def _isolated_runtime(tmp_path, monkeypatch):
    mem_dir = tmp_path / "memory"
    monkeypatch.setattr(settings_mod.settings, "memory_dir", str(mem_dir))
    monkeypatch.setattr(settings_mod.settings, "data_source", "stub")
    monkeypatch.setattr(settings_mod.settings, "backtest_candle_limit", 80)
    reset_risk_tracker()
    reset_memory()
    yield
    reset_risk_tracker()
    reset_memory()