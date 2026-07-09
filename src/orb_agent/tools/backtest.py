from langchain_core.tools import tool

@tool
def run_orb_backtest(pair: str) -> dict:
    return {"pair": pair, "win_rate": 0.0, "profit_factor": 0.0}