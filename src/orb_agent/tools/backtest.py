from langchain_core.tools import tool

@tool
def run_orb_backtest(pair: str) -> dict:
    """Executa backtest walk-forward para o par."""
    return {"pair": pair, "win_rate": 0.0, "profit_factor": 0.0}