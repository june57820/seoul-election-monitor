$ErrorActionPreference = "Stop"

$ProjectRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
$WatchdogScript = Join-Path $PSScriptRoot "public_share_watchdog.ps1"

$existing = Get-CimInstance Win32_Process | Where-Object {
    $_.CommandLine -like "*public_share_watchdog.ps1*"
}

if (-not $existing) {
    Start-Process `
        -FilePath powershell `
        -ArgumentList @("-ExecutionPolicy", "Bypass", "-File", $WatchdogScript) `
        -WorkingDirectory $ProjectRoot `
        -WindowStyle Hidden | Out-Null
    Write-Host "Public share watchdog started."
} else {
    Write-Host "Public share watchdog is already running."
}
