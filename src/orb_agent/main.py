import argparse
import json

from orb_agent.config.settings import settings
from orb_agent.observability.langsmith import configure_tracing
from orb_agent.pipeline.analyze import run_pair_analysis
from orb_agent.tools.analyze import analyze_all_primary_pairs
from orb_agent.tools.backtest import run_backtest_all_pairs, run_orb_backtest


def main():
    configure_tracing()
    p = argparse.ArgumentParser(description="Opening Range Breakout agent")
    p.add_argument("--pair", default="EURUSD")
    p.add_argument("--all", action="store_true", help="Analisar todos os pares ativos")
    p.add_argument("--backtest", action="store_true", help="Executar backtest walk-forward")
    p.add_argument("--json", action="store_true", help="Output JSON formatado")
    args = p.parse_args()

    if args.backtest:
        if args.all:
            payload = run_backtest_all_pairs.invoke({
                "pairs": settings.pairs_list,
                "save_golive": True,
            })
            if args.json:
                print(json.dumps(payload, indent=2, default=str))
            else:
                print(payload["summary"])
        else:
            bt = run_orb_backtest.invoke({"pair": args.pair})
            if args.json:
                print(json.dumps(bt, indent=2, default=str))
            else:
                print(
                    f"{bt['pair']}: {bt['total_trades']} trades · "
                    f"WR {bt.get('win_rate', 0):.1%} · PF {bt.get('profit_factor', 0):.2f}"
                )
        return

    if args.all:
        payload = analyze_all_primary_pairs.invoke({})
        if settings.webhook_enabled:
            from orb_agent.alerts.dispatcher import notify_scan_complete

            notify_scan_complete(payload)
        if args.json:
            print(json.dumps(payload, indent=2, default=str))
        else:
            print(payload.get("summary", ""))
            for pair, info in payload.get("results", {}).items():
                status = "SETUP" if info.get("found") else (info.get("reason") or "sem setup")
                print(f"{pair}: {status}")
        return

    result = run_pair_analysis(args.pair)
    if args.json:
        print(json.dumps(result, indent=2, default=str))
    else:
        print(result)


if __name__ == "__main__":
    main()