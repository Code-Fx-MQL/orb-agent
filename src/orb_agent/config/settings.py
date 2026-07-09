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
    default_htf: str = "1d"
    default_mtf: str = "1h"
    default_ltf: str = "15m"
    orb_session_candles: int = 1
    orb_breakout_mode: str = "retest"
    orb_require_retest: bool = True
    max_risk_per_trade: float = 0.01
    max_daily_risk: float = 0.03
    max_weekly_risk: float = 0.06
    block_news: bool = True
    live_approved: bool = False
    live_approval_token: str = ""
    memory_dir: str = "data/memory"
    webhook_enabled: bool = False
    ccxt_ohlcv_limit: int = 100
    ccxt_timeout_ms: int = 30000
    ccxt_api_key: str = ""
    ccxt_api_secret: str = ""
    backtest_candle_limit: int = 500
    backtest_htf_lookback: int = 30
    backtest_mtf_lookback: int = 48

    @property
    def pairs_list(self) -> list[str]:
        return [p.strip().upper() for p in self.pairs.split(",") if p.strip()]

settings = Settings()