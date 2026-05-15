param(
    [string]$SendKey = ""
)

$ErrorActionPreference = "Stop"
$RepoRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..")
$VenvPython = Join-Path $RepoRoot ".venv\Scripts\python.exe"
$Requirements = Join-Path $RepoRoot "windows_deploy\requirements.windows.txt"
$AutoTemplate = Join-Path $RepoRoot "windows_deploy\templates\auto_screen_config.windows.json"
$AgentTemplate = Join-Path $RepoRoot "windows_deploy\templates\agent_core_config.windows.json"
$AutoConfig = Join-Path $RepoRoot "auto_screen_config.ui.json"
$AgentConfig = Join-Path $RepoRoot "agent_core_config.ui.json"
$SecretDir = Join-Path $HOME ".codex\secrets"
$SecretFile = Join-Path $SecretDir "serverchan_sendkey.txt"

Set-Location $RepoRoot

if (-not (Test-Path $VenvPython)) {
    python -m venv .venv
}

& $VenvPython -m pip install --upgrade pip wheel
& $VenvPython -m pip install -r $Requirements

if (-not (Test-Path $AutoConfig)) {
    Copy-Item $AutoTemplate $AutoConfig
}

if (-not (Test-Path $AgentConfig)) {
    Copy-Item $AgentTemplate $AgentConfig
}

New-Item -ItemType Directory -Force -Path $SecretDir | Out-Null
if ($SendKey.Trim()) {
    Set-Content -Path $SecretFile -Value $SendKey.Trim() -Encoding UTF8
} elseif (-not (Test-Path $SecretFile)) {
    New-Item -ItemType File -Path $SecretFile | Out-Null
}

New-Item -ItemType Directory -Force -Path (Join-Path $RepoRoot "auto_screen_data\dashboard") | Out-Null

Write-Host "Windows deployment prepared."
Write-Host "Repo: $RepoRoot"
Write-Host "Python: $VenvPython"
Write-Host "Auto config: $AutoConfig"
Write-Host "Agent config: $AgentConfig"
Write-Host "ServerChan SendKey file: $SecretFile"
Write-Host "Start dashboard:"
Write-Host "  powershell -ExecutionPolicy Bypass -File .\windows_deploy\scripts\start_dashboard.ps1 -AutoStartScan"
