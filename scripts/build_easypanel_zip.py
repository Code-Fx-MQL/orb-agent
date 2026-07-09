#!/usr/bin/env python3
"""Empacota o projeto para upload EasyPanel (sem .venv, .git, secrets locais)."""

from __future__ import annotations

import zipfile
from pathlib import Path

EXCLUDE_DIRS = {
    ".git",
    ".venv",
    "venv",
    "__pycache__",
    ".pytest_cache",
    ".ruff_cache",
    "node_modules",
    "terminals",
}
EXCLUDE_FILES_SUFFIX = {".zip", ".pyc"}


def should_skip(path: Path) -> bool:
    parts = set(path.parts)
    if parts & EXCLUDE_DIRS:
        return True
    if path.name == ".env":
        return True
    if path.name in ("docker-compose.yml", ".env.production"):
        return True
    if path.suffix in EXCLUDE_FILES_SUFFIX:
        return True
    if path.name.startswith("orb-agent-easypanel") and path.suffix == ".zip":
        return True
    return False


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    out_zip = root / "orb-agent-easypanel-deploy.zip"
    compose_src = root / "deploy" / "easypanel" / "compose.yml"
    env_prod = root / "deploy" / "easypanel" / ".env.production"

    if not compose_src.exists():
        raise SystemExit(f"Compose nao encontrado: {compose_src}")
    if not env_prod.exists():
        raise SystemExit(f"Env producao nao encontrado: {env_prod} — rode generate_env_production.py")

    if out_zip.exists():
        out_zip.unlink()

    with zipfile.ZipFile(out_zip, "w", zipfile.ZIP_DEFLATED) as zf:
        for path in root.rglob("*"):
            if path.is_dir():
                continue
            if should_skip(path):
                continue
            rel = path.relative_to(root)
            zf.write(path, rel.as_posix())

        zf.writestr("docker-compose.yml", compose_src.read_text(encoding="utf-8"))
        zf.writestr(
            "deploy/easypanel/.env.production",
            env_prod.read_text(encoding="utf-8"),
        )

    print(f"Pacote: {out_zip} ({out_zip.stat().st_size // 1024} KB)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())