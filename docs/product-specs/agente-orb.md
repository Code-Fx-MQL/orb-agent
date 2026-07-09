# Spec - Agente Opening Range Breakout

## MVP — Fases 0-8 completas

- [x] Pipeline ORB top-down (1D → 1H → 15m)
- [x] CCXT + backtest walk-forward
- [x] Paper trading + Dashboard Streamlit
- [x] Audit JSONL + LangSmith + alertas n8n
- [x] Live gate duplo + broker stub/ccxt
- [x] Checklist go-live + Live Ops
- [x] Docker + EasyPanel deploy
- [x] Telegram alertas
- [x] Scan agendado (Windows Task Scheduler)

## Fase 8 — Produção

| Componente | Ficheiro |
|------------|----------|
| Docker | `Dockerfile`, `docker-compose.yml` |
| EasyPanel | `deploy/easypanel/compose.yml` |
| Telegram | `alerts/telegram_messages.py` |
| Scan agendado | `scripts/scheduled_scan.py` |
| CI deploy | `.github/workflows/deploy.yml` |
| Guia deploy | `docs/deploy-easypanel-github.md` |

## Maturidade

Paridade com blueprint [trading-harness Fases 0-8](https://github.com/Code-Fx-MQL/trading-harness/blob/main/docs/FASES-0-8.md).