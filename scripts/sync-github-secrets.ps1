# Sincroniza secrets e variables do .env local para GitHub Actions (orb-agent)
param(
    [string]$Repo = "Code-Fx-MQL/orb-agent",
    [string]$EnvFile = ".env",
    [string]$EasyPanelUrl = "https://0ikuso.easypanel.host"
)

$ErrorActionPreference = "Stop"

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

$gh = Get-Command gh -ErrorAction SilentlyContinue
if (-not $gh) {
    $ghPath = "C:\Program Files\GitHub CLI\gh.exe"
    if (Test-Path $ghPath) { $gh = $ghPath } else {
        Write-Error "GitHub CLI (gh) nao encontrado. winget install GitHub.cli"
    }
}

if (-not $env:GH_TOKEN) {
    $cred = "url=https://github.com" | git credential fill 2>$null
    $tokenLine = $cred -split "`n" | Where-Object { $_ -match '^password=' } | Select-Object -First 1
    if ($tokenLine) { $env:GH_TOKEN = $tokenLine -replace '^password=', '' }
}
if (-not $env:GH_TOKEN) {
    Write-Error "GH_TOKEN nao disponivel. Execute: gh auth login"
}

$root = Split-Path $PSScriptRoot -Parent
$local = Read-DotEnv (Join-Path $root $EnvFile)

$secretMap = @{
    EASYPANEL_URL = $EasyPanelUrl
    EASYPANEL_TOKEN = $env:EASYPANEL_TOKEN
    WEBHOOK_URL = if ($local["ORB_WEBHOOK_URL"]) { $local["ORB_WEBHOOK_URL"] } else { "https://8.fullscopetrade.com/webhook/orb-globalsend" }
    TELEGRAM_BOT_TOKEN = $local["ORB_TELEGRAM_BOT_TOKEN"]
    TELEGRAM_CHAT_ID = $local["ORB_TELEGRAM_CHAT_ID"]
    ORB_UI_PASSWORD = $local["ORB_UI_PASSWORD"]
    ORB_LIVE_APPROVAL_TOKEN = $local["ORB_LIVE_APPROVAL_TOKEN"]
    LANGSMITH_API_KEY = $local["ORB_LANGSMITH_API_KEY"]
}

$variables = @{
    WEBHOOK_APP_ID = if ($local["ORB_WEBHOOK_APP_ID"]) { $local["ORB_WEBHOOK_APP_ID"] } else { "orb-agent" }
    EASYPANEL_PROJECT = "localprojetos"
    EASYPANEL_SERVICE = "orb-agent"
}

Write-Host "=== GitHub Secrets ($Repo) ===" -ForegroundColor Cyan
foreach ($entry in $secretMap.GetEnumerator()) {
    if ([string]::IsNullOrWhiteSpace($entry.Value)) {
        Write-Host "[skip] $($entry.Key) (vazio)" -ForegroundColor DarkYellow
        continue
    }
    & $gh secret set $entry.Key --body $entry.Value -R $Repo | Out-Null
    Write-Host "[secret] $($entry.Key)" -ForegroundColor Green
}

Write-Host ""
Write-Host "=== GitHub Variables ($Repo) ===" -ForegroundColor Cyan
foreach ($entry in $variables.GetEnumerator()) {
    & $gh variable set $entry.Key --body $entry.Value -R $Repo | Out-Null
    Write-Host "[var] $($entry.Key) = $($entry.Value)" -ForegroundColor Green
}

Write-Host ""
Write-Host "Concluido: https://github.com/$Repo/settings/secrets/actions" -ForegroundColor Cyan
if (-not $secretMap["EASYPANEL_TOKEN"]) {
    Write-Host "AVISO: defina `$env:EASYPANEL_TOKEN antes de sync ou gh secret set EASYPANEL_TOKEN" -ForegroundColor Yellow
}