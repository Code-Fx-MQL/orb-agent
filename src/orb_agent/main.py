import argparse
import json

from orb_agent.config.settings import settings
from orb_agent.pipeline.analyze import run_pair_analysis


def main():
    p = argparse.ArgumentParser(description="Opening Range Breakout agent")
    p.add_argument("--pair", default="EURUSD")
    p.add_argument("--all", action="store_true", help="Analisar todos os pares ativos")
    p.add_argument("--json", action="store_true", help="Output JSON formatado")
    args = p.parse_args()

    pairs = settings.pairs_list if args.all else [args.pair]
    results = [run_pair_analysis(pair) for pair in pairs]

    if args.json:
        print(json.dumps(results if args.all else results[0], indent=2, default=str))
    elif args.all:
        for item in results:
            det = item.get("detection", {})
            status = "SETUP" if det.get("found") else det.get("reason", "sem setup")
            print(f"{item['pair']}: {status}")
    else:
        print(results[0])


if __name__ == "__main__":
    main()