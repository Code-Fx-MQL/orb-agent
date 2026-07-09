# Rotina agendada - scan ORB + alertas paper + webhook n8n
$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
Set-Location $root

$python = Join-Path $root ".venv\Scripts\python.exe"
$scanPy = Join-Path $PSScriptRoot "scheduled_scan.py"

if (-not (Test-Path $python)) { Write-Error "venv nao encontrado - rode setup.ps1" }
if (-not (Test-Path $scanPy)) { Write-Error "Script nao encontrado: $scanPy" }

Write-Host "=== ORB Scheduled Scan $(Get-Date -Format 'yyyy-MM-dd HH:mm') ===" -ForegroundColor Cyan
& $python $scanPy
Write-Host "[OK] Scan concluido" -ForegroundColor Green