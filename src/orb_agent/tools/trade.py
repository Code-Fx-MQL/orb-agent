from langchain_core.tools import tool

@tool
def calculate_trade_params(setup: dict) -> dict:
    """Calcula entry, SL, TP e sizing a partir do setup."""
    return {"valid": False, "reason": "stub"}

@tool
def identify_confluences(setup: dict) -> dict:
    """Lista confluencias do setup detectado."""
    return {"confluences": [], "strength": "weak"}