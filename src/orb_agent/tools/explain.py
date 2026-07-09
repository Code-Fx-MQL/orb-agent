from langchain_core.tools import tool

@tool
def explain_setup_detalhado(setup: dict, trade: dict) -> str:
    return "Explicacao stub."

@tool
def log_trade_outcome(setup_id: str, outcome: str) -> dict:
    return {"logged": True, "setup_id": setup_id}