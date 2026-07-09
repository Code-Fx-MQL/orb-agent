from langchain_core.tools import tool

@tool
def explain_setup_detalhado(setup: dict, trade: dict) -> str:
    """Gera explicacao legivel do setup e parametros de trade."""
    return "Explicacao stub."

@tool
def log_trade_outcome(setup_id: str, outcome: str) -> dict:
    """Regista resultado do trade na memoria."""
    return {"logged": True, "setup_id": setup_id}