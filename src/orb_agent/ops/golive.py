"""Checklist go-live e snapshot operacional para Live Ops."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from typing import Any, Literal

from orb_agent.alerts.webhooks import webhook_status
from orb_agent.backtest.golive import backtest_golive_path
from orb_agent.config.settings import OperationMode, settings
from orb_agent.guardrails.live_gate import live_gate_status
from orb_agent.metrics.collector import collect_metrics
from orb_agent.paper.store import get_paper_store

CheckStatus = Literal["ok", "warn", "fail", "pending"]

GO_LIVE_WR = 0.55
GO_LIVE_PF = 1.0
MIN_BACKTEST_TRADES = 20
PAPER_MIN_DAYS = 14
CORE_PAIRS = ("XAUUSD", "EURUSD")


def _status_icon(status: CheckStatus) -> str:
    return {"ok": "OK", "warn": "!", "fail": "X", "pending": "..."}[status]


def _load_backtest_golive() -> dict[str, Any] | None:
    path = backtest_golive_path()
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None


def _paper_validation_days() -> tuple[int, CheckStatus, str]:
    store = get_paper_store()
    summary = store.summary()
    timestamps: list[datetime] = []

    for pos in summary.get("open", []) + store.get_closed():
        raw = pos.get("opened_at")
        if not raw:
            continue
        try:
            timestamps.append(datetime.fromisoformat(str(raw).replace("Z", "+00:00")))
        except ValueError:
            continue

    if not timestamps:
        return 0, "fail", "Nenhuma posicao paper — iniciar validacao"

    earliest = min(timestamps)
    now = datetime.now(UTC)
    if earliest.tzinfo is None:
        earliest = earliest.replace(tzinfo=UTC)
    days = (now - earliest).days

    if days >= PAPER_MIN_DAYS:
        return days, "ok", f"{days} dias de paper trading"
    return days, "warn", f"{days}/{PAPER_MIN_DAYS} dias — minimo 2 semanas"


def _evaluate_backtest(bt: dict[str, Any] | None) -> dict[str, Any]:
    if not bt:
        return {
            "id": "backtest_kpi",
            "label": "Backtest com KPIs",
            "status": "fail",
            "detail": "Arquivo data/backtest_golive.json ausente — rodar orb-agent --backtest --all",
        }

    totals = bt.get("totals", {})
    total_trades = int(totals.get("total_trades", 0))
    wr = float(totals.get("win_rate", 0))
    pf = float(totals.get("profit_factor", 0))
    pairs_kpi = int(totals.get("pairs_meeting_kpi", 0))

    global_ok = wr >= GO_LIVE_WR and pf >= GO_LIVE_PF and total_trades >= MIN_BACKTEST_TRADES
    core_ok = all(
        bt.get("results", {}).get(p, {}).get("meets_kpi") for p in CORE_PAIRS
    )

    if global_ok and core_ok:
        status: CheckStatus = "ok"
    elif wr >= GO_LIVE_WR and pf >= GO_LIVE_PF:
        status = "warn"
    else:
        status = "fail"

    detail = (
        f"{total_trades} trades · WR {wr:.1%} · PF {pf:.2f} · "
        f"{pairs_kpi} pares KPI · core "
        f"{sum(1 for p in CORE_PAIRS if bt.get('results', {}).get(p, {}).get('meets_kpi'))}/"
        f"{len(CORE_PAIRS)}"
    )
    if total_trades < MIN_BACKTEST_TRADES:
        detail += f" · amostra < {MIN_BACKTEST_TRADES}"

    return {
        "id": "backtest_kpi",
        "label": "Backtest com KPIs",
        "status": status,
        "detail": detail,
        "metrics": {"trades": total_trades, "win_rate": wr, "profit_factor": pf, "pairs_kpi": pairs_kpi},
    }


def _ui_auth_status() -> dict[str, bool]:
    configured = bool(settings.ui_password)
    return {"enabled": configured, "ready": configured}


def get_golive_checklist() -> dict[str, Any]:
    gate = live_gate_status()
    paper_days, paper_status, paper_detail = _paper_validation_days()
    bt = _load_backtest_golive()
    auth = _ui_auth_status()
    webhook = webhook_status()

    approval_ok = bool(gate["approved_env"]) and bool(gate["token_configured"])
    broker_mode = str(gate.get("broker_mode", "stub"))

    items: list[dict[str, Any]] = [
        _evaluate_backtest(bt),
        {
            "id": "paper_validation",
            "label": f"Paper trading ({PAPER_MIN_DAYS} dias)",
            "status": paper_status,
            "detail": paper_detail,
            "metrics": {"days": paper_days, "min_days": PAPER_MIN_DAYS},
        },
        {
            "id": "human_approval",
            "label": "Aprovacao humana dupla",
            "status": "ok" if approval_ok else "fail",
            "detail": (
                "ORB_LIVE_APPROVED + token configurados"
                if approval_ok
                else "Definir ORB_LIVE_APPROVED=true e ORB_LIVE_APPROVAL_TOKEN no .env"
            ),
        },
        {
            "id": "broker",
            "label": "Broker validado",
            "status": "ok" if broker_mode == "ccxt" else "warn",
            "detail": f"ORB_BROKER_MODE={broker_mode}" + (" (simulado)" if broker_mode == "stub" else ""),
        },
        {
            "id": "guardrails",
            "label": "Guardrails de risco",
            "status": "ok",
            "detail": (
                f"1%/{settings.max_daily_risk:.0%}/{settings.max_weekly_risk:.0%} · "
                f"news={'on' if settings.block_news else 'off'} · "
                f"retest={'on' if settings.orb_require_retest else 'off'}"
            ),
        },
        {
            "id": "webhooks",
            "label": "Webhooks n8n",
            "status": "ok" if webhook.get("ready") else "warn",
            "detail": (
                f"Ativo → {settings.webhook_url}"
                if webhook.get("ready")
                else "WEBHOOK_ENABLED ou WEBHOOK_URL nao configurados"
            ),
        },
        {
            "id": "ui_auth",
            "label": "Protecao dashboard",
            "status": "ok" if auth["ready"] else "warn",
            "detail": (
                "ORB_UI_PASSWORD configurada"
                if auth["ready"]
                else "Auth desativado — definir ORB_UI_PASSWORD em producao"
            ),
        },
        {
            "id": "live_gate",
            "label": "Live gate operacional",
            "status": "ok" if gate["allowed"] else ("warn" if settings.mode == OperationMode.LIVE else "pending"),
            "detail": str(gate["reason"]),
        },
    ]

    blockers = [i for i in items if i["status"] == "fail"]
    warnings = [i for i in items if i["status"] == "warn"]

    if not blockers and not warnings:
        overall: CheckStatus = "ok"
    elif not blockers:
        overall = "warn"
    else:
        overall = "fail"

    return {
        "overall": overall,
        "overall_label": {
            "ok": "Pronto para go-live (com aprovacao humana)",
            "warn": "Quase pronto — revisar avisos",
            "fail": "Bloqueado — corrigir itens criticos",
        }[overall],
        "items": items,
        "blockers": len(blockers),
        "warnings": len(warnings),
        "core_pairs": list(CORE_PAIRS),
        "backtest_summary": bt.get("summary") if bt else None,
    }


def get_ops_snapshot() -> dict[str, Any]:
    gate = live_gate_status()
    metrics = collect_metrics()
    checklist = get_golive_checklist()
    bt = _load_backtest_golive()
    webhook = webhook_status()

    return {
        "timestamp": datetime.now(UTC).isoformat(),
        "mode": settings.mode.value,
        "pairs_count": len(settings.pairs_list),
        "pairs": settings.pairs_list,
        "gate": gate,
        "checklist": checklist,
        "metrics": metrics,
        "webhook": {
            "enabled": webhook.get("enabled"),
            "url_configured": webhook.get("configured"),
            "app_id": settings.webhook_app_id,
            "url_host": (
                settings.webhook_url.split("/")[2]
                if settings.webhook_url and "://" in settings.webhook_url
                else None
            ),
        },
        "filters": {
            "breakout_mode": settings.orb_breakout_mode,
            "require_retest": settings.orb_require_retest,
            "session_candles": settings.orb_session_candles,
        },
        "backtest_totals": bt.get("totals") if bt else None,
        "langsmith": settings.langsmith_tracing,
    }


def format_checklist_row(item: dict[str, Any]) -> str:
    status = item.get("status", "pending")
    return f"{_status_icon(status)} {item.get('label', '')} — {item.get('detail', '')}"