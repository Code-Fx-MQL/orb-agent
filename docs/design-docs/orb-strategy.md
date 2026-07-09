# Opening Range Breakout (ORB) - Regras da estrategia

> Implementacao Fase 1 em `src/orb_agent/tools/orb.py`.

## Glossario

| Termo | Definicao |
|-------|-----------|
| Opening Range (OR) | High/low da primeira hora da sessao (1 vela 1H por defeito) |
| Breakout | Fecho LTF fora do OR |
| Reteste | Pullback ao boundary do OR com fecho a favor |
| Bias HTF | Direcao do dia no timeframe diario |

## Algoritmo top-down (implementado)

```
1D  -> bias: fecho > abertura E fecho > fecho anterior (bullish)
1H  -> OR = high/low da(s) primeira(s) vela(s) de sessao (ORB_SESSION_CANDLES)
15m -> breakout do OR + reteste (modo retest) ou entrada imediata (immediate)
```

### Parametros (`config/orb_rules.py`)

| Parametro | Default | Descricao |
|-----------|---------|-----------|
| `ORB_SESSION_CANDLES` | 1 | Velas MTF do opening range |
| `MIN_OR_RANGE_FOREX` | 0.0008 | Range minimo (~8 pips) |
| `MIN_OR_RANGE_GOLD` | 2.0 | Range minimo XAUUSD |
| `RETEST_TOLERANCE_RATIO` | 0.25 | Zona de reteste (% do OR) |
| `REQUIRE_RETEST` | true | Exigir reteste antes da entrada |
| `MIN_RISK_REWARD` | 1.0 | TP = 1R por defeito |
| `LTF_LOOKBACK` | 16 | Velas LTF analisadas |

### Trade params (detector)

| Direcao | Entry | SL | TP |
|---------|-------|----|----|
| Bullish | Fecho LTF no reteste/breakout | `or_low` | entry + 1R |
| Bearish | Fecho LTF no reteste/breakout | `or_high` | entry - 1R |

## Contrato `detect_orb_setup`

Output quando `found=True`:

```python
{
  "found": True,
  "pair": "EURUSD",
  "setup": {
    "direction": "bullish" | "bearish",
    "or_high": float,
    "or_low": float,
    "entry": float,
    "stop_loss": float,
    "take_profit": float,
    "confidence": float,
    "metadata": {"pattern": "breakout_retest", ...}
  }
}
```

## KPIs alvo

- Win rate backtest >= 50%
- Profit factor >= 1.0
- Amostra >= 20 trades antes de paper

## Disclaimer

Uso educacional. Sem garantia de resultados. Testar em demo/backtest antes de paper ou live.