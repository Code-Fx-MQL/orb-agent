from typing import Any

from langchain_core.tools import tool

from orb_agent.config.settings import settings
from orb_agent.pipeline.analyze import run_pair_analysis


@tool
def analyze_pair(pair: str) -> dict:
    """Executa analise completa para um par."""
    return run_pair_analysis(pair)


@tool
def analyze_all_primary_pairs() -> dict[str, Any]:
    """Analisa todos os pares ativos configurados."""
    results: dict[str, Any] = {}
    found = 0
    for pair in settings.pairs_list:
        info = run_pair_analysis(pair)
        results[pair] = info
        if info.get("found"):
            found += 1
    return {
        "results": results,
        "summary": f"Scan {len(settings.pairs_list)} pares · {found} setup(s) encontrado(s)",
        "found_count": found,
    }