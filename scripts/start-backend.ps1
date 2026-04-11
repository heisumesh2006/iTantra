$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
Set-Location (Join-Path $projectRoot 'backend')
& (Join-Path $projectRoot '.venv/Scripts/python.exe') -X utf8 -m uvicorn app.main:app --host 127.0.0.1 --port 8000
if ($LASTEXITCODE) { throw 'Backend exited with an error' }
