param([string]$HarnessPath = "")
$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
if (-not $HarnessPath) {
    $HarnessPath = Join-Path (Split-Path -Parent $root) "trading-harness"
}
& "$HarnessPath\scripts\validate-harness.ps1" -RepoPath $root