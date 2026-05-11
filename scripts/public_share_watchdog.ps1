$ErrorActionPreference = "SilentlyContinue"

$ProjectRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
$StartScript = Join-Path $PSScriptRoot "start_public_share.ps1"
$PublicUrlFile = Join-Path $ProjectRoot "public_url.txt"
$WatchdogLog = Join-Path $ProjectRoot "public_share_watchdog.log"
$Port = 8501

function Write-WatchdogLog($Message) {
    $line = "$(Get-Date -Format s) $Message"
    Add-Content -Path $WatchdogLog -Value $line -Encoding UTF8
}

Write-WatchdogLog "watchdog started"

while ($true) {
    $localOk = $false
    try {
        $response = Invoke-WebRequest -UseBasicParsing -Uri "http://127.0.0.1:$Port/_stcore/health" -TimeoutSec 5
        $localOk = $response.StatusCode -eq 200
    } catch {}

    $publicOk = $false
    $publicUrl = $null
    if (Test-Path $PublicUrlFile) {
        $publicUrl = (Get-Content -Path $PublicUrlFile -Raw).Trim()
    }
    if ($publicUrl) {
        try {
            $response = Invoke-WebRequest -UseBasicParsing -Uri $publicUrl -TimeoutSec 12
            $publicOk = $response.StatusCode -eq 200
        } catch {}
    }

    $cloudflared = Get-Process cloudflared -ErrorAction SilentlyContinue
    if (-not $localOk -or -not $publicOk -or -not $cloudflared) {
        Write-WatchdogLog "restart requested localOk=$localOk publicOk=$publicOk cloudflared=$([bool]$cloudflared)"
        powershell -ExecutionPolicy Bypass -File $StartScript | Out-Null
        Start-Sleep -Seconds 10
    }

    Start-Sleep -Seconds 30
}
