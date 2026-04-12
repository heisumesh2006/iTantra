$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
Set-Location (Join-Path $projectRoot 'backend')
& (Join-Path $projectRoot '.venv/Scripts/python.exe') -X utf8 -m pytest -q
if ($LASTEXITCODE) { throw 'Backend tests failed' }
& (Join-Path $projectRoot '.venv/Scripts/python.exe') -m ruff check .
if ($LASTEXITCODE) { throw 'Backend lint failed' }
Set-Location (Join-Path $projectRoot 'frontend')
npm.cmd test
if ($LASTEXITCODE) { throw 'Frontend tests failed' }
npm.cmd run format:check
if ($LASTEXITCODE) { throw 'Frontend formatting check failed' }
npm.cmd run build
if ($LASTEXITCODE) { throw 'Frontend build failed' }
