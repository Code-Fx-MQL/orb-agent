"""Regras codificadas - Opening Range Breakout."""

from enum import Enum

from orb_agent.models.schemas import SetupDirection

__all__ = [
    "SetupDirection",
    "BreakoutMode",
    "ORB_SESSION_CANDLES",
    "MIN_OR_RANGE_FOREX",
    "MIN_OR_RANGE_GOLD",
    "RETEST_TOLERANCE_RATIO",
    "REQUIRE_RETEST",
    "LTF_LOOKBACK",
    "MIN_SETUP_CONFIDENCE",
    "MIN_RISK_REWARD",
    "DEFAULT_BREAKOUT_MODE",
]


class BreakoutMode(str, Enum):
    """Breakout com reteste (conservador) ou entrada no primeiro fecho fora do OR."""

    RETEST = "retest"
    IMMEDIATE = "immediate"


ORB_SESSION_CANDLES = 1
MIN_OR_RANGE_FOREX = 0.0008
MIN_OR_RANGE_GOLD = 2.0
RETEST_TOLERANCE_RATIO = 0.25
REQUIRE_RETEST = True
LTF_LOOKBACK = 16
MIN_SETUP_CONFIDENCE = 0.5
MIN_RISK_REWARD = 1.0
DEFAULT_BREAKOUT_MODE = BreakoutMode.RETEST