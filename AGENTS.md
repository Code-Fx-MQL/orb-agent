# AGENTS.md — Mapa do Repositório

> Índice para agentes. Detalhes em `docs/`.

## Missão

**Agente Opening Range Breakout** — IA especializada em Opening Range Breakout com Harness Engineering.

Blueprint: [trading-harness](https://github.com/Code-Fx-MQL/trading-harness)

## Onde começar

| Tarefa | Arquivo |
|--------|---------|
| Plano ativo | `docs/exec-plans/active/fase-1-definicao.md` |
| Regras da estratégia | `docs/design-docs/orb-strategy.md` |
| Spec do agente | `docs/product-specs/agente-orb.md` |
| Arquitetura | `ARCHITECTURE.md` |

## Código

```
src/orb_agent/
├── pipeline/analyze.py    # Orquestração determinística
├── tools/orb.py  # detect_orb_setup
├── config/orb_rules.py
├── guardrails/            # Risco, live gate
└── main.py                # CLI
```

## Comandos

```powershell
.\scripts\setup.ps1
.\scripts\validate.ps1
orb-agent --pair XAUUSD
pytest
```

## Regras inegociáveis

- Modo default `analysis`
- Live bloqueado sem gate duplo
- Pipeline determinístico (sem LLM obrigatório)
- Top-down: HTF → MTF → LTF (configurável em settings)