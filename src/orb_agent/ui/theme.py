"""Tema visual do dashboard ORB."""

import streamlit as st


def inject_theme() -> None:
    st.markdown(
        """
        <style>
        .orb-title { font-size: 1.6rem; margin-bottom: 0.2rem; }
        .orb-subtitle { color: #6b7280; margin-bottom: 1rem; }
        </style>
        """,
        unsafe_allow_html=True,
    )