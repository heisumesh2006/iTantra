param([switch]$WithModels)
$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $projectRoot
if (-not (Test-Path '.venv/Scripts/python.exe')) { python -m venv .venv; if ($LASTEXITCODE) { throw 'Virtual environment creation failed' } }
$requirements = if ($WithModels) { 'backend/requirements/ml.txt' } else { 'backend/requirements/base.txt' }
& '.venv/Scripts/python.exe' -m pip install -r $requirements -r backend/requirements/dev.txt
if ($LASTEXITCODE) { throw 'Dependency installation failed' }
npm.cmd ci --prefix frontend
if ($LASTEXITCODE) { throw 'Frontend installation failed' }
if (-not (Test-Path '.env')) { Copy-Item -LiteralPath '.env.example' -Destination '.env' }
Write-Host 'Setup complete. Model weights require an explicit scripts/download-models.py command.'
