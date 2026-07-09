# AGENTS.md — Mapa do Repositório

> Índice para agentes. Detalhes em `docs/`.

## Missão

**Agente Opening Range Breakout** — Harness Engineering completo (Fases 0–9), em **paper trading** com dashboard em produção.

Blueprint: [trading-harness](https://github.com/Code-Fx-MQL/trading-harness)

## Onde começar

| Tarefa | Arquivo |
|--------|---------|
| **Estado atual + próximos passos** | `docs/ESTADO_ATUAL.md` |
| Plano ativo | `docs/exec-plans/active/operacao-paper-live.md` |
| Validação ORB | `docs/design-docs/orb-validation-checklist.md` |
| Tech debt | `docs/exec-plans/tech-debt-tracker.md` |
| Deploy | `docs/deploy-easypanel-github.md` |
| n8n | `docs/deploy-n8n.md` |

## Produção

- URL: `https://fullscopetrade-harness-orb-agent.0ikuso.easypanel.host/`
- Health: `/_stcore/health` → `ok`
- Container: apenas `orb-ui` (Streamlit); scan agendado no Windows

## Código principal

```
src/orb_agent/
├── pipeline/analyze.py      # Pipeline ORB paper/live
├── alerts/                  # n8n, Telegram, dispatcher
├── paper/                   # Store + alertas SL/TP
├── providers/ohlcv_cache.py # Cache disco
├── tools/analyze.py         # Scan paralelo
└── ui/                      # Streamlit dashboard
```

## Comandos

```powershell
python scripts/verify-system.py
python scripts/test-production-ops.py
python scripts/test-webhook.py
.\scripts\scheduled-scan.ps1
orb-agent --all --json
pytest -m "not integration"
```

## Regras

- Modo atual: **paper** (live requer gate duplo + checklist)
- Fases 0–9: concluídas
- Próximo marco: paper 14d + core KPI por par
- Escala horizontal: PostgreSQL/Redis (futuro)