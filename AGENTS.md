# AGENTS.md — Mapa do Repositório

> Índice para agentes. Detalhes em `docs/`.

## Missão

**Agente Opening Range Breakout** — IA especializada em Opening Range Breakout com Harness Engineering.

Blueprint: [trading-harness](https://github.com/Code-Fx-MQL/trading-harness)

## Onde começar

| Tarefa | Arquivo |
|--------|---------|
| Plano ativo | `docs/exec-plans/active/fase-5-ui.md` |
| Regras da estratégia | `docs/design-docs/orb-strategy.md` |
| Spec do agente | `docs/product-specs/agente-orb.md` |
| Arquitetura | `ARCHITECTURE.md` |

## Código

```
src/orb_agent/
├── providers/             # CCXT + symbols
├── pipeline/analyze.py    # Pipeline + modo paper
├── paper/                 # store.py, alerts.py
├── metrics/collector.py   # KPIs memoria + paper
├── ui/                    # app.py, charts.py, theme.py
├── tools/data.py          # fetch_multi_tf_data
├── tools/orb.py           # detect_orb_setup
├── tools/analyze.py       # analyze_pair, analyze_all_primary_pairs
├── config/orb_rules.py
└── main.py
```

## Comandos

```powershell
.\scripts\setup.ps1
.\scripts\validate.ps1
orb-agent --pair EURUSD
orb-agent --all --json
orb-agent --backtest --pair EURUSD
ORB_DATA_SOURCE=ccxt orb-agent --pair XAUUSD
pip install -e ".[ui]"
orb-ui
pytest -m "not integration"
```

## Regras inegociáveis

- Modo default `analysis`
- Live bloqueado sem gate duplo
- Pipeline determinístico (sem LLM obrigatório)
- Top-down: HTF → MTF → LTF (configurável em settings)
- Paper abre posição apenas com `ORB_MODE=paper` e risco aprovado