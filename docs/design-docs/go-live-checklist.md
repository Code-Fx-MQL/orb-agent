# Checklist Go-Live — Agente ORB

> Live trading so com aprovacao humana dupla. Nunca ativar sem este checklist.

## Pre-requisitos

| # | Item | Como validar |
|---|------|--------------|
| 1 | Backtest walk-forward | `orb-agent --backtest --all` → `data/backtest_golive.json` |
| 2 | KPIs minimos | WR >= 55%, PF >= 1.0, >= 20 trades, core XAUUSD + EURUSD |
| 3 | Paper trading 14+ dias | `ORB_MODE=paper` com posicoes em `data/memory/paper_trades.json` |
| 4 | Guardrails ativos | Risco 1%/3%/6%, news block, retest ORB |
| 5 | Webhooks configurados | `ORB_WEBHOOK_ENABLED=true` + URL n8n |
| 6 | Dashboard protegido | `ORB_UI_PASSWORD` definida |

## Gate duplo (inegociavel)

```env
ORB_MODE=live
ORB_LIVE_APPROVED=true
ORB_LIVE_APPROVAL_TOKEN=<token-secreto>
```

Sessao CLI:

```powershell
orb-agent --pair EURUSD --live-token <token-secreto>
```

Sem **ambos** (.env + token de sessao), o broker bloqueia com `live_blocked` no audit log.

## Broker

| Modo | Uso |
|------|-----|
| `stub` | Simula ordens — validacao do fluxo |
| `ccxt` | Execucao real — requer API keys |

```env
ORB_BROKER_MODE=stub   # ou ccxt
ORB_CCXT_API_KEY=...
ORB_CCXT_API_SECRET=...
```

## Rotacao de token

```python
from orb_agent.guardrails.token_rotation import rotate_live_token
rotate_live_token(current_token="...", env_path=".env")
```

Log em `data/audit/token_rotation.jsonl`.

## Semáforo no dashboard

Aba **Live Ops** → checklist automatico via `ops/golive.py`:

- Verde: pronto (com aprovacao humana final)
- Amarelo: avisos (broker stub, paper < 14 dias)
- Vermelho: bloqueadores (backtest ausente, gate incompleto)

## Assinaturas humanas

| Papel | Responsabilidade |
|-------|------------------|
| Trader | Valida estrategia e risco |
| Revisor | Confirma checklist e token |

Ambos devem assinar antes de `ORB_LIVE_APPROVED=true`.