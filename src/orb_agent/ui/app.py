"""Dashboard Streamlit — Agente ORB."""

from __future__ import annotations

from typing import Any

import streamlit as st

from orb_agent.audit.logger import get_audit_logger
from orb_agent.config.settings import settings
from orb_agent.memory.store import get_memory
from orb_agent.metrics.collector import collect_metrics
from orb_agent.observability.langsmith import configure_tracing, is_tracing_enabled
from orb_agent.paper.alerts import check_paper_alerts
from orb_agent.paper.store import get_paper_store
from orb_agent.pipeline.analyze import run_pair_analysis
from orb_agent.tools.analyze import analyze_all_primary_pairs
from orb_agent.tools.backtest import run_backtest_all_pairs, run_orb_backtest
from orb_agent.tools.data import fetch_multi_tf_data
from orb_agent.ui.charts import build_multi_tf_charts, build_orb_chart
from orb_agent.ui.live_ops_panel import render_live_ops_tab
from orb_agent.ui.production import (
    render_auto_refresh_controls,
    render_ops_header,
    setup_auto_refresh,
)
from orb_agent.ui.theme import inject_theme


def _check_ui_auth() -> bool:
    if not settings.ui_password:
        return True
    if st.session_state.get("orb_ui_authed"):
        return True
    st.subheader("Login")
    pwd = st.text_input("Password", type="password")
    if st.button("Entrar"):
        if pwd == settings.ui_password:
            st.session_state["orb_ui_authed"] = True
            st.rerun()
        else:
            st.error("Password invalida")
    return False


def _render_setup(result: dict[str, Any]) -> None:
    if not result.get("found"):
        st.warning(result.get("reason") or "Nenhum setup ORB detectado.")
        return

    setup = result.get("setup") or {}
    trade = result.get("trade_params") or {}
    conf = result.get("confluences") or {}

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Direcao", str(setup.get("direction", "—")).upper())
    c2.metric("Confianca", f"{setup.get('confidence', 0):.0%}")
    c3.metric("R:R", f"1:{trade.get('risk_reward', 0)}")
    c4.metric("OR", f"{setup.get('or_low')} — {setup.get('or_high')}")

    t1, t2, t3 = st.columns(3)
    t1.metric("Entry", trade.get("entry", "—"))
    t2.metric("Stop Loss", trade.get("stop_loss", "—"))
    t3.metric("Take Profit", trade.get("take_profit", "—"))

    if conf.get("confluences"):
        st.subheader("Confluencias")
        for item in conf["confluences"]:
            st.write(f"• {item}")

    risk = result.get("risk_check") or {}
    if risk.get("approved"):
        st.success("Risco aprovado")
    elif risk:
        st.error(risk.get("reason", "Bloqueado"))

    bt = result.get("backtest") or {}
    if bt and not bt.get("error"):
        st.caption(
            f"Backtest: {bt.get('total_trades', 0)} trades · "
            f"WR {bt.get('win_rate', 0):.0%} · PF {bt.get('profit_factor', 0):.2f}"
        )

    if result.get("explanation"):
        with st.expander("Explicacao"):
            st.markdown(result["explanation"])


def main() -> None:
    st.set_page_config(page_title="Agente ORB", page_icon="📈", layout="wide")
    inject_theme()
    configure_tracing()
    if not _check_ui_auth():
        return

    st.markdown('<p class="orb-title"><strong>Agente ORB</strong> — Opening Range Breakout</p>', unsafe_allow_html=True)
    st.markdown(
        '<p class="orb-subtitle">Top-down: 1D → 1H → 15m · Fase 7 live gate</p>',
        unsafe_allow_html=True,
    )

    pairs = settings.pairs_list
    pair = st.sidebar.selectbox("Par", pairs, index=0)
    st.sidebar.info(f"Modo: **{settings.mode.value}** · Dados: **{settings.data_source}**")
    if is_tracing_enabled():
        st.sidebar.success("LangSmith ativo")
    render_auto_refresh_controls()
    render_ops_header()
    setup_auto_refresh()

    tab_live, tab_analyze, tab_chart, tab_all, tab_backtest, tab_metrics, tab_memory, tab_paper, tab_audit = st.tabs([
        "Live Ops", "Analise", "Grafico", "Todos", "Backtest", "Metricas", "Memoria", "Paper", "Audit",
    ])

    with tab_live:
        render_live_ops_tab()

    with tab_analyze:
        if st.button("Analisar", key="btn_analyze"):
            with st.spinner(f"Analisando {pair}..."):
                result = run_pair_analysis(pair)
            st.session_state["last_result"] = result
            alerts = result.get("paper_alerts") or {}
            for alert in alerts.get("alerts", []):
                if alert["type"] == "tp_hit":
                    st.success(alert["message"])
                else:
                    st.error(alert["message"])

        if "last_result" in st.session_state:
            _render_setup(st.session_state["last_result"])

    with tab_chart:
        tfs = [settings.default_htf, settings.default_mtf, settings.default_ltf]
        multi = st.checkbox("Painel top-down (1D + 1H + 15m)", value=True)
        if st.button("Carregar grafico", key="btn_chart"):
            with st.spinner("OHLCV..."):
                st.session_state["chart_data"] = fetch_multi_tf_data.invoke({
                    "pair": pair,
                    "timeframes": tfs,
                })

        if "chart_data" in st.session_state:
            data = st.session_state["chart_data"]
            setup = trade = None
            last = st.session_state.get("last_result")
            if last and last.get("pair") == pair:
                setup = last.get("setup")
                trade = last.get("trade_params")

            if multi:
                charts = build_multi_tf_charts(
                    data["timeframes"], pair, setup=setup, trade_params=trade, timeframes=tfs,
                )
                cols = st.columns(len(charts))
                for col, (tf, fig) in zip(cols, charts, strict=True):
                    with col:
                        st.plotly_chart(fig, use_container_width=True)
            else:
                tf = st.selectbox("Timeframe", tfs)
                fig = build_orb_chart(
                    data["timeframes"].get(tf, []),
                    setup=setup,
                    trade_params=trade,
                    title=f"{pair} {tf}",
                )
                st.plotly_chart(fig, use_container_width=True)

    with tab_all:
        if st.button("Analisar todos", key="btn_all"):
            with st.spinner("Scan em lote..."):
                st.session_state["all_result"] = analyze_all_primary_pairs.invoke({})
        if "all_result" in st.session_state:
            data = st.session_state["all_result"]
            st.markdown(data.get("summary", ""))
            for p, info in data.get("results", {}).items():
                icon = "OK" if info.get("found") else "—"
                st.write(f"{icon} **{p}**: {(info.get('reason') or '')[:100]}")

    with tab_backtest:
        limit = st.number_input("Candles", min_value=50, max_value=2000, value=settings.backtest_candle_limit)
        c1, c2 = st.columns(2)
        if c1.button("Backtest par", key="btn_bt_pair"):
            with st.spinner("Walk-forward..."):
                st.session_state["bt_result"] = run_orb_backtest.invoke({
                    "pair": pair,
                    "candle_limit": int(limit),
                })
        if c2.button("Backtest todos", key="btn_bt_all"):
            with st.spinner("Todos os pares..."):
                st.session_state["bt_result"] = run_backtest_all_pairs.invoke({
                    "candle_limit": int(limit),
                    "save_golive": True,
                })
        if "bt_result" in st.session_state:
            st.json(st.session_state["bt_result"])

    with tab_metrics:
        metrics = collect_metrics()
        kpis = metrics.get("kpis", {})
        m1, m2, m3, m4, m5 = st.columns(5)
        m1.metric("Paper WR", f"{kpis.get('paper_win_rate', 0):.0%}")
        m2.metric("Paper abertas", kpis.get("open_paper_positions", 0))
        m3.metric("Paper Max DD", f"{kpis.get('paper_max_drawdown_pct', 0)}%")
        m4.metric("Setups memoria", kpis.get("memory_setups", 0))
        m5.metric("Audit events", kpis.get("audit_events", 0))
        audit_counts = metrics.get("audit", {}).get("event_counts", {})
        if audit_counts:
            st.subheader("Audit (recente)")
            for event, count in audit_counts.items():
                st.write(f"**{event}**: {count}")
        for p, stats in metrics.get("paper", {}).get("by_pair", {}).items():
            st.write(
                f"**{p}**: {stats.get('total', 0)} trades · "
                f"WR {stats.get('win_rate', 0):.0%} · PnL {stats.get('total_pnl', 0)}%",
            )

    with tab_memory:
        summary = get_memory().summary()
        st.metric("Entradas", summary.get("total_entries", 0))
        if summary.get("entries"):
            st.dataframe(summary["entries"], use_container_width=True)

    with tab_paper:
        if st.button("Verificar SL/TP", key="btn_paper"):
            with st.spinner("..."):
                st.session_state["paper_alert_result"] = check_paper_alerts()
        if "paper_alert_result" in st.session_state:
            for alert in st.session_state["paper_alert_result"].get("alerts", []):
                st.write(alert.get("message"))

        paper = get_paper_store().summary()
        st.metric("Posicoes abertas", paper["open_positions"])
        if paper["open"]:
            st.subheader("Abertas")
            for pos in paper["open"]:
                st.write(
                    f"**{pos['pair']}** {pos.get('direction')} · entry {pos.get('entry')} · "
                    f"SL {pos.get('stop_loss')} · TP {pos.get('take_profit')}",
                )
        if paper["recent_closed"]:
            st.subheader("Fechadas")
            for pos in paper["recent_closed"]:
                st.write(f"{pos['pair']} · {pos.get('outcome')} · PnL {pos.get('pnl_percent')}%")

    with tab_audit:
        summary = get_audit_logger().summary()
        st.metric("Eventos recentes", summary.get("total_logged", 0))
        st.caption(summary.get("path", ""))
        if summary.get("recent"):
            st.dataframe(summary["recent"], use_container_width=True)


if __name__ == "__main__":
    main()