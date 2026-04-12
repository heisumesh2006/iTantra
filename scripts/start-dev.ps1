$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
$logDirectory = Join-Path $projectRoot 'storage/logs'
New-Item -ItemType Directory -Force -Path $logDirectory | Out-Null
foreach ($port in @(8000,5173)) {
    $listening = Get-NetTCPConnection -LocalPort $port -State Listen -ErrorAction SilentlyContinue
    if ($listening) { throw "Port $port is already in use. Open the existing app or stop that server first." }
}
$backend = Start-Process -FilePath (Join-Path $projectRoot '.venv/Scripts/python.exe') -ArgumentList '-X','utf8','-m','uvicorn','app.main:app','--host','127.0.0.1','--port','8000' -WorkingDirectory (Join-Path $projectRoot 'backend') -WindowStyle Hidden -PassThru -RedirectStandardOutput (Join-Path $logDirectory 'backend.log') -RedirectStandardError (Join-Path $logDirectory 'backend-error.log')
$frontend = Start-Process -FilePath 'cmd.exe' -ArgumentList '/c','npm.cmd run dev' -WorkingDirectory (Join-Path $projectRoot 'frontend') -WindowStyle Hidden -PassThru -RedirectStandardOutput (Join-Path $logDirectory 'frontend.log') -RedirectStandardError (Join-Path $logDirectory 'frontend-error.log')
@{backend=$backend.Id;frontend=$frontend.Id;backendStartTicks=[string]$backend.StartTime.ToUniversalTime().Ticks;frontendStartTicks=[string]$frontend.StartTime.ToUniversalTime().Ticks;created=(Get-Date).ToString('o')} | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $logDirectory 'servers.json')

$startupDeadline = (Get-Date).AddSeconds(30)
$ready = $false
while ((Get-Date) -lt $startupDeadline) {
    try {
        $health = Invoke-RestMethod -Uri 'http://127.0.0.1:8000/api/v1/health' -TimeoutSec 1
        $frontendStatus = (Invoke-WebRequest -Uri 'http://127.0.0.1:5173' -UseBasicParsing -TimeoutSec 1).StatusCode
        if ($health.status -eq 'ok' -and $frontendStatus -eq 200) { $ready = $true; break }
    } catch { Start-Sleep -Milliseconds 500 }
}
if (-not $ready) { throw 'Servers did not become ready within 30 seconds. Inspect storage/logs and use stop-dev.ps1 before retrying.' }
Write-Host 'Frontend: http://127.0.0.1:5173  Backend: http://127.0.0.1:8000/docs'
Write-Host 'Stop the owned servers with scripts/stop-dev.ps1.'
