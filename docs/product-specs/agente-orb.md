# Spec - Agente Opening Range Breakout

## Maturidade: Fases 0-9

- [x] Fases 0-8 — paridade blueprint trading-harness
- [x] Fase 9 — cache OHLCV, scan paralelo, rotacao audit, Mem0 opcional

## Fase 9 — Operacoes e escala

| Componente | Ficheiro |
|------------|----------|
| Cache OHLCV | `providers/ohlcv_cache.py` |
| Scan paralelo | `tools/analyze.py` (`ORB_SCAN_WORKERS`) |
| Rotacao audit | `audit/rotation.py` |
| Mem0 cloud | `memory/mem0_sync.py` |
| Health check | `scripts/verify-system.py` |

## Futuro

- Estado distribuido (PostgreSQL/Redis)
- Fila de jobs para scans
- Replicas horizontais