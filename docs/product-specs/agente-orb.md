# Spec - Agente Opening Range Breakout

## MVP

- [x] Pipeline deterministico com detector ORB
- [x] detect_orb_setup (1D bias -> 1H OR -> 15m breakout/retest)
- [x] Dados CCXT (stub/ccxt/auto) + pairs registry
- [x] Backtest walk-forward + export `data/backtest_golive.json`
- [x] Paper trading + Dashboard Streamlit
- [x] Audit JSONL + LangSmith + alertas
- [x] Live gate duplo (`guardrails/live_gate.py`)
- [x] Broker executor stub/ccxt (`broker/executor.py`)
- [x] Checklist go-live (`ops/golive.py`)
- [x] Painel Live Ops (`ui/live_ops_panel.py`)
- [x] Rotacao de token (`guardrails/token_rotation.py`)

## Fase 7 — Live gate

| Componente | Ficheiro |
|------------|----------|
| Gate duplo | `src/orb_agent/guardrails/live_gate.py` |
| Broker | `src/orb_agent/broker/executor.py` |
| Checklist | `src/orb_agent/ops/golive.py` |
| Live Ops UI | `src/orb_agent/ui/live_ops_panel.py` |
| Token rotation | `src/orb_agent/guardrails/token_rotation.py` |

Eventos audit live: `live_blocked`, `live_order_stub`, `live_order_placed`, `live_order_failed`.

## Proximo (Fase 8)

- Docker + deploy
- Telegram webhooks
- Scan agendado