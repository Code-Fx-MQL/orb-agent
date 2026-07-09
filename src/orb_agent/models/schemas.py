from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class SetupDirection(str, Enum):
    BULLISH = "bullish"
    BEARISH = "bearish"


class ORBSetup(BaseModel):
    pair: str
    direction: SetupDirection
    htf_timeframe: str
    mtf_timeframe: str
    ltf_timeframe: str
    or_high: float
    or_low: float
    entry: float
    stop_loss: float
    take_profit: float
    confidence: float = Field(ge=0.0, le=1.0)
    metadata: dict[str, Any] = Field(default_factory=dict)