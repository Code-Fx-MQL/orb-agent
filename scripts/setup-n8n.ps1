# Configura webhook n8n ORB (path dedicado orb-globalsend)
$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
$envFile = Join-Path $root ".env"

if (-not (Test-Path $envFile)) {
    Copy-Item (Join-Path $root ".env.example") $envFile
    Write-Host "[OK] .env criado" -ForegroundColor Green
}

Write-Host "=== Setup n8n ORB Agent ===" -ForegroundColor Cyan
Write-Host ""
$n8nUrl = Read-Host "n8n Webhook URL (default: https://8.fullscopetrade.com/webhook/orb-globalsend)"
if (-not $n8nUrl) { $n8nUrl = "https://8.fullscopetrade.com/webhook/orb-globalsend" }

$content = Get-Content $envFile -Raw

function Set-EnvVar([string]$name, [string]$value) {
    if ($content -match "(?m)^${name}=.*") {
        $script:content = $content -replace "(?m)^${name}=.*", "${name}=${value}"
    } else {
        $script:content += "`n${name}=${value}"
    }
}

Set-EnvVar "ORB_WEBHOOK_ENABLED" "true"
Set-EnvVar "ORB_WEBHOOK_URL" $n8nUrl
Set-EnvVar "ORB_WEBHOOK_APP_ID" "orb-agent"

Set-Content $envFile $content.TrimEnd() -Encoding UTF8
Write-Host "`n[OK] .env atualizado" -ForegroundColor Green
Write-Host "Importar workflow: deploy\n8n\orb-agent-ai-review.workflow.json" -ForegroundColor Yellow
Write-Host "Guia: docs\deploy-n8n.md" -ForegroundColor Yellow

$python = Join-Path $root ".venv\Scripts\python.exe"
if (Test-Path $python) {
    Write-Host "`nEnviando test_ping..." -ForegroundColor Cyan
    & $python (Join-Path $PSScriptRoot "test-webhook.py")
}