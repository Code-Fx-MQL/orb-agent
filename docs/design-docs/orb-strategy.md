# Opening Range Breakout (ORB) - Regras da estrategia

> Scaffold de exemplo gerado por [trading-harness](https://github.com/Code-Fx-MQL/trading-harness).

## Glossario

| Termo | Definicao |
|-------|-----------|
| Opening Range (OR) | High/low da primeira hora (ou N minutos) da sessao |
| Breakout | Fecho LTF fora do range OR |
| Reteste | Pullback ao boundary do OR antes da entrada |
| Killzone | London open (08:00 UTC) ou NY open (13:30 UTC) |

## Algoritmo top-down

```
1D  -> bias direcional (tendencia do dia)
1H  -> define Opening Range da sessao ativa
15m -> breakout + reteste para entrada
```

## Parametros e defaults

| Parametro | Default | Modulo |
|-----------|---------|--------|
| `ORB_SESSION_MINUTES` | 60 | `config/orb_rules.py` |
| Sessao London | 08:00-09:00 UTC | settings / rules |
| SL | Extremo oposto do OR | `tools/trade.py` |
| TP | 1R ou fecho em resistencia HTF | `tools/trade.py` |

## Mapeamento harness

| Conceito ORB | Modulo harness |
|--------------|----------------|
| Range da primeira hora | `detect_orb_setup` (HTF/MTF) |
| False breakout | `reason` no detector |
| Confirma tendencia diaria | `analysis/confluences.py` |
| Reteste boundary | trigger LTF em `detect_orb_setup` |
| Killzone | filtro em pipeline |

## KPIs alvo

- Win rate backtest >= 50%
- Profit factor >= 1.0
- Amostra >= 20 trades antes de paper

## Disclaimer

Uso educacional. Sem garantia de resultados. Testar em demo/backtest antes de paper ou live.