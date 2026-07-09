"""Componentes de producao — header ops e auto-refresh."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from html import escape
from typing import Any

import streamlit as st

from orb_agent.alerts.webhooks import telegram_status, webhook_status
from orb_agent.config.settings import settings
from orb_agent.metrics.collector import collect_metrics
from orb_agent.ops.golive import get_golive_checklist
from orb_agent.observability.langsmith import is_tracing_enabled
from orb_agent.paper.alerts import check_paper_alerts
from orb_agent.paper.store import get_paper_store


def _status_class(status: str) -> str:
    return {"ok": "ok", "warn": "warn", "fail": "fail"}.get(status, "info")


def _format_refresh_time(iso_ts: str | None) -> str:
    if not iso_ts:
        return "—"
    try:
        dt = datetime.fromisoformat(iso_ts.replace("Z", "+00:00"))
        return dt.astimezone().strftime("%H:%M:%S")
    except ValueError:
        return iso_ts[:19]


def refresh_live_data() -> dict[str, Any]:
    """Atualiza cache de metricas e alertas paper."""
    metrics = collect_metrics()
    paper = get_paper_store().summary()
    alerts = check_paper_alerts()
    checklist = get_golive_checklist()
    payload = {
        "metrics": metrics,
        "paper": paper,
        "alerts": alerts,
        "checklist_overall": checklist.get("overall", "pending"),
        "checklist_label": checklist.get("overall_label", ""),
        "refreshed_at": datetime.now(UTC).isoformat(),
    }
    st.session_state["orb_live_data"] = payload
    return payload


def get_live_data() -> dict[str, Any]:
    if "orb_live_data" not in st.session_state:
        return refresh_live_data()
    return st.session_state["orb_live_data"]


def _ops_item(label: str, value: str, css: str = "info") -> str:
    return (
        f'<div class="orb-ops-item">'
        f'<div class="orb-ops-label">{escape(label)}</div>'
        f'<div class="orb-ops-value {css}">{escape(value)}</div>'
        f"</div>"
    )


def render_ops_header() -> None:
    """Barra superior com status operacional."""
    live = get_live_data()
    metrics = live.get("metrics", {})
    kpis = metrics.get("kpis", {})
    paper_open = kpis.get("open_paper_positions", 0)
    webhook = webhook_status()
    golive = live.get("checklist_overall", "pending")
    golive_label = live.get("checklist_label", golive.upper())

    items = [
        _ops_item("Modo", settings.mode.value.upper(), "info"),
        _ops_item("Go-live", golive_label[:28], _status_class(golive)),
        _ops_item("Paper abertas", str(paper_open), "ok" if paper_open == 0 else "warn"),
        _ops_item(
            "Webhook",
            "Ativo" if webhook.get("ready") else "Off",
            "ok" if webhook.get("ready") else "warn",
        ),
        _ops_item(
            "Telegram",
            "Ativo" if telegram_status().get("ready") else "Off",
            "ok" if telegram_status().get("ready") else "warn",
        ),
        _ops_item(
            "LangSmith",
            "On" if is_tracing_enabled() else "Off",
            "ok" if is_tracing_enabled() else "warn",
        ),
        _ops_item("Refresh", _format_refresh_time(live.get("refreshed_at")), "info"),
    ]
    st.markdown(f'<div class="orb-ops-bar">{"".join(items)}</div>', unsafe_allow_html=True)


def render_auto_refresh_controls() -> None:
    st.sidebar.divider()
    st.sidebar.subheader("Auto-refresh")
    enabled = settings.ui_auto_refresh_enabled
    interval = int(settings.ui_auto_refresh_seconds)
    if enabled:
        st.sidebar.caption(f"Atualiza a cada **{interval // 60} min** ({interval}s)")
        if st.sidebar.button("Atualizar agora", key="btn_refresh_now"):
            refresh_live_data()
            st.rerun()
    else:
        st.sidebar.caption("Desativado — `ORB_UI_AUTO_REFRESH_ENABLED=false`")


def setup_auto_refresh() -> None:
    if not settings.ui_auto_refresh_enabled:
        return

    interval = max(30, int(settings.ui_auto_refresh_seconds))

    @st.fragment(run_every=timedelta(seconds=interval))
    def _auto_refresh_fragment() -> None:
        previous = st.session_state.get("orb_live_data", {}).get("refreshed_at")
        refresh_live_data()
        alerts = st.session_state.get("orb_live_data", {}).get("alerts", {})
        new_alerts = alerts.get("alerts", [])
        old_count = st.session_state.get("orb_alert_count", 0)
        if len(new_alerts) > old_count:
            st.session_state["orb_alert_count"] = len(new_alerts)
            st.toast(f"{len(new_alerts)} alerta(s) paper", icon="🔔")
        elif previous != st.session_state.get("orb_live_data", {}).get("refreshed_at"):
            st.toast("Dados atualizados", icon="🔄")

    _auto_refresh_fragment()