# Spec - Agente Opening Range Breakout

## MVP

- [x] Pipeline deterministico com detector ORB
- [x] detect_orb_setup (1D bias -> 1H OR -> 15m breakout/retest)
- [x] Testes unitarios e tool
- [x] Modo analysis default
- [x] Dados CCXT (stub/ccxt/auto) + pairs registry
- [x] Pipeline completo: deteccao -> trade -> risco -> explicacao
- [x] calculate_trade_params com sizing e validacao R:R
- [x] Backtest walk-forward + export `data/backtest_golive.json`
- [x] Memoria JSON (`memory/store.py`)
- [x] Paper trading (`paper/store.py`, `paper/alerts.py`)
- [x] Dashboard Streamlit (`ui/app.py`, `orb-ui`)
- [x] Audit JSONL (`audit/logger.py`)
- [x] LangSmith tracing opcional (`observability/langsmith.py`)
- [x] Alertas dispatcher + payloads (`alerts/`)
- [x] Auto-refresh UI (`ui/production.py`)

## Fase 6 — Observabilidade

| Componente | Ficheiro |
|------------|----------|
| Audit log | `src/orb_agent/audit/logger.py` |
| LangSmith | `src/orb_agent/observability/langsmith.py` |
| Metricas | `src/orb_agent/metrics/collector.py` |
| Alertas | `src/orb_agent/alerts/dispatcher.py` |
| Auto-refresh | `src/orb_agent/ui/production.py` |

Eventos audit: `analysis_no_setup`, `setup_filtered`, `risk_blocked`, `setup_detected`, `paper_open`, `webhook_dispatch`.

## Proximo (Fase 7+)

- Live gate duplo
- Broker executor
- Checklist go-live
- Deploy Docker (Fase 8)