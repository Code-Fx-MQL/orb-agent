# Spec - Agente Opening Range Breakout

## MVP

- [x] Pipeline deterministico com detector ORB
- [x] detect_orb_setup (1D bias -> 1H OR -> 15m breakout/retest)
- [x] Testes unitarios e tool
- [x] Modo analysis default
- [x] Dados CCXT (stub/ccxt/auto) + pairs registry
- [x] Pipeline completo: deteccao -> trade -> risco -> explicacao
- [x] calculate_trade_params com sizing e validacao R:R
- [x] Backtest walk-forward + export `data/backtest_golive.json`
- [x] Memoria JSON (`memory/store.py`)
- [ ] Paper trading + UI (Fase 5)