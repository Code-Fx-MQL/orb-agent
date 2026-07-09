from datetime import datetime
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


class TradeParams(BaseModel):
    pair: str
    direction: SetupDirection
    entry: float
    stop_loss: float
    take_profit: float
    risk_reward: float
    position_size_lots: float
    risk_percent: float


class RiskCheckResult(BaseModel):
    approved: bool
    reason: str | None = None
    risk_percent: float = 0.0
    daily_risk_used: float = 0.0
    weekly_risk_used: float = 0.0


class BacktestResult(BaseModel):
    pair: str
    period_start: datetime
    period_end: datetime
    total_trades: int
    win_rate: float
    avg_rr: float
    profit_factor: float
    max_drawdown: float
    notes: str = ""