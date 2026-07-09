# AGENTS.md — Mapa do Repositório

> Índice para agentes. Detalhes em `docs/`.

## Missão

**Agente Opening Range Breakout** — IA especializada em Opening Range Breakout com Harness Engineering.

Blueprint: [trading-harness](https://github.com/Code-Fx-MQL/trading-harness)

## Onde começar

| Tarefa | Arquivo |
|--------|---------|
| Plano ativo | `docs/exec-plans/active/fase-7-live-gate.md` |
| Checklist go-live | `docs/design-docs/go-live-checklist.md` |
| Regras da estratégia | `docs/design-docs/orb-strategy.md` |
| Spec do agente | `docs/product-specs/agente-orb.md` |
| Arquitetura | `ARCHITECTURE.md` |

## Código

```
src/orb_agent/
├── guardrails/live_gate.py   # Gate duplo live
├── guardrails/token_rotation.py
├── broker/executor.py        # stub + ccxt
├── ops/golive.py             # Checklist semáforo
├── pipeline/analyze.py       # Pipeline + paper/live
├── audit/logger.py
├── alerts/dispatcher.py
├── ui/live_ops_panel.py
└── main.py                   # --live-token
```

## Comandos

```powershell
.\scripts\setup.ps1
.\scripts\validate.ps1
orb-agent --pair EURUSD
orb-agent --pair EURUSD --live-token TOKEN
ORB_MODE=live orb-agent --pair XAUUSD --live-token TOKEN
pip install -e ".[ui]"
orb-ui
pytest -m "not integration"
```

## Regras inegociáveis

- Modo default `analysis`
- Live bloqueado sem gate duplo (`ORB_LIVE_APPROVED` + `--live-token`)
- Broker stub por default — `ORB_BROKER_MODE=ccxt` só com checklist OK
- Pipeline determinístico (sem LLM obrigatório)
- Top-down: HTF → MTF → LTF (configurável em settings)