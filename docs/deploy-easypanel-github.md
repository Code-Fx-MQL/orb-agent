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

## 5. Deploy via webhook (EasyPanel)

Se o serviço já tem source configurado (Git/ZIP), use o **Deploy Webhook** do painel:

```powershell
.\scripts\trigger-deploy-webhook.ps1 -DeployUrl "http://SEU-PAINEL:3000/api/deploy/SEU_TOKEN"
# ou tudo num comando:
.\scripts\deploy-easypanel.ps1 -DeployWebhookUrl "http://SEU-PAINEL:3000/api/deploy/SEU_TOKEN"
```

Resposta esperada: `200` + `Deploying...`

> O URL `/api/deploy/...` **nao** e o token API tRPC (`Settings -> API`). Sao credenciais diferentes.

---

## 6. Deploy local (API EasyPanel tRPC)

```powershell
cd C:\Users\Rsantos\orb-agent
$env:EASYPANEL_TOKEN = "SEU_TOKEN"   # Settings -> API no painel
.\scripts\deploy-easypanel.ps1
```

Gera `deploy/easypanel/.env.production`, empacota `orb-agent-easypanel-deploy.zip` e faz upload para `localprojetos/orb-agent`.

Sincronizar secrets GitHub (apos `gh auth login`):

```powershell
$env:EASYPANEL_TOKEN = "SEU_TOKEN"
.\scripts\sync-github-secrets.ps1
```

---

## 7. Disparar deploy GitHub

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