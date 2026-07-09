"""Graficos ORB com Opening Range."""

from __future__ import annotations

from typing import Any

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots


def candles_to_df(candles: list[dict[str, Any]]) -> pd.DataFrame:
    rows = []
    for c in candles:
        ts = pd.to_datetime(c["timestamp"], unit="ms", utc=True)
        rows.append({
            "timestamp": ts,
            "open": float(c["open"]),
            "high": float(c["high"]),
            "low": float(c["low"]),
            "close": float(c["close"]),
            "volume": float(c.get("volume", 0)),
        })
    return pd.DataFrame(rows).sort_values("timestamp")


def build_orb_chart(
    candles: list[dict[str, Any]],
    setup: dict[str, Any] | None = None,
    trade_params: dict[str, Any] | None = None,
    title: str = "OHLCV",
) -> go.Figure:
    df = candles_to_df(candles)
    if df.empty:
        fig = go.Figure()
        fig.update_layout(title=f"{title} — sem dados")
        return fig

    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, row_heights=[0.75, 0.25], vertical_spacing=0.03)
    fig.add_trace(
        go.Candlestick(
            x=df["timestamp"],
            open=df["open"],
            high=df["high"],
            low=df["low"],
            close=df["close"],
            name="OHLCV",
        ),
        row=1,
        col=1,
    )
    fig.add_trace(
        go.Bar(x=df["timestamp"], y=df["volume"], name="Volume", marker_color="rgba(80,120,200,0.35)"),
        row=2,
        col=1,
    )

    if setup:
        for key, color, label in [
            ("or_high", "green", "OR High"),
            ("or_low", "red", "OR Low"),
        ]:
            val = setup.get(key)
            if val is not None:
                fig.add_hline(y=float(val), line_dash="dash", line_color=color, annotation_text=label, row=1, col=1)

    if trade_params:
        for key, color, label in [
            ("entry", "blue", "Entry"),
            ("stop_loss", "crimson", "SL"),
            ("take_profit", "limegreen", "TP"),
        ]:
            val = trade_params.get(key)
            if val is not None:
                fig.add_hline(y=float(val), line_color=color, annotation_text=label, row=1, col=1)

    fig.update_layout(title=title, xaxis_rangeslider_visible=False, height=480)
    return fig


def build_multi_tf_charts(
    timeframes_data: dict[str, list],
    pair: str,
    setup: dict[str, Any] | None = None,
    trade_params: dict[str, Any] | None = None,
    timeframes: list[str] | None = None,
) -> list[tuple[str, go.Figure]]:
    tfs = timeframes or list(timeframes_data.keys())
    charts: list[tuple[str, go.Figure]] = []
    for tf in tfs:
        candles = timeframes_data.get(tf, [])
        fig = build_orb_chart(candles, setup=setup, trade_params=trade_params, title=f"{pair} {tf}")
        charts.append((tf, fig))
    return charts