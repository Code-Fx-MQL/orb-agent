# Deploy EasyPanel + GitHub Actions — Agente ORB

> **Repositório:** [Code-Fx-MQL/orb-agent](https://github.com/Code-Fx-MQL/orb-agent)

Guia para deploy do dashboard ORB no EasyPanel via workflow GitHub Actions.

---

## Visão geral

```
workflow_dispatch (GitHub)
        │
        ▼
  testes unitários
        │
        ▼
  gera deploy/easypanel/.env.production
        │
        ▼
  empacota ZIP (compose + código)
        │
        ▼
  upload via API EasyPanel → serviço orb-agent
```

| Componente | Valor |
|------------|-------|
| Workflow | `.github/workflows/deploy.yml` |
| Compose ZIP | `deploy/easypanel/compose.yml` |
| Ambiente GitHub | `production` |

---

## 1. Token EasyPanel

1. Painel EasyPanel → **Settings** → **API**
2. Criar token (ex.: `orb-agent-github-deploy`)
3. Guardar como secret `EASYPANEL_TOKEN`

Verificação opcional:

```powershell
$env:EASYPANEL_URL = "https://SEU-PAINEL.easypanel.host"
Set-Item -Path Env:EASYPANEL_TOKEN -Value "SEU_TOKEN"
python scripts/upload-easypanel-api.py --zip orb-agent-easypanel-deploy.zip
# (requer ZIP gerado previamente)
```

---

## 2. Secrets GitHub (repositório orb-agent)

| Secret / Variable | Descrição |
|-------------------|-----------|
| `EASYPANEL_URL` | URL do painel |
| `EASYPANEL_TOKEN` | Token API |
| `EASYPANEL_PROJECT` (var) | Nome do projeto |
| `EASYPANEL_SERVICE` (var) | Nome do serviço compose (`orb-agent`) |
| `WEBHOOK_URL` | Webhook n8n |
| `TELEGRAM_BOT_TOKEN` | Bot Telegram |
| `TELEGRAM_CHAT_ID` | Chat ID |
| `ORB_UI_PASSWORD` | Password dashboard |
| `ORB_LIVE_APPROVAL_TOKEN` | Token live gate |
| `LANGSMITH_API_KEY` | Opcional |

```powershell
gh secret set EASYPANEL_TOKEN --body "SEU_TOKEN" -R Code-Fx-MQL/orb-agent
gh variable set EASYPANEL_PROJECT --body "localprojetos" -R Code-Fx-MQL/orb-agent
gh variable set EASYPANEL_SERVICE --body "orb-agent" -R Code-Fx-MQL/orb-agent
```

---

## 3. Deploy local (Docker)

```powershell
cd C:\Users\Rsantos\orb-agent
Copy-Item .env.example .env
docker compose up --build -d
```

Dashboard: `http://localhost:8501`

Volume `./data` persiste paper, memória e audit.

---

## 4. Scan agendado (Windows)

```powershell
.\scripts\register-scheduled-task.ps1 -IntervalMinutes 15
# ou 24h:
.\scripts\register-scheduled-task.ps1 -IntervalMinutes 15 -AllDay

# Teste manual:
.\scripts\scheduled-scan.ps1
```

---

## 5. Disparar deploy GitHub

1. GitHub → **Actions** → **Deploy EasyPanel**
2. **Run workflow**
3. Verificar logs do job `deploy`

---

## Variáveis de produção mínimas

```env
ORB_MODE=paper
ORB_PAIRS=XAUUSD,EURUSD
ORB_WEBHOOK_ENABLED=true
ORB_WEBHOOK_URL=https://...
ORB_WEBHOOK_APP_ID=orb-agent
ORB_TELEGRAM_ENABLED=true
ORB_TELEGRAM_BOT_TOKEN=...
ORB_TELEGRAM_CHAT_ID=...
ORB_UI_PASSWORD=...
```

Volume obrigatório no EasyPanel: `/app/data`