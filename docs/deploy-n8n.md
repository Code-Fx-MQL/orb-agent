# Deploy workflow n8n — ORB Agent

Workflow de revisão IA + Telegram para alertas do ORB Agent.

## Arquitetura

```
orb-agent (scan / setup)
    POST https://8.fullscopetrade.com/webhook/orb-globalsend
         app=orb-agent · event_type=setup_found|scan_complete|paper_alert|test_ping
              │
              ▼
    n8n: ORB Agent — IA Review
         ├── setup_found → OpenAI → Telegram (approve/reject/review)
         ├── paper_alert → Telegram SL/TP
         ├── scan_complete → JSON ack
         └── test_ping → JSON ack
```

> **Nota:** O CRT Agent usa `globalsend` com `app=crt-agent`. O ORB usa path dedicado `orb-globalsend` para evitar conflito de webhooks no n8n.

## Importar no n8n

1. Abrir n8n → **Workflows** → **Import from File**
2. Selecionar `deploy/n8n/orb-agent-ai-review.workflow.json`
3. Configurar credenciais:
   - **OpenAI** → nó `OpenAI Review`
   - **Telegram** → nós `Telegram Approve`, `Reject`, `Review`, `Paper Alert`
4. Em cada nó Telegram, definir **Chat ID** (ex.: `-1004357973860`)
5. **Ativar** o workflow (toggle Active)
6. Se receber `Not orb-agent payload`, reimportar workflow atualizado (nó **Normalize Payload** após webhook)

## Configurar o agente

No `.env` local:

```env
ORB_WEBHOOK_ENABLED=true
ORB_WEBHOOK_URL=https://8.fullscopetrade.com/webhook/orb-globalsend
ORB_WEBHOOK_APP_ID=orb-agent
ORB_TELEGRAM_ENABLED=true
ORB_TELEGRAM_BOT_TOKEN=<seu-bot>
ORB_TELEGRAM_CHAT_ID=<seu-chat>
```

Testar:

```powershell
python scripts\test-webhook.py
python scripts\test-setup-found.py
```

Resposta esperada do n8n (`test_ping`):

```json
{ "ok": true, "handled": "test_ping", "app": "orb-agent", "message": "ORB Agent webhook OK" }
```

## Eventos suportados

| `event_type` | Ação n8n |
|--------------|----------|
| `setup_found` | OpenAI revisa → Telegram approve/reject/review |
| `paper_alert` | Telegram alerta SL/TP paper |
| `scan_complete` | Ack JSON (setups encontrados) |
| `test_ping` | Ack de teste |
| `live_order` / `live_blocked` | Ack genérico (fallback) |

## Payload `setup_found` (campo `data`)

Campos principais enviados pelo harness:

- `pair`, `setup_id`, `direction`, `confidence`
- `entry`, `stop_loss`, `take_profit`, `risk_reward`
- `setup.or_high`, `setup.or_low`, `setup.breakout_mode`
- `confluences`, `backtest`, `risk_check`
- `explanation_full`

## Troubleshooting

| Problema | Solução |
|----------|---------|
| HTTP 404 no teste | Workflow não importado/ativo ou URL errada |
| `Not orb-agent payload` | Verificar `ORB_WEBHOOK_APP_ID=orb-agent` |
| Telegram duplicado | Harness envia direto + n8n — desativar um dos canais se preferir só n8n |
| IA parse_error | Verificar credencial OpenAI e modelo `gpt-4o-mini` |