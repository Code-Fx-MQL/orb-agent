from orb_agent.config.settings import settings, OperationMode
from orb_agent.tools.registry import get_all_tools
from orb_agent.pipeline.analyze import run_pair_analysis

def test_settings_default_analysis():
    assert settings.mode == OperationMode.ANALYSIS

def test_registry_has_eight_tools():
    assert len(get_all_tools()) >= 8

def test_run_pair_analysis_stub():
    result = run_pair_analysis("XAUUSD")
    assert result["pair"] == "XAUUSD"
    assert "detection" in result