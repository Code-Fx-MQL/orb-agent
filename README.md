# Agente Opening Range Breakout

Agente de IA para **Opening Range Breakout** construído com [Trading Harness](https://github.com/Code-Fx-MQL/trading-harness).

> **Humans steer. Agents execute.**

⚠️ Uso educacional e pesquisa. Trading envolve risco de perda de capital.

## Início rápido

```powershell
.\scripts\setup.ps1
Copy-Item .env.example .env
orb-agent --pair EURUSD
orb-agent --all --json
pip install -e ".[ui]"
orb-ui
python scripts\verify-system.py
pytest
.\scripts\validate.ps1
```

## Docker

```powershell
docker compose up --build -d
```

## Scan agendado

```powershell
.\scripts\scheduled-scan.ps1
.\scripts\register-scheduled-task.ps1 -IntervalMinutes 15
```

## Documentação

| Doc | Conteúdo |
|-----|----------|
| [Regras ORB](docs/design-docs/orb-strategy.md) | Estratégia |
| [Checklist validação](docs/design-docs/orb-validation-checklist.md) | Assinatura trader |
| [Deploy EasyPanel](docs/deploy-easypanel-github.md) | Produção |
| [Go-live](docs/design-docs/go-live-checklist.md) | Live gate |
| [Tech debt](docs/exec-plans/tech-debt-tracker.md) | Dívida técnica |

## Status

| Fase | Status |
|------|--------|
| 0–8 | OK (blueprint completo) |
| **9 — Operações** | **OK (cache, scan paralelo, escala)** |

Ver [FASES 0–8](https://github.com/Code-Fx-MQL/trading-harness/blob/main/docs/FASES-0-8.md) + Fase 9 em `docs/exec-plans/active/fase-9-operacoes.md`.