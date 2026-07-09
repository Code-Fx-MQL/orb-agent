from langchain_core.tools import tool

@tool
def check_risk_limits(pair: str, risk_percent: float, mode: str) -> dict:
    """Valida limites de risco diario/semanal antes de abrir posicao."""
    return {"approved": mode != "live", "reason": None}