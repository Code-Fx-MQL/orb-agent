"""Engine de backtest ORB — walk-forward 1D -> 1H -> 15m."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from orb_agent.config.orb_rules import MIN_RISK_REWARD, MIN_SETUP_CONFIDENCE
from orb_agent.config.settings import settings
from orb_agent.models.schemas import BacktestResult, SetupDirection
from orb_agent.tools.orb import evaluate_orb_setup


def _candles_until(candles: list[dict[str, Any]], ts: int) -> list[dict[str, Any]]:
    return [c for c in candles if int(c["timestamp"]) <= ts]


def _candles_after(candles: list[dict[str, Any]], ts: int) -> list[dict[str, Any]]:
    return [c for c in candles if int(c["timestamp"]) > ts]


def _simulate_trade(
    future_candles: list[dict[str, Any]],
    direction: SetupDirection,
    entry: float,
    sl: float,
    tp: float,
    max_bars: int = 48,
) -> dict[str, Any]:
    """Simula SL/TP no primeiro toque em candles LTF futuros."""
    for candle in future_candles[:max_bars]:
        high = float(candle["high"])
        low = float(candle["low"])
        if direction == SetupDirection.BULLISH:
            if low <= sl:
                return {"outcome": "loss", "exit_price": sl, "rr_achieved": -1.0}
            if high >= tp:
                risk = abs(entry - sl)
                reward = abs(tp - entry)
                rr = reward / risk if risk > 0 else 0.0
                return {"outcome": "win", "exit_price": tp, "rr_achieved": round(rr, 2)}
        else:
            if high >= sl:
                return {"outcome": "loss", "exit_price": sl, "rr_achieved": -1.0}
            if low <= tp:
                risk = abs(sl - entry)
                reward = abs(entry - tp)
                rr = reward / risk if risk > 0 else 0.0
                return {"outcome": "win", "exit_price": tp, "rr_achieved": round(rr, 2)}
    return {"outcome": "timeout", "exit_price": entry, "rr_achieved": 0.0}


def run_orb_backtest_engine(
    pair: str,
    htf_candles: list[dict[str, Any]],
    mtf_candles: list[dict[str, Any]],
    ltf_candles: list[dict[str, Any]],
) -> dict[str, Any]:
    """Backtest walk-forward sem lookahead — avalia ORB em cada janela LTF."""
    pair = pair.upper()
    trades: list[dict[str, Any]] = []
    last_entry_ts = -1
    min_gap_ms = 4 * 15 * 60 * 1000

    if len(ltf_candles) < 8:
        return _aggregate_trades(pair, trades, ltf_candles)

    for i in range(7, len(ltf_candles) - 3):
        ts = int(ltf_candles[i]["timestamp"])
        if ts - last_entry_ts < min_gap_ms:
            continue

        htf_slice = _candles_until(htf_candles, ts)[-settings.backtest_htf_lookback :]
        mtf_slice = _candles_until(mtf_candles, ts)[-settings.backtest_mtf_lookback :]
        ltf_slice = _candles_until(ltf_candles, ts)

        if len(htf_slice) < 2 or len(mtf_slice) < settings.orb_session_candles or len(ltf_slice) < 3:
            continue

        detection = evaluate_orb_setup(
            pair,
            htf_slice,
            mtf_slice,
            ltf_slice,
            htf_timeframe=settings.default_htf,
            mtf_timeframe=settings.default_mtf,
            ltf_timeframe=settings.default_ltf,
            session_candles=settings.orb_session_candles,
            require_retest=settings.orb_require_retest,
        )
        if not detection.get("found"):
            continue

        setup = detection["setup"]
        if float(setup.get("confidence", 0)) < MIN_SETUP_CONFIDENCE:
            continue

        direction = SetupDirection(setup["direction"])
        entry = float(setup["entry"])
        sl = float(setup["stop_loss"])
        tp = float(setup["take_profit"])

        future = _candles_after(ltf_candles, ts)
        sim = _simulate_trade(future, direction, entry, sl, tp)
        trades.append({
            "timestamp": ts,
            "direction": direction.value,
            "entry": entry,
            "sl": sl,
            "tp": tp,
            "pattern": (setup.get("metadata") or {}).get("pattern"),
            **sim,
        })
        last_entry_ts = ts

    return _aggregate_trades(pair, trades, ltf_candles)


def _aggregate_trades(
    pair: str,
    trades: list[dict[str, Any]],
    timeline_candles: list[dict[str, Any]],
) -> dict[str, Any]:
    if not timeline_candles:
        return BacktestResult(
            pair=pair,
            period_start=datetime.now(UTC),
            period_end=datetime.now(UTC),
            total_trades=0,
            win_rate=0.0,
            avg_rr=0.0,
            profit_factor=0.0,
            max_drawdown=0.0,
            notes="Sem candles para backtest",
        ).model_dump(mode="json")

    if not trades:
        return BacktestResult(
            pair=pair,
            period_start=_ts_to_dt(int(timeline_candles[0]["timestamp"])),
            period_end=_ts_to_dt(int(timeline_candles[-1]["timestamp"])),
            total_trades=0,
            win_rate=0.0,
            avg_rr=0.0,
            profit_factor=0.0,
            max_drawdown=0.0,
            notes="Nenhum setup ORB no periodo",
        ).model_dump(mode="json")

    wins = [t for t in trades if t["outcome"] == "win"]
    losses = [t for t in trades if t["outcome"] == "loss"]
    decided = wins + losses
    win_rate = len(wins) / len(decided) if decided else 0.0
    avg_rr = sum(t["rr_achieved"] for t in decided) / len(decided) if decided else 0.0

    gross_profit = sum(max(t["rr_achieved"], 0) for t in wins)
    gross_loss = abs(sum(min(t["rr_achieved"], 0) for t in losses))
    profit_factor = gross_profit / gross_loss if gross_loss > 0 else gross_profit

    equity = 0.0
    peak = 0.0
    max_dd = 0.0
    for t in decided:
        equity += t["rr_achieved"]
        peak = max(peak, equity)
        max_dd = max(max_dd, peak - equity)

    result = BacktestResult(
        pair=pair,
        period_start=_ts_to_dt(int(timeline_candles[0]["timestamp"])),
        period_end=_ts_to_dt(int(timeline_candles[-1]["timestamp"])),
        total_trades=len(trades),
        win_rate=round(win_rate, 4),
        avg_rr=round(avg_rr, 2),
        profit_factor=round(profit_factor, 2),
        max_drawdown=round(max_dd, 2),
        notes=f"{len(wins)}W / {len(losses)}L / {len(trades) - len(decided)} timeout",
    )
    out = result.model_dump(mode="json")
    out["wins"] = len(wins)
    out["losses"] = len(losses)
    out["timeouts"] = len(trades) - len(decided)
    out["trades_sample"] = trades[-5:]
    out["meets_kpi"] = (
        win_rate >= 0.50
        and profit_factor >= 1.0
        and len(decided) >= 5
        and avg_rr >= MIN_RISK_REWARD
    )
    return out


def _ts_to_dt(ts: int) -> datetime:
    return datetime.fromtimestamp(ts / 1000, tz=UTC)