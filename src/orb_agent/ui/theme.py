"""Tema visual do dashboard ORB."""

import streamlit as st


def inject_theme() -> None:
    st.markdown(
        """
        <style>
        .orb-title { font-size: 1.6rem; margin-bottom: 0.2rem; }
        .orb-subtitle { color: #6b7280; margin-bottom: 1rem; }
        .orb-ops-bar {
            display: flex; flex-wrap: wrap; gap: 0.75rem;
            padding: 0.6rem 0.8rem; margin-bottom: 1rem;
            background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px;
        }
        .orb-ops-item { min-width: 90px; }
        .orb-ops-label { font-size: 0.7rem; color: #64748b; text-transform: uppercase; }
        .orb-ops-value { font-size: 0.95rem; font-weight: 600; }
        .orb-ops-value.ok { color: #16a34a; }
        .orb-ops-value.warn { color: #d97706; }
        .orb-ops-value.fail { color: #dc2626; }
        .orb-ops-value.info { color: #334155; }
        </style>
        """,
        unsafe_allow_html=True,
    )