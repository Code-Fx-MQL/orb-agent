from langchain_core.tools import tool
from orb_agent.pipeline.analyze import run_pair_analysis

@tool
def analyze_pair(pair: str) -> dict:
    """Executa analise completa para um par."""
    return run_pair_analysis(pair)