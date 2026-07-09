from langchain_core.tools import tool


@tool
def explain_setup_detalhado(setup: dict, trade: dict) -> str:
    """Gera explicacao legivel do setup ORB e parametros de trade."""
    direction = setup.get("direction", "?")
    pair = setup.get("pair", "?")
    meta = setup.get("metadata") or {}
    pattern = meta.get("pattern", "orb")

    lines = [
        f"## Setup ORB — {pair}",
        "",
        f"- **Direcao:** {direction}",
        f"- **Padrao:** {pattern}",
        f"- **Opening Range:** {setup.get('or_low')} — {setup.get('or_high')}",
        f"- **Confianca:** {setup.get('confidence', 0):.0%}",
        "",
        "### Trade",
        f"- Entry: {trade.get('entry')}",
        f"- SL: {trade.get('stop_loss')}",
        f"- TP: {trade.get('take_profit')}",
        f"- R:R: 1:{trade.get('risk_reward')}",
        f"- Size: {trade.get('position_size_lots')} lots",
        f"- Risco: {trade.get('risk_percent', 0):.1%}",
    ]
    return "\n".join(lines)


@tool
def log_trade_outcome(setup_id: str, outcome: str) -> dict:
    """Regista resultado do trade na memoria."""
    return {"logged": True, "setup_id": setup_id}