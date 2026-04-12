$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
$pidPath = Join-Path $projectRoot 'storage/logs/servers.json'
if (-not (Test-Path -LiteralPath $pidPath)) { Write-Host 'No saved server processes.'; exit 0 }
$saved = Get-Content -LiteralPath $pidPath -Raw | ConvertFrom-Json
foreach ($role in @('backend','frontend')) {
    $serverProcessId = $saved.$role
    $server = Get-Process -Id $serverProcessId -ErrorAction SilentlyContinue
    if (-not $server) { continue }
    $identityProperty = $role + 'StartTicks'
    $expectedTicks = $saved.$identityProperty
    if ($expectedTicks) {
        $sameProcess = ([string]$server.StartTime.ToUniversalTime().Ticks -eq [string]$expectedTicks)
    } else {
        # Legacy records require a bounded birth-time match; never accept any newer recycled PID.
        $sameProcess = [Math]::Abs(($server.StartTime - [datetime]$saved.created).TotalSeconds) -le 10
    }
    if (-not $sameProcess) { Write-Warning "PID $serverProcessId was reused; leaving it untouched."; continue }
    & taskkill.exe /PID $serverProcessId /T /F | Out-Null
    if ($LASTEXITCODE -ne 0) { throw "Could not stop verified project process $serverProcessId" }
}
Remove-Item -LiteralPath $pidPath
