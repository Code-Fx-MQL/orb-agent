# Fase 2 - Dados e ambiente (CCXT)

**Status:** concluida

## Entregaveis

| # | Item | Status |
|---|------|--------|
| 2.1 | `providers/ccxt_provider.py` | OK |
| 2.2 | `providers/symbols.py` | OK |
| 2.3 | `tools/data.py` -> `fetch_multi_tf_data` | OK |
| 2.4 | Modos stub / ccxt / auto | OK |
| 2.5 | `config/pairs_registry.py` | OK |
| 2.6 | `tests/test_ccxt_data.py` | OK |
| 2.7 | CI com `ORB_DATA_SOURCE=stub` | OK |

## Proximo (Fase 3)

- Refinar detector ORB com dados reais
- `calculate_trade_params` integrado ao pipeline
- CLI `--all` em producao