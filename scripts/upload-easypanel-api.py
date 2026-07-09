#!/usr/bin/env python3
"""Upload ORB Agent para EasyPanel via API tRPC (Compose + deploy)."""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
import zipfile
from pathlib import Path


def trpc_post(base_url: str, token: str, procedure: str, payload: dict) -> dict:
    url = f"{base_url.rstrip('/')}/api/trpc/{procedure}"
    body = json.dumps({"json": payload}).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=body,
        method="POST",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    if "error" in data:
        raise RuntimeError(data["error"].get("json", data["error"]))
    return data.get("result", {}).get("data", {}).get("json", data.get("json", data))


def trpc_get(base_url: str, token: str, procedure: str, payload: dict | None = None) -> dict:
    query = ""
    if payload is not None:
        query = "?input=" + urllib.parse.quote(json.dumps({"json": payload}))
    url = f"{base_url.rstrip('/')}/api/trpc/{procedure}{query}"
    req = urllib.request.Request(
        url,
        method="GET",
        headers={"Authorization": f"Bearer {token}"},
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    if "error" in data:
        raise RuntimeError(data["error"].get("json", data["error"]))
    return data.get("result", {}).get("data", {}).get("json", data.get("json", data))


def load_env_production(path: Path) -> str:
    lines = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        lines.append(line)
    return "\n".join(lines) + "\n"


def read_compose_from_zip(zip_path: Path) -> str:
    with zipfile.ZipFile(zip_path) as zf:
        for name in ("docker-compose.yml", "compose.yml"):
            try:
                return zf.read(name).decode("utf-8")
            except KeyError:
                continue
    raise FileNotFoundError("docker-compose.yml nao encontrado no ZIP")


def main() -> int:
    parser = argparse.ArgumentParser(description="Upload ORB Agent para EasyPanel")
    parser.add_argument("--zip", default="orb-agent-easypanel-deploy.zip")
    parser.add_argument("--project", default="localprojetos")
    parser.add_argument("--service", default="orb-agent")
    parser.add_argument("--env-file", default="deploy/easypanel/.env.production")
    parser.add_argument("--url", default=os.environ.get("EASYPANEL_URL", ""))
    parser.add_argument("--token", default=os.environ.get("EASYPANEL_TOKEN", ""))
    parser.add_argument("--proxy-port", type=int, default=8501)
    args = parser.parse_args()

    if not args.url or not args.token:
        print("Defina EASYPANEL_URL e EASYPANEL_TOKEN (Settings -> API no painel).")
        return 1

    root = Path(__file__).resolve().parents[1]
    zip_path = root / args.zip
    env_path = root / args.env_file
    if not zip_path.exists():
        print(f"ZIP nao encontrado: {zip_path}")
        return 1

    compose_yaml = read_compose_from_zip(zip_path)
    env_text = load_env_production(env_path)

    print(f"EasyPanel: {args.url}")
    user = trpc_get(args.url, args.token, "auth.getUser")
    print(f"Auth OK: {user.get('email', 'token valido')}")

    projects = trpc_get(args.url, args.token, "projects.listProjects")
    names = {p.get("name") for p in projects}
    if args.project not in names:
        trpc_post(args.url, args.token, "projects.createProject", {"name": args.project})
        print(f"Projeto criado: {args.project}")

    existing = trpc_get(args.url, args.token, "projects.inspectProject", {"projectName": args.project})
    service_names = {s.get("name") for s in existing.get("services", [])}
    if args.service not in service_names:
        trpc_post(
            args.url,
            args.token,
            "services.compose.createService",
            {"projectName": args.project, "serviceName": args.service},
        )
        print(f"Servico compose criado: {args.service}")

    trpc_post(
        args.url,
        args.token,
        "services.compose.updateSourceInline",
        {
            "projectName": args.project,
            "serviceName": args.service,
            "compose": compose_yaml,
        },
    )
    trpc_post(
        args.url,
        args.token,
        "services.compose.updateEnv",
        {
            "projectName": args.project,
            "serviceName": args.service,
            "env": env_text,
        },
    )
    trpc_post(
        args.url,
        args.token,
        "services.compose.deployService",
        {"projectName": args.project, "serviceName": args.service},
    )
    print("Deploy compose iniciado.")
    print("Upload via API concluido.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except urllib.error.HTTPError as exc:
        print(f"HTTP {exc.code}: {exc.read().decode('utf-8', errors='replace')[:500]}")
        raise SystemExit(1) from exc
    except Exception as exc:
        print(f"Erro: {exc}")
        raise SystemExit(1) from exc