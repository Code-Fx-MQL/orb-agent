import pytest

from orb_agent.tools.risk import reset_risk_tracker


@pytest.fixture(autouse=True)
def _reset_risk_tracker():
    reset_risk_tracker()
    yield
    reset_risk_tracker()