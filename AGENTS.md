# AGENTS.md — Mapa do Repositório

> Índice para agentes. Detalhes em `docs/`.

## Missão

**Agente Opening Range Breakout** — Harness Engineering completo (Fases 0–9).

Blueprint: [trading-harness](https://github.com/Code-Fx-MQL/trading-harness)

## Onde começar

| Tarefa | Arquivo |
|--------|---------|
| Plano ativo | `docs/exec-plans/active/fase-9-operacoes.md` |
| Validação ORB | `docs/design-docs/orb-validation-checklist.md` |
| Tech debt | `docs/exec-plans/tech-debt-tracker.md` |
| Deploy | `docs/deploy-easypanel-github.md` |

## Código (Fase 9)

```
src/orb_agent/
├── providers/ohlcv_cache.py   # Cache disco TTL
├── audit/rotation.py        # Rotacao audit log
├── tools/analyze.py         # Scan paralelo
├── memory/mem0_sync.py      # Mem0 opcional
└── ...
```

## Comandos

```powershell
python scripts/verify-system.py
python scripts/test-webhook.py
.\scripts\scheduled-scan.ps1
orb-agent --all --json
pytest -m "not integration"
```

## Regras

- Fases 0–8: blueprint trading-harness
- Fase 9: hardening pós-MVP (cache, paralelo, rotação)
- Escala horizontal requer PostgreSQL/Redis (futuro)