"""Gate de aprovacao humana para live trading — Fase 7."""

from __future__ import annotations

from orb_agent.config.settings import OperationMode, settings

_session_token: str | None = None


def set_live_session_token(token: str | None) -> None:
    global _session_token
    _session_token = token


def get_live_session_token() -> str | None:
    return _session_token


def is_live_trading_allowed(session_token: str | None = None) -> tuple[bool, str]:
    """Duplo gate: ORB_LIVE_APPROVED + token de aprovacao valido."""
    if settings.mode != OperationMode.LIVE:
        return False, f"Modo atual e {settings.mode.value}, nao live"

    if not settings.live_approved:
        return False, "ORB_LIVE_APPROVED=false — aprovacao humana pendente no .env"

    expected = settings.live_approval_token
    if not expected:
        return False, "ORB_LIVE_APPROVAL_TOKEN nao configurado"

    token = session_token or _session_token
    if not token:
        return False, "Token de sessao ausente — use --live-token"

    if token != expected:
        return False, "Token de aprovacao invalido"

    return True, "Live trading autorizado"


def live_gate_status() -> dict[str, object]:
    allowed, reason = is_live_trading_allowed()
    return {
        "mode": settings.mode.value,
        "approved_env": settings.live_approved,
        "token_configured": bool(settings.live_approval_token),
        "session_token_set": bool(_session_token),
        "allowed": allowed,
        "reason": reason,
        "broker_mode": settings.broker_mode,
    }