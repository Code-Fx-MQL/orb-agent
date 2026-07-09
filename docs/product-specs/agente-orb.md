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

## Fase 5 — UI e paper

| Componente | Ficheiro |
|------------|----------|
| Dashboard | `src/orb_agent/ui/app.py` |
| Graficos ORB | `src/orb_agent/ui/charts.py` |
| Paper store | `src/orb_agent/paper/store.py` |
| Alertas SL/TP | `src/orb_agent/paper/alerts.py` |
| Metricas | `src/orb_agent/metrics/collector.py` |

Modo `ORB_MODE=paper` abre posicao simulada em `data/memory/paper_trades.json` quando o setup passa risco.

## Proximo (Fase 6+)

- Observabilidade (audit JSONL, LangSmith)
- Live gate
- Deploy Docker