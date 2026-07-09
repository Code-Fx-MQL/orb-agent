from langchain_core.tools import tool

@tool
def calculate_trade_params(setup: dict) -> dict:
    return {"valid": False, "reason": "stub"}

@tool
def identify_confluences(setup: dict) -> dict:
    return {"confluences": [], "strength": "weak"}