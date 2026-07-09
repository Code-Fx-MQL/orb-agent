"""Painel Streamlit — Live Ops, go-live e operacoes de producao."""

from __future__ import annotations

import streamlit as st

from orb_agent.alerts.telegram_messages import format_generic_message
from orb_agent.alerts.webhooks import send_telegram, send_webhook, telegram_status
from orb_agent.audit.logger import get_audit_logger
from orb_agent.guardrails.live_gate import live_gate_status, set_live_session_token
from orb_agent.ops.golive import CORE_PAIRS, get_ops_snapshot
from orb_agent.paper.alerts import check_paper_alerts
from orb_agent.tools.analyze import analyze_all_primary_pairs


def _status_badge(status: str) -> str:
    return {"ok": "OK", "warn": "!", "fail": "X", "pending": "..."}.get(status, "...")


def _render_checklist(checklist: dict) -> None:
    overall = checklist.get("overall", "pending")
    st.markdown(f"### {_status_badge(overall)} {checklist.get('overall_label', 'Status')}")
    st.caption(
        f"Bloqueadores: **{checklist.get('blockers', 0)}** · "
        f"Avisos: **{checklist.get('warnings', 0)}** · "
        f"Pares core: {', '.join(checklist.get('core_pairs', CORE_PAIRS))}",
    )

    rows = []
    for item in checklist.get("items", []):
        rows.append({
            "": _status_badge(item.get("status", "pending")),
            "Item": item.get("label", ""),
            "Status": item.get("status", "").upper(),
            "Detalhe": item.get("detail", ""),
        })
    st.dataframe(rows, use_container_width=True, hide_index=True)

    if checklist.get("backtest_summary"):
        st.caption(f"Ultimo backtest go-live: {checklist['backtest_summary']}")


def _render_gate(gate: dict) -> None:
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Modo", str(gate.get("mode", "—")).upper())
    c2.metric("Aprovado (.env)", "Sim" if gate.get("approved_env") else "Nao")
    c3.metric("Token config.", "Sim" if gate.get("token_configured") else "Nao")
    c4.metric("Broker", str(gate.get("broker_mode", "stub")))

    if gate.get("allowed"):
        st.success(f"Live gate: {gate.get('reason')}")
    else:
        st.warning(f"Live gate: {gate.get('reason')}")

    with st.expander("Testar token de sessao (nao persiste no .env)"):
        token = st.text_input("Token de sessao", type="password", key="live_ops_token")
        if st.button("Validar token", key="btn_validate_token"):
            set_live_session_token(token or None)
            status = live_gate_status()
            if status["allowed"]:
                st.success("Token valido — live gate autorizado nesta sessao")
            else:
                st.error(status["reason"])


def _render_actions() -> None:
    st.subheader("Acoes operacionais")
    col_scan, col_webhook, col_telegram, col_alerts = st.columns(4)

    with col_scan:
        if st.button("Executar scan", key="btn_live_scan", type="primary"):
            with st.spinner("Scan dos pares prioritarios..."):
                result = analyze_all_primary_pairs.invoke({})
                from orb_agent.alerts.dispatcher import notify_scan_complete, notify_setup_found

                notify_scan_complete(result)
                setups = 0
                for pair, data in result.get("results", {}).items():
                    if data.get("found"):
                        notify_setup_found(pair, data)
                        setups += 1
                st.session_state["last_scan"] = {
                    "summary": result.get("summary", ""),
                    "setups": setups,
                    "results": result.get("results", {}),
                }

    with col_webhook:
        if st.button("Testar webhook", key="btn_test_webhook"):
            with st.spinner("Enviando test_ping..."):
                result = send_webhook(
                    event_type="test_ping",
                    title="Teste Live Ops",
                    body="Ping do dashboard ORB Agent.",
                    level="success",
                    data={"source": "live_ops_panel", "test": True},
                )
                st.session_state["last_webhook"] = result

    with col_telegram:
        if st.button("Testar Telegram", key="btn_test_telegram"):
            tg = telegram_status()
            if not tg["ready"]:
                st.session_state["last_telegram"] = {
                    "sent": False,
                    "reason": "Configure ORB_TELEGRAM_ENABLED, ORB_TELEGRAM_BOT_TOKEN e ORB_TELEGRAM_CHAT_ID",
                }
            else:
                with st.spinner("Enviando Telegram..."):
                    msg = format_generic_message(
                        "Teste Live Ops",
                        "Telegram do harness ORB Agent operacional.",
                        "success",
                    )
                    st.session_state["last_telegram"] = send_telegram(msg, parse_mode="HTML")

    with col_alerts:
        if st.button("Verificar SL/TP", key="btn_live_alerts"):
            with st.spinner("Verificando paper..."):
                st.session_state["last_paper_alerts"] = check_paper_alerts()

    if st.session_state.get("last_scan"):
        scan = st.session_state["last_scan"]
        st.success(f"Scan: {scan.get('summary', '')} · {scan.get('setups', 0)} setup(s)")

    if st.session_state.get("last_webhook"):
        wh = st.session_state["last_webhook"]
        if wh.get("sent"):
            st.success(f"Webhook enviado · event_type={wh.get('event_type')}")
        else:
            st.error(f"Webhook falhou: {wh}")

    if st.session_state.get("last_telegram"):
        tg = st.session_state["last_telegram"]
        if tg.get("sent"):
            st.success("Telegram enviado")
        else:
            st.error(f"Telegram falhou: {tg.get('reason', tg)}")

    if st.session_state.get("last_paper_alerts"):
        alerts = st.session_state["last_paper_alerts"]
        for alert in alerts.get("alerts", []):
            if alert.get("type") == "tp_hit":
                st.success(alert.get("message", ""))
            else:
                st.error(alert.get("message", ""))
        if not alerts.get("alerts"):
            st.info(alerts.get("message", "Sem alertas"))


def _render_audit() -> None:
    recent = get_audit_logger().recent(limit=15)
    if not recent:
        st.caption("Nenhum evento no audit log")
        return

    rows = []
    for entry in recent:
        rows.append({
            "Hora": entry.get("timestamp", "")[:19].replace("T", " "),
            "Evento": entry.get("event", ""),
            "Modo": entry.get("mode", ""),
        })
    st.dataframe(rows, use_container_width=True, hide_index=True)


def render_live_ops_tab() -> None:
    snapshot = get_ops_snapshot()
    checklist = snapshot["checklist"]
    gate = snapshot["gate"]

    st.subheader("Live Ops")
    st.caption("Painel operacional — go-live, gate, scan e webhooks")

    overall = checklist.get("overall", "pending")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Go-live", overall.upper(), delta=checklist.get("overall_label", ""))
    m2.metric("Pares ativos", snapshot.get("pairs_count", 0))
    m3.metric("Paper abertas", snapshot["metrics"]["kpis"].get("open_paper_positions", 0))
    bt = snapshot.get("backtest_totals") or {}
    m4.metric("Backtest WR", f"{bt.get('win_rate', 0):.1%}" if bt else "—")

    tab_status, tab_actions, tab_audit = st.tabs(["Checklist", "Acoes", "Audit"])

    with tab_status:
        _render_checklist(checklist)
        st.divider()
        _render_gate(gate)

        filters = snapshot.get("filters", {})
        f1, f2, f3 = st.columns(3)
        f1.write(f"Breakout: **{filters.get('breakout_mode')}**")
        f2.write(f"Retest: **{'sim' if filters.get('require_retest') else 'nao'}**")
        f3.write(f"OR candles: **{filters.get('session_candles')}**")

        wh = snapshot.get("webhook", {})
        if wh.get("enabled") and wh.get("url_configured"):
            st.success(f"Webhook: {wh.get('app_id')} → {wh.get('url_host', 'configurado')}")
        else:
            st.warning("Webhook nao configurado")

        tg = snapshot.get("telegram", {})
        if tg.get("ready"):
            st.success("Telegram: ativo")
        elif tg.get("configured"):
            st.warning("Telegram: configurado mas ORB_TELEGRAM_ENABLED=false")
        else:
            st.warning("Telegram nao configurado")

    with tab_actions:
        _render_actions()

    with tab_audit:
        _render_audit()