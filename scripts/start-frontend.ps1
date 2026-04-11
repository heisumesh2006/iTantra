$ErrorActionPreference = 'Stop'
Set-Location (Join-Path (Split-Path -Parent $PSScriptRoot) 'frontend')
npm.cmd run dev
if ($LASTEXITCODE) { throw 'Frontend exited with an error' }
