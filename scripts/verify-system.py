#!/usr/bin/env python3
"""Verificacao end-to-end do sistema ORB."""

import sys

from orb_agent.audit.rotation import maybe_rotate_audit_log
from orb_agent.guardrails.live_gate import live_gate_status
from orb_agent.metrics.collector import collect_metrics
from orb_agent.paper.alerts import check_paper_alerts
from orb_agent.pipeline.analyze import run_pair_analysis
from orb_agent.providers.ohlcv_cache import cache_stats
from orb_agent.tools.backtest import run_orb_backtest


def main() -> int:
    errors: list[str] = []

    print("=== Verificacao ORB Agent ===\n")

    print("[1] Pipeline analise (stub/CCXT)")
    for pair in ["EURUSD", "XAUUSD"]:
        result = run_pair_analysis(pair)
        src = result.get("data_source")
        if src not in ("ccxt", "stub"):
            errors.append(f"{pair}: data_source inesperado {src}")
        if "paper_alerts" not in result:
            errors.append(f"{pair}: paper_alerts ausente")
        print(f"  {pair}: found={result.get('found')} source={src}")

    print("\n[2] Backtest EURUSD")
    bt = run_orb_backtest.invoke({"pair": "EURUSD"})
    if bt.get("data_source") not in ("ccxt", "stub", None):
        errors.append(f"backtest source: {bt.get('data_source')}")
    print(f"  trades={bt.get('total_trades')} source={bt.get('data_source')}")

    print("\n[3] Metricas")
    metrics = collect_metrics()
    if "kpis" not in metrics:
        errors.append("metricas sem kpis")
    print(f"  mode={metrics.get('mode')} paper={metrics['kpis'].get('open_paper_positions')}")

    print("\n[4] Live gate")
    gate = live_gate_status()
    if gate["allowed"] and gate["mode"] != "live":
        errors.append("live gate allowed fora de live")
    print(f"  mode={gate['mode']} allowed={gate['allowed']}")

    print("\n[5] Paper alerts")
    pa = check_paper_alerts()
    if "alerts" not in pa:
        errors.append("paper alerts sem campo alerts")
    print(f"  {pa.get('message')}")

    print("\n[6] Cache OHLCV")
    stats = cache_stats()
    print(f"  enabled={stats.get('enabled')} files={stats.get('files')}")

    print("\n[7] Audit rotation check")
    rot = maybe_rotate_audit_log()
    print(f"  rotated={rot.get('rotated')} size_mb={rot.get('size_mb', 'n/a')}")

    print("\n=== Resultado ===")
    if errors:
        for err in errors:
            print(f"  FAIL: {err}")
        return 1
    print("  OK — sistema funcionando como esperado")
    return 0


if __name__ == "__main__":
    sys.exit(main())