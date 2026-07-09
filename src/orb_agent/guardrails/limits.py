from datetime import date

from orb_agent.config.settings import settings


def _week_key() -> str:
    today = date.today()
    return f"{today.isocalendar().year}-W{today.isocalendar().week:02d}"


class RiskTracker:
    def __init__(self) -> None:
        self._daily_risk: dict[date, float] = {}
        self._weekly_risk: dict[str, float] = {}

    @property
    def daily_risk_used(self) -> float:
        return self._daily_risk.get(date.today(), 0.0)

    @property
    def weekly_risk_used(self) -> float:
        return self._weekly_risk.get(_week_key(), 0.0)

    def can_take_trade(self, risk_percent: float) -> tuple[bool, str]:
        if risk_percent > settings.max_risk_per_trade:
            return False, f"Risco por trade excede {settings.max_risk_per_trade:.1%}"
        if self.daily_risk_used + risk_percent > settings.max_daily_risk:
            return False, f"Risco diario excederia {settings.max_daily_risk:.1%}"
        if self.weekly_risk_used + risk_percent > settings.max_weekly_risk:
            return False, f"Risco semanal excederia {settings.max_weekly_risk:.1%}"
        return True, "OK"

    def record_trade_risk(self, risk_percent: float) -> None:
        today = date.today()
        self._daily_risk[today] = self.daily_risk_used + risk_percent
        wk = _week_key()
        self._weekly_risk[wk] = self.weekly_risk_used + risk_percent