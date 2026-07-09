"""Formatacao de mensagens Telegram para alertas ORB."""

from __future__ import annotations

from typing import Any


def _esc(text: object) -> str:
    s = str(text) if text is not None else "—"
    return (
        s.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def format_setup_found_message(data: dict[str, Any]) -> str:
    conf = data.get("confluences") or {}
    bt = data.get("backtest") or {}
    setup = data.get("setup") or {}
    kpi = "sim" if bt.get("meets_kpi") else "nao"

    return (
        f"<b>ORB Agent — Setup detectado</b>\n\n"
        f"<b>Par:</b> {_esc(data.get('pair'))}\n"
        f"<b>Setup ID:</b> {_esc(data.get('setup_id'))}\n"
        f"<b>Direcao:</b> {_esc(data.get('direction'))}\n"
        f"<b>Confianca:</b> {float(data.get('confidence') or 0):.0%}\n\n"
        f"<b>Trade</b>\n"
        f"E {_esc(data.get('entry'))} · SL {_esc(data.get('stop_loss'))} · "
        f"TP {_esc(data.get('take_profit'))}\n"
        f"R:R {_esc(data.get('risk_reward'))}\n\n"
        f"<b>OR:</b> {_esc(setup.get('or_low'))} — {_esc(setup.get('or_high'))}\n"
        f"<b>Confluencia:</b> {_esc(conf.get('strength'))} "
        f"({conf.get('confluence_count', 0)})\n"
        f"<b>Backtest KPI:</b> {kpi}\n"
        f"<b>Fonte:</b> {_esc(data.get('data_source'))} ({_esc(data.get('exchange'))})\n\n"
        f"<i>Revisao IA no n8n em curso — aguardar decisao approve/reject.</i>"
    )


def format_paper_alert_message(data: dict[str, Any]) -> str:
    icon = "TP" if data.get("type") == "tp_hit" else "SL"
    return (
        f"<b>Paper {_esc(data.get('pair'))}</b> [{icon}]\n"
        f"{_esc(data.get('message', ''))}"
    )


def format_scan_complete_message(data: dict[str, Any], summary: str) -> str:
    found = data.get("setups_found") or []
    pairs = ", ".join(found) if found else "nenhum"
    return (
        f"<b>Scan ORB concluido</b>\n"
        f"{_esc(summary)}\n"
        f"<b>Setups:</b> {_esc(pairs)}"
    )


def format_generic_message(title: str, body: str, level: str) -> str:
    emoji = {"info": "i", "success": "OK", "warning": "!", "error": "X", "trade": "$"}.get(level, "*")
    return f"{emoji} <b>{_esc(title)}</b>\n{_esc(body)}"