# AGENTS.md — Mapa do Repositório

> Índice para agentes. Detalhes em `docs/`.

## Missão

**Agente Opening Range Breakout** — IA especializada em Opening Range Breakout com Harness Engineering.

Blueprint: [trading-harness](https://github.com/Code-Fx-MQL/trading-harness)

## Onde começar

| Tarefa | Arquivo |
|--------|---------|
| Plano ativo | `docs/exec-plans/active/fase-8-producao.md` |
| Deploy produção | `docs/deploy-easypanel-github.md` |
| Checklist go-live | `docs/design-docs/go-live-checklist.md` |
| Regras da estratégia | `docs/design-docs/orb-strategy.md` |
| Spec do agente | `docs/product-specs/agente-orb.md` |

## Código

```
src/orb_agent/
├── guardrails/live_gate.py
├── broker/executor.py
├── ops/golive.py
├── alerts/                  # webhooks, telegram, dispatcher
├── pipeline/analyze.py
├── ui/app.py + live_ops_panel.py
└── main.py
```

## Comandos

```powershell
orb-agent --pair EURUSD
orb-ui
docker compose up --build -d
.\scripts\scheduled-scan.ps1
.\scripts\register-scheduled-task.ps1 -IntervalMinutes 15
pytest -m "not integration"
```

## Deploy

- `Dockerfile` + `docker-compose.yml` — local
- `deploy/easypanel/` — EasyPanel compose
- `.github/workflows/deploy.yml` — CI deploy manual

## Regras inegociáveis

- Modo default `analysis`
- Live bloqueado sem gate duplo
- Volume `/app/data` obrigatório em produção
- Scan agendado separado do auto-refresh UI