from orb_agent.tools.analyze import analyze_all_primary_pairs, analyze_pair
from orb_agent.tools.backtest import run_orb_backtest
from orb_agent.tools.data import fetch_multi_tf_data
from orb_agent.tools.explain import explain_setup_detalhado, log_trade_outcome
from orb_agent.tools.orb import detect_orb_setup
from orb_agent.tools.risk import check_risk_limits
from orb_agent.tools.trade import calculate_trade_params, identify_confluences


def get_all_tools():
    return [
        fetch_multi_tf_data,
        detect_orb_setup,
        identify_confluences,
        calculate_trade_params,
        run_orb_backtest,
        explain_setup_detalhado,
        check_risk_limits,
        log_trade_outcome,
        analyze_pair,
        analyze_all_primary_pairs,
    ]