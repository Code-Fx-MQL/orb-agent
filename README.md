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
ORB_DATA_SOURCE=ccxt orb-agent --pair XAUUSD
pytest
.\scripts\validate.ps1
```

## Documentação

| Doc | Conteúdo |
|-----|----------|
| [Regras Opening Range Breakout](docs/design-docs/orb-strategy.md) | Definição da estratégia |
| [Plano ativo](docs/exec-plans/active/fase-3-core.md) | Roadmap atual |
| [AGENTS.md](AGENTS.md) | Mapa para agentes IA |

## Status

| Fase | Status |
|------|--------|
| 0 — Fundação | OK |
| 1 — Definição ORB | OK (`detect_orb_setup`) |
| 2 — Dados CCXT | OK |
| **3 — Core + pipeline** | **OK (trade params + risco)** |
| 4 — Backtest + memoria | Pendente |

Ver [FASES 0–8](https://github.com/Code-Fx-MQL/trading-harness/blob/main/docs/FASES-0-8.md).