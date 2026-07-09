$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
python -m venv "$root\.venv"
Push-Location $root
& "$root\.venv\Scripts\pip.exe" install -e ".[dev]"
Pop-Location
Write-Host "Setup OK" -ForegroundColor Green