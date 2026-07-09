import argparse
from orb_agent.pipeline.analyze import run_pair_analysis

def main():
    p = argparse.ArgumentParser(description="Opening Range Breakout agent")
    p.add_argument("--pair", default="XAUUSD")
    args = p.parse_args()
    result = run_pair_analysis(args.pair)
    print(result)

if __name__ == "__main__":
    main()