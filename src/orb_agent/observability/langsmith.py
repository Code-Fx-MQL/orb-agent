"""Configuracao LangSmith — tracing opcional do pipeline."""

from __future__ import annotations

import os
from collections.abc import Callable
from typing import Any, TypeVar

import structlog

from orb_agent.config.settings import settings

logger = structlog.get_logger(__name__)

F = TypeVar("F", bound=Callable[..., Any])

_configured = False


def is_tracing_enabled() -> bool:
    return bool(settings.langsmith_tracing and settings.langsmith_api_key)


def configure_tracing() -> bool:
    """Ativa LangSmith via variaveis de ambiente (idempotente)."""
    global _configured
    if _configured:
        return is_tracing_enabled()

    if not is_tracing_enabled():
        return False

    key = settings.langsmith_api_key or ""
    project = settings.langsmith_project

    os.environ["LANGSMITH_TRACING"] = "true"
    os.environ["LANGSMITH_API_KEY"] = key
    os.environ["LANGSMITH_PROJECT"] = project
    os.environ["LANGCHAIN_TRACING_V2"] = "true"
    os.environ["LANGCHAIN_API_KEY"] = key
    os.environ["LANGCHAIN_PROJECT"] = project

    _configured = True
    logger.info("langsmith_tracing_enabled", project=project)
    return True


def _noop_decorator(*_args: Any, **_kwargs: Any) -> Callable[[F], F]:
    def wrapper(fn: F) -> F:
        return fn

    return wrapper


def get_traceable() -> Callable[..., Callable[[F], F]]:
    """Retorna @traceable do LangSmith ou no-op se indisponivel."""
    configure_tracing()
    if not is_tracing_enabled():
        return _noop_decorator
    try:
        from langsmith import traceable

        return traceable
    except ImportError:
        logger.warning("langsmith_not_installed")
        return _noop_decorator


def traced(name: str, run_type: str = "chain") -> Callable[[F], F]:
    """Decorator seguro — no-op sem API key ou pacote."""
    traceable = get_traceable()
    return traceable(name=name, run_type=run_type)