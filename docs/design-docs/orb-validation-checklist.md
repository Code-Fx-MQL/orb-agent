# Checklist de Validacao — Estrategia ORB

> Assinar antes de promover paper → live.

**Ultima validacao:** 2026-07-09 · fonte Kraken (CCXT) · `data/backtest_golive.json`

## Regras da estrategia

| # | Criterio | OK |
|---|----------|-----|
| 1 | Top-down 1D → 1H → 15m documentado | [x] |
| 2 | Opening Range definido (session candles) | [x] |
| 3 | Breakout + retest como modo default | [x] |
| 4 | Bias diario alinhado com direcao do trade | [x] |
| 5 | R:R minimo 1:1 respeitado (`MIN_RISK_REWARD`) | [x] |

## KPIs backtest

Execucao: `orb-agent --backtest --all` com `ORB_BACKTEST_CANDLE_LIMIT=2000`.

| # | Criterio | Valor alvo | Resultado | OK |
|---|----------|------------|-----------|-----|
| 6 | Win rate global | >= 55% | **58.8%** (10W/7L) | [x] |
| 7 | Profit factor | >= 1.0 | **1.00** | [x] |
| 8 | Trades minimos | >= 20 | **20** | [x] |
| 9 | Core XAUUSD + EURUSD | meets_kpi | **0/2** (XAU avg_rr 0.6; EUR avg_rr 0.0) | [ ] |

### Detalhe por par

| Par | Trades | WR | PF | meets_kpi | Periodo |
|-----|--------|-----|-----|-----------|---------|
| XAUUSD | 5 | 80% | 4.00 | nao (avg_rr 0.6) | 2026-07-01 → 2026-07-09 |
| EURUSD | 15 | 50% | 1.00 | nao (avg_rr 0.0, 3 timeout) | 2026-07-01 → 2026-07-09 |

## Operacao

| # | Criterio | OK |
|---|----------|-----|
| 10 | Paper trading >= 14 dias | [~] iniciado 2026-07-09 · scan 15 min Seg-Sex 08–17h |
| 11 | Webhooks n8n testados (`scripts/test-webhook.py`) | [x] n8n + Telegram OK (2026-07-09) |
| 12 | `scripts/verify-system.py` sem erros | [x] |
| 13 | Live gate duplo configurado | [x] (codigo + `.env`; modo live nao ativo) |

## Veredicto

| Fase | Status |
|------|--------|
| Paper trading | **Em curso** desde 2026-07-09 (meta: 14 dias) |
| Live | **Bloqueado** — item 9 (core KPI) + paper 14d |

## Assinaturas

| Papel | Nome | Data |
|-------|------|------|
| Trader | Rsantos | 2026-07-09 |
| Revisor | ORB Agent (verify-system + backtest) | 2026-07-09 |