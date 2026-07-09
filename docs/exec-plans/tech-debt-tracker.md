# Tech Debt Tracker — ORB Agent

> Atualizado: 2026-07-09 (pos-deploy EasyPanel)

| ID | Descricao | Severidade | Status |
|----|-----------|------------|--------|
| TD-CACHE | Cache OHLCV entre scans | Baixa | Resolvido (Fase 9) |
| TD-PARALLEL | Scan sequencial lento | Baixa | Resolvido (Fase 9) |
| TD-AUDIT-ROT | Audit log sem rotacao | Baixa | Resolvido (Fase 9) |
| TD-MEM0 | Memoria so JSON local | Baixa | Mem0 opcional (Fase 9) |
| TD-ORB-RULES | Regras ORB nao assinadas pelo trader | Alta | Resolvido (checklist 2026-07-09) |
| TD-BT-SAMPLE | Backtest global < 20 trades | Media | Resolvido global (20 trades); core KPI 0/2 aberto |
| TD-BT-CORE-KPI | Core XAUUSD/EURUSD meets_kpi | Media | Aberto |
| TD-LLM | Grafo LLM opcional (nao obrigatorio) | Baixa | Aceite |
| TD-HORIZONTAL | Sem lock distribuido / PostgreSQL | Media | Futuro pos-Fase 9 |
| TD-PROD-SCAN | Scan agendado so no Windows (nao no container) | Baixa | Aceite — ver ESTADO_ATUAL |

Ver checklist: [`docs/design-docs/orb-validation-checklist.md`](../design-docs/orb-validation-checklist.md)