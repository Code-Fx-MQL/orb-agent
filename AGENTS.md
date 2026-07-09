# AGENTS.md — Mapa do Repositório

> Índice para agentes. Detalhes em `docs/`.

## Missão

**Agente Opening Range Breakout** — IA especializada em Opening Range Breakout com Harness Engineering.

Blueprint: [trading-harness](https://github.com/Code-Fx-MQL/trading-harness)

## Onde começar

| Tarefa | Arquivo |
|--------|---------|
| Plano ativo | `docs/exec-plans/active/fase-6-observability.md` |
| Regras da estratégia | `docs/design-docs/orb-strategy.md` |
| Spec do agente | `docs/product-specs/agente-orb.md` |
| Arquitetura | `ARCHITECTURE.md` |

## Código

```
src/orb_agent/
├── providers/             # CCXT + symbols
├── pipeline/analyze.py    # Pipeline + audit + tracing
├── audit/logger.py        # JSONL append-only
├── observability/langsmith.py
├── alerts/                # dispatcher, payloads, webhooks
├── paper/                 # store.py, alerts.py
├── metrics/collector.py   # KPIs memoria + paper + audit
├── ui/                    # app.py, production.py, charts.py
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
python scripts/doc_garden.py
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
- Audit log ativo em todas as análises (`data/audit/trade_audit.jsonl`)