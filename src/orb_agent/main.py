import argparse
import json

from orb_agent.config.settings import settings
from orb_agent.pipeline.analyze import run_pair_analysis
from orb_agent.tools.backtest import run_backtest_all_pairs, run_orb_backtest


def main():
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

    pairs = settings.pairs_list if args.all else [args.pair]
    results = [run_pair_analysis(pair) for pair in pairs]

    if args.json:
        print(json.dumps(results if args.all else results[0], indent=2, default=str))
    elif args.all:
        for item in results:
            if item.get("found"):
                tp = item.get("trade_params") or {}
                bt = item.get("backtest") or {}
                status = (
                    f"SETUP R:R 1:{tp.get('risk_reward', '?')} · "
                    f"BT WR {bt.get('win_rate', 0):.0%}"
                )
            else:
                status = item.get("reason", "sem setup")
            print(f"{item['pair']}: {status}")
    else:
        print(results[0])


if __name__ == "__main__":
    main()