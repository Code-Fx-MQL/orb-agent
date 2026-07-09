# Registra scan ORB no Windows Task Scheduler via schtasks
param(
    [ValidateSet(5, 15)]
    [int]$IntervalMinutes = 15,
    [switch]$AllDay
)

$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $PSScriptRoot
$scanScript = Join-Path $PSScriptRoot "scheduled-scan.ps1"
$taskName = "ORB-Agent-Scan"

if (-not (Test-Path $scanScript)) {
    Write-Error "Script nao encontrado: $scanScript"
}

$taskCmd = "powershell.exe -NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File `"$scanScript`""

$prevEap = $ErrorActionPreference
$ErrorActionPreference = "SilentlyContinue"
$null = schtasks /Query /TN $taskName 2>&1
$exists = $LASTEXITCODE -eq 0
$ErrorActionPreference = $prevEap

if ($exists) {
    Write-Host "Removendo tarefa existente '$taskName'..." -ForegroundColor Yellow
    schtasks /Delete /TN $taskName /F | Out-Null
}

if ($AllDay) {
    schtasks /Create `
        /TN $taskName `
        /TR $taskCmd `
        /SC MINUTE `
        /MO $IntervalMinutes `
        /F | Out-Null
    $scheduleLabel = "Todos os dias, a cada $IntervalMinutes min (24h)"
} else {
    schtasks /Create `
        /TN $taskName `
        /TR $taskCmd `
        /SC WEEKLY `
        /D MON,TUE,WED,THU,FRI `
        /ST 08:00 `
        /RI $IntervalMinutes `
        /DU 09:00 `
        /F | Out-Null
    $scheduleLabel = "Seg-Sex, 08:00-17:00, a cada $IntervalMinutes min"
}

if ($LASTEXITCODE -ne 0) {
    Write-Error "Falha ao criar tarefa agendada (schtasks exit $LASTEXITCODE)"
}

Write-Host "=== Tarefa agendada criada ===" -ForegroundColor Green
Write-Host "Nome:    $taskName"
Write-Host "Horario: $scheduleLabel"
Write-Host "Script:  $scanScript"
Write-Host ""
Write-Host "Comandos uteis:"
Write-Host "  schtasks /Query /TN $taskName /V /FO LIST"
Write-Host "  schtasks /Run /TN $taskName"
Write-Host "  schtasks /Delete /TN $taskName /F"