from concurrent.futures import ThreadPoolExecutor, as_completed
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
    """Analisa todos os pares ativos configurados (paralelo quando scan_workers > 1)."""
    pairs = settings.pairs_list
    workers = max(1, min(settings.scan_workers, len(pairs)))
    results: dict[str, Any] = {}

    if workers == 1 or len(pairs) == 1:
        for pair in pairs:
            results[pair] = run_pair_analysis(pair)
    else:
        with ThreadPoolExecutor(max_workers=workers) as pool:
            futures = {pool.submit(run_pair_analysis, p): p for p in pairs}
            for future in as_completed(futures):
                pair = futures[future]
                results[pair] = future.result()

    found = sum(1 for info in results.values() if info.get("found"))
    return {
        "results": results,
        "summary": f"Scan {len(pairs)} pares · {found} setup(s) encontrado(s)",
        "found_count": found,
        "parallel_workers": workers,
    }