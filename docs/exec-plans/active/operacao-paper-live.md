# Plano ativo — Paper → Live

**Status:** em curso  
**Inicio:** 2026-07-09

## Objetivo

Validar estrategia ORB em paper ≥ 14 dias e desbloquear go-live quando KPIs core estiverem cumpridos.

## Checklist operacional

| # | Tarefa | Meta | Status |
|---|--------|------|--------|
| 1 | Paper trading continuo | ≥ 14 dias | Em curso |
| 2 | Scan agendado Windows | 15 min mercado | OK |
| 3 | Dashboard producao | Health `ok` | OK |
| 4 | Webhooks n8n + Telegram | test_ping, scan, setup, paper | OK |
| 5 | Core KPI por par | XAUUSD + EURUSD `meets_kpi` | Pendente |
| 6 | Go-live checklist | Assinatura final | Bloqueado |

## Acoes semanais

1. Rever `data/memory/paper_trades.json` e metricas no dashboard.
2. Correr `python scripts/test-production-ops.py`.
3. Verificar execucoes n8n (setup_found / scan_complete).
4. Atualizar checklist em `orb-validation-checklist.md` se KPIs mudarem.

## Criterio de conclusao

- Paper ≥ 14 dias com posicoes registadas
- Item 9 do checklist ORB (core KPI) marcado
- `go-live-checklist.md` sem bloqueadores

Proximo marco: **~2026-07-23** (14 dias paper).

Estado completo: [`docs/ESTADO_ATUAL.md`](../../ESTADO_ATUAL.md)