# Dispara deploy EasyPanel via Deploy Webhook URL
param(
    [Parameter(Mandatory = $true)]
    [string]$DeployUrl
)

$ErrorActionPreference = "Stop"
Write-Host "Trigger deploy: $DeployUrl" -ForegroundColor Cyan
$r = Invoke-WebRequest -Uri $DeployUrl -Method GET -UseBasicParsing -TimeoutSec 120
Write-Host "Status: $($r.StatusCode)" -ForegroundColor Green
Write-Host $r.Content