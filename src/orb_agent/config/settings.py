from enum import Enum
from pydantic_settings import BaseSettings, SettingsConfigDict

class OperationMode(str, Enum):
    ANALYSIS = "analysis"
    PAPER = "paper"
    LIVE = "live"

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_prefix="ORB_", extra="ignore")

    mode: OperationMode = OperationMode.ANALYSIS
    pairs: str = "XAUUSD,EURUSD"
    data_source: str = "stub"
    default_htf: str = "4h"
    default_mtf: str = "1h"
    default_ltf: str = "15m"
    max_risk_per_trade: float = 0.01
    max_daily_risk: float = 0.03
    max_weekly_risk: float = 0.06
    block_news: bool = True
    live_approved: bool = False
    live_approval_token: str = ""
    memory_dir: str = "data/memory"
    webhook_enabled: bool = False

settings = Settings()