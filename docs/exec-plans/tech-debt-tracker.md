# Tech Debt Tracker — ORB Agent

> Atualizado: 2026-07-09

| ID | Descricao | Severidade | Status |
|----|-----------|------------|--------|
| TD-CACHE | Cache OHLCV entre scans | Baixa | Resolvido (Fase 9) |
| TD-PARALLEL | Scan sequencial lento | Baixa | Resolvido (Fase 9) |
| TD-AUDIT-ROT | Audit log sem rotacao | Baixa | Resolvido (Fase 9) |
| TD-MEM0 | Memoria so JSON local | Baixa | Mem0 opcional (Fase 9) |
| TD-ORB-RULES | Regras ORB nao assinadas pelo trader | Alta | Aberto |
| TD-BT-SAMPLE | Backtest global < 20 trades | Media | Aberto |
| TD-LLM | Grafo LLM opcional (nao obrigatorio) | Baixa | Aceite |
| TD-HORIZONTAL | Sem lock distribuido / PostgreSQL | Media | Futuro pos-Fase 9 |

Ver checklist: [`docs/design-docs/orb-validation-checklist.md`](../design-docs/orb-validation-checklist.md)