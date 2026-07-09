# Estado atual — ORB Agent

> Atualizado: 2026-07-09 · Repositório: [Code-Fx-MQL/orb-agent](https://github.com/Code-Fx-MQL/orb-agent)

## Resumo

Agente **Opening Range Breakout** maduro para **paper trading** e **dashboard em produção**. Blueprint trading-harness (Fases 0–8) + Fase 9 (operações) concluídas. **Live bloqueado** até paper 14d e KPIs core por par.

## Fases

| Fase | Escopo | Status |
|------|--------|--------|
| 0–8 | Blueprint trading-harness | OK |
| 9 | Cache, scan paralelo, audit, Mem0, scripts ops | OK |
| — | Paper + produção EasyPanel | **Em curso** |

## Operação ativa

| Componente | Estado |
|------------|--------|
| Modo local | `ORB_MODE=paper` |
| Pares | XAUUSD, EURUSD |
| Dados | CCXT/Kraken (`ORB_DATA_SOURCE=auto`) |
| Scan Windows | Tarefa `ORB-Agent-Scan` — Seg–Sex 08–17h, 15 min |
| Dashboard produção | [fullscopetrade-harness-orb-agent.0ikuso.easypanel.host](https://fullscopetrade-harness-orb-agent.0ikuso.easypanel.host/) |
| Health produção | `/_stcore/health` → 200 `ok` |
| Webhooks n8n | `orb-globalsend` + workflow IA review |
| Telegram | Alertas diretos + n8n |
| Backtest go-live | 20 trades · WR 58.8% · PF 1.00 (global OK) |

## Validação (checklist)

| Item | Status |
|------|--------|
| Regras ORB assinadas | OK (2026-07-09) |
| Backtest global ≥ 20 trades | OK |
| Core XAUUSD/EURUSD `meets_kpi` | Pendente (0/2) |
| Paper ≥ 14 dias | Em curso (desde 2026-07-09) |
| Webhooks testados | OK |
| Live gate | Configurado; modo live inativo |

Ver [`docs/design-docs/orb-validation-checklist.md`](design-docs/orb-validation-checklist.md).

## Arquitetura de deploy

```
Windows (dev/ops)                    EasyPanel (produção)
├── ORB-Agent-Scan (15 min)          └── orb-ui (Streamlit :8501)
├── .env paper + webhooks                ├── volume /app/data
├── scripts/test-*.py                    └── env produção (.env.production)
└── orb-ui local (opcional)

n8n (8.fullscopetrade.com)
└── orb-globalsend → IA review → Telegram
```

O container EasyPanel corre apenas o **dashboard** (`orb-ui`). Scan automático em produção não está no container — mantém-se no **Task Scheduler** local ou futuro sidecar/cron.

## Scripts operacionais

| Script | Uso |
|--------|-----|
| `scripts/verify-system.py` | Sanidade pipeline + paper + cache |
| `scripts/test-webhook.py` | `test_ping` n8n + Telegram |
| `scripts/test-setup-found.py` | `setup_found` + IA n8n |
| `scripts/test-paper-alert.py` | `paper_alert` TP/SL |
| `scripts/test-production-ops.py` | Health + scan + webhooks (env produção) |
| `scripts/scheduled-scan.ps1` | Scan manual / rotina |
| `scripts/deploy-easypanel.ps1` | ZIP + upload API ou webhook |
| `scripts/trigger-deploy-webhook.ps1` | Deploy webhook EasyPanel |

## Testes

```powershell
pytest -m "not integration"   # 71 passed
python scripts\verify-system.py
python scripts\test-production-ops.py
```

## Dívida técnica aberta

| ID | Descrição | Prioridade |
|----|-----------|------------|
| TD-BT-CORE-KPI | Core XAUUSD/EURUSD `meets_kpi` | Média |
| TD-HORIZONTAL | PostgreSQL/Redis, fila jobs, réplicas | Futuro |

Ver [`docs/exec-plans/tech-debt-tracker.md`](exec-plans/tech-debt-tracker.md).

## Próximos passos

### 1. Paper trading (prioridade)

- Manter `ORB_MODE=paper` e scan agendado até **≥ 14 dias** (meta: ~2026-07-23).
- Monitorizar `data/memory/paper_trades.json` e alertas SL/TP.
- Rever métricas no dashboard produção (Live Ops).

### 2. KPIs core por par

- Ajustar parâmetros ou amostra backtest até XAUUSD e EURUSD passarem `meets_kpi`.
- Comando: `orb-agent --backtest --all` com `ORB_BACKTEST_CANDLE_LIMIT=2000`.

### 3. Operação produção

- Confirmar **Environment** no EasyPanel alinhado com `deploy/easypanel/.env.production`.
- Redeploy via webhook quando necessário: `deploy-easypanel.ps1 -DeployWebhookUrl <url>`.
- Opcional: sincronizar secrets GitHub (`sync-github-secrets.ps1`) para CI.

### 4. Go-live (após paper + KPIs)

- Assinar [`go-live-checklist.md`](design-docs/go-live-checklist.md).
- `ORB_MODE=live` + `ORB_LIVE_APPROVED` + `--live-token`.
- Nunca ativar live sem checklist completo.

### 5. Futuro (Fase 10+)

- Scan/cron no EasyPanel (sidecar ou job scheduler).
- PostgreSQL/Redis para estado distribuído.
- Atualizar blueprint `trading-harness` com secção Fase 9.

## Referências

- [Deploy EasyPanel](deploy-easypanel-github.md)
- [Workflow n8n](deploy-n8n.md)
- [Estratégia ORB](design-docs/orb-strategy.md)
- [Fase 9 concluída](exec-plans/completed/fase-9-operacoes.md)