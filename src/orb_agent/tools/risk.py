from langchain_core.tools import tool

@tool
def check_risk_limits(pair: str, risk_percent: float, mode: str) -> dict:
    return {"approved": mode != "live", "reason": None}