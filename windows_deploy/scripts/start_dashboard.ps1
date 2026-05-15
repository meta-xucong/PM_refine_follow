param(
    [int]$Port = 8787,
    [switch]$AutoStartScan
)

$ErrorActionPreference = "Stop"
$RepoRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..")
$VenvPython = Join-Path $RepoRoot ".venv\Scripts\python.exe"

if (-not (Test-Path $VenvPython)) {
    Write-Host "Virtualenv not found. Preparing Windows deployment first..."
    & powershell -ExecutionPolicy Bypass -File (Join-Path $RepoRoot "windows_deploy\scripts\prepare_windows.ps1")
}

Set-Location $RepoRoot
$env:PYTHONUTF8 = "1"
$env:PYTHONIOENCODING = "utf-8"
$env:PM_AUTOSTART_SCAN = if ($AutoStartScan) { "1" } else { "0" }

Write-Host "Dashboard: http://127.0.0.1:$Port"
Write-Host "Press Ctrl+C to stop dashboard."
& $VenvPython -m dashboard.server --host 127.0.0.1 --port $Port
