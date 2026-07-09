class RiskTracker:
    def can_take_trade(self, risk_percent: float) -> bool:
        return risk_percent <= 0.01