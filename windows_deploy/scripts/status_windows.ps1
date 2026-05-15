param(
    [int]$Port = 8787
)

$ErrorActionPreference = "Stop"
$BaseUrl = "http://127.0.0.1:$Port"

Write-Host "== /api/process =="
try {
    Invoke-RestMethod -Uri "$BaseUrl/api/process" -TimeoutSec 5 | ConvertTo-Json -Depth 8
} catch {
    Write-Host "dashboard not reachable: $($_.Exception.Message)"
}

Write-Host ""
Write-Host "== /api/serverchan-key =="
try {
    Invoke-RestMethod -Uri "$BaseUrl/api/serverchan-key" -TimeoutSec 5 | ConvertTo-Json -Depth 5
} catch {
    Write-Host "dashboard not reachable: $($_.Exception.Message)"
}

Write-Host ""
Write-Host "== recent auto_screen log =="
$RepoRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..")
$LogPath = Join-Path $RepoRoot "auto_screen_data\dashboard\auto_screen.log"
if (Test-Path $LogPath) {
    Get-Content -Path $LogPath -Tail 30
} else {
    Write-Host "log not found: $LogPath"
}
