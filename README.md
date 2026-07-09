# Agente Opening Range Breakout

Agente de IA para **Opening Range Breakout** construído com [Trading Harness](https://github.com/Code-Fx-MQL/trading-harness).

> **Humans steer. Agents execute.**

⚠️ Uso educacional e pesquisa. Trading envolve risco de perda de capital.

**Estado atual:** paper trading ativo · dashboard em [produção EasyPanel](https://fullscopetrade-harness-orb-agent.0ikuso.easypanel.host/) · live bloqueado.  
→ Detalhes: [`docs/ESTADO_ATUAL.md`](docs/ESTADO_ATUAL.md)

## Início rápido

```powershell
.\scripts\setup.ps1
Copy-Item .env.example .env
orb-agent --pair EURUSD
orb-agent --all --json
pip install -e ".[ui]"
orb-ui
python scripts\verify-system.py
pytest -m "not integration"
.\scripts\validate.ps1
```

## Operação

| Ambiente | Comando / URL |
|----------|----------------|
| Scan agendado | `.\scripts\register-scheduled-task.ps1 -IntervalMinutes 15` |
| Scan manual | `.\scripts\scheduled-scan.ps1` |
| Testes webhook | `python scripts\test-webhook.py` |
| Produção | `python scripts\test-production-ops.py` |
| Dashboard prod. | https://fullscopetrade-harness-orb-agent.0ikuso.easypanel.host/ |

## Docker

```powershell
docker compose up --build -d
```

## Deploy EasyPanel

```powershell
# API tRPC (token Settings -> API)
$env:EASYPANEL_TOKEN = "SEU_TOKEN"
.\scripts\deploy-easypanel.ps1

# Ou deploy webhook
.\scripts\deploy-easypanel.ps1 -DeployWebhookUrl "http://PAINEL:3000/api/deploy/TOKEN"
```

Ver [deploy EasyPanel](docs/deploy-easypanel-github.md).

## Documentação

| Doc | Conteúdo |
|-----|----------|
| [**Estado atual**](docs/ESTADO_ATUAL.md) | Operação, deploy, próximos passos |
| [Regras ORB](docs/design-docs/orb-strategy.md) | Estratégia |
| [Checklist validação](docs/design-docs/orb-validation-checklist.md) | Paper → live |
| [Deploy EasyPanel](docs/deploy-easypanel-github.md) | Produção |
| [Workflow n8n](docs/deploy-n8n.md) | IA review + Telegram |
| [Go-live](docs/design-docs/go-live-checklist.md) | Live gate |
| [Tech debt](docs/exec-plans/tech-debt-tracker.md) | Dívida técnica |
| [Plano ativo](docs/exec-plans/active/operacao-paper-live.md) | Paper → live |

## Status das fases

| Fase | Status |
|------|--------|
| 0–8 | OK (blueprint) |
| 9 — Operações | OK |
| Paper + produção | **Em curso** |

Blueprint: [FASES 0–8](https://github.com/Code-Fx-MQL/trading-harness/blob/main/docs/FASES-0-8.md)