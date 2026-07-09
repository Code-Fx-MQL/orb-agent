#!/usr/bin/env python3
"""Doc gardening — valida consistencia entre AGENTS.md, README e planos ativos."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ACTIVE_DIR = ROOT / "docs" / "exec-plans" / "active"
AGENTS = ROOT / "AGENTS.md"
README = ROOT / "README.md"


def _fail(msg: str) -> None:
    print(f"[FAIL] {msg}")
    sys.exit(1)


def main() -> None:
    print("=== Doc Gardening (orb-agent) ===")

    if not AGENTS.exists():
        _fail("AGENTS.md ausente")
    if not README.exists():
        _fail("README.md ausente")

    active_plans = list(ACTIVE_DIR.glob("*.md"))
    if len(active_plans) > 1:
        _fail(f"Maximo 1 plano ativo, encontrado {len(active_plans)}: {active_plans}")

    active_name = active_plans[0].name if active_plans else None
    if active_name:
        print(f"[OK] Plano ativo: {active_name}")
    else:
        print("[OK] Nenhum plano ativo (MVP completo)")

    agents_text = AGENTS.read_text(encoding="utf-8")
    readme_text = README.read_text(encoding="utf-8")

    if active_name:
        active_rel = f"docs/exec-plans/active/{active_name}"
        if active_name not in agents_text and active_rel not in agents_text:
            _fail(f"AGENTS.md nao referencia {active_name}")

    if len(agents_text.splitlines()) > 150:
        _fail("AGENTS.md excede 150 linhas")

    required = [
        "docs/design-docs",
        "docs/product-specs",
        "src/orb_agent/main.py",
        "src/orb_agent/pipeline/analyze.py",
        "src/orb_agent/audit/logger.py",
        "src/orb_agent/observability/langsmith.py",
        "src/orb_agent/alerts/dispatcher.py",
    ]
    for rel in required:
        if not (ROOT / rel).exists():
            _fail(f"Caminho obrigatorio ausente: {rel}")

    if active_name:
        phase_match = re.search(r"fase-\d+", active_name)
        if phase_match and phase_match.group() not in readme_text.lower():
            print(f"[WARN] README pode nao mencionar {phase_match.group()}")

    print("[OK] Documentacao consistente")


if __name__ == "__main__":
    main()