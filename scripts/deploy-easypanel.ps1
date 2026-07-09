# Deploy ORB Agent para EasyPanel (gera env, ZIP e upload API)
param(
    [string]$EasyPanelUrl = "https://0ikuso.easypanel.host",
    [string]$Project = "localprojetos",
    [string]$Service = "orb-agent",
    [switch]$SkipUpload
)

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
Set-Location $root

function Read-DotEnv([string]$Path) {
    $map = @{}
    if (-not (Test-Path $Path)) { return $map }
    Get-Content $Path | ForEach-Object {
        $line = $_.Trim()
        if ($line -eq "" -or $line.StartsWith("#")) { return }
        $idx = $line.IndexOf("=")
        if ($idx -lt 1) { return }
        $key = $line.Substring(0, $idx).Trim()
        $val = $line.Substring($idx + 1).Trim()
        $map[$key] = $val
    }
    return $map
}

$python = Join-Path $root ".venv\Scripts\python.exe"
if (-not (Test-Path $python)) { $python = "python" }

$local = Read-DotEnv (Join-Path $root ".env")

# Mapear .env local -> variaveis CI
$map = @{
    WEBHOOK_URL = if ($local["ORB_WEBHOOK_URL"]) { $local["ORB_WEBHOOK_URL"] } else { "https://8.fullscopetrade.com/webhook/orb-globalsend" }
    TELEGRAM_BOT_TOKEN = $local["ORB_TELEGRAM_BOT_TOKEN"]
    TELEGRAM_CHAT_ID = $local["ORB_TELEGRAM_CHAT_ID"]
    ORB_UI_PASSWORD = $local["ORB_UI_PASSWORD"]
    ORB_LIVE_APPROVAL_TOKEN = $local["ORB_LIVE_APPROVAL_TOKEN"]
    LANGSMITH_API_KEY = $local["ORB_LANGSMITH_API_KEY"]
}
foreach ($entry in $map.GetEnumerator()) {
    if ($entry.Value) {
        Set-Item -Path "Env:$($entry.Key)" -Value $entry.Value
    }
}
if (-not $env:ORB_WEBHOOK_APP_ID) {
    $env:ORB_WEBHOOK_APP_ID = if ($local["ORB_WEBHOOK_APP_ID"]) { $local["ORB_WEBHOOK_APP_ID"] } else { "orb-agent" }
}

Write-Host "=== ORB Agent - Deploy EasyPanel ===" -ForegroundColor Cyan
Write-Host "1/3 Gerar .env.production"
& $python (Join-Path $PSScriptRoot "generate_env_production.py")

Write-Host "2/3 Empacotar ZIP"
& $python (Join-Path $PSScriptRoot "build_easypanel_zip.py")

if ($SkipUpload) {
    Write-Host "[OK] Pacote pronto (upload ignorado): orb-agent-easypanel-deploy.zip" -ForegroundColor Green
    exit 0
}

$token = $env:EASYPANEL_TOKEN
if (-not $token) {
    Write-Host ""
    Write-Host "EASYPANEL_TOKEN nao definido." -ForegroundColor Yellow
    Write-Host "  EasyPanel -> Settings -> API -> gerar token" -ForegroundColor Yellow
    Write-Host "  `$env:EASYPANEL_TOKEN = 'SEU_TOKEN'" -ForegroundColor Yellow
    Write-Host "  .\scripts\deploy-easypanel.ps1" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "ZIP gerado: orb-agent-easypanel-deploy.zip" -ForegroundColor Green
    exit 1
}

$env:EASYPANEL_URL = $EasyPanelUrl
Write-Host "3/3 Upload -> $EasyPanelUrl ($Project / $Service)"
& $python (Join-Path $PSScriptRoot "upload-easypanel-api.py") `
    --zip orb-agent-easypanel-deploy.zip `
    --project $Project `
    --service $Service `
    --url $EasyPanelUrl `
    --token $token

Write-Host "[OK] Deploy EasyPanel concluido" -ForegroundColor Green