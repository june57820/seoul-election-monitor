$ErrorActionPreference = "Stop"

$ProjectRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
Set-Location $ProjectRoot

$Port = 8501
$StreamlitLog = Join-Path $ProjectRoot "streamlit.public.out.log"
$StreamlitErr = Join-Path $ProjectRoot "streamlit.public.err.log"
$TunnelOut = Join-Path $ProjectRoot "cloudflared.out.log"
$TunnelErr = Join-Path $ProjectRoot "cloudflared.err.log"
$PublicUrlFile = Join-Path $ProjectRoot "public_url.txt"
$StatusFile = Join-Path $ProjectRoot "public_share_status.json"
$CloudflaredDir = Join-Path $ProjectRoot "tools\cloudflared"
$CloudflaredExe = Join-Path $CloudflaredDir "cloudflared.exe"

New-Item -ItemType Directory -Force -Path $CloudflaredDir | Out-Null

if (-not (Test-Path $CloudflaredExe)) {
    Write-Host "Downloading cloudflared..."
    Invoke-WebRequest `
        -Uri "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe" `
        -OutFile $CloudflaredExe
}

$streamlitListener = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue
if (-not $streamlitListener) {
    Write-Host "Starting Streamlit on port $Port..."
    Start-Process `
        -FilePath python `
        -ArgumentList @("-m", "streamlit", "run", "app.py", "--server.headless", "true", "--server.address", "127.0.0.1", "--server.port", "$Port", "--browser.gatherUsageStats", "false") `
        -WorkingDirectory $ProjectRoot `
        -WindowStyle Hidden `
        -RedirectStandardOutput $StreamlitLog `
        -RedirectStandardError $StreamlitErr | Out-Null
}

$localReady = $false
for ($i = 0; $i -lt 30; $i++) {
    Start-Sleep -Seconds 1
    try {
        $response = Invoke-WebRequest -UseBasicParsing -Uri "http://127.0.0.1:$Port/_stcore/health" -TimeoutSec 3
        if ($response.StatusCode -eq 200) {
            $localReady = $true
            break
        }
    } catch {
        try {
            $response = Invoke-WebRequest -UseBasicParsing -Uri "http://127.0.0.1:$Port/" -TimeoutSec 3
            if ($response.StatusCode -eq 200) {
                $localReady = $true
                break
            }
        } catch {}
    }
}

if (-not $localReady) {
    Write-Error "Streamlit did not become reachable on http://127.0.0.1:$Port. Check streamlit.public.err.log."
}

Get-Process cloudflared -ErrorAction SilentlyContinue | Stop-Process -Force
if (Test-Path $TunnelOut) { Remove-Item -LiteralPath $TunnelOut -Force }
if (Test-Path $TunnelErr) { Remove-Item -LiteralPath $TunnelErr -Force }
if (Test-Path $PublicUrlFile) { Remove-Item -LiteralPath $PublicUrlFile -Force }

Write-Host "Starting public tunnel..."
Start-Process `
    -FilePath $CloudflaredExe `
    -ArgumentList @("tunnel", "--url", "http://127.0.0.1:$Port", "--no-autoupdate") `
    -WorkingDirectory $ProjectRoot `
    -WindowStyle Hidden `
    -RedirectStandardOutput $TunnelOut `
    -RedirectStandardError $TunnelErr | Out-Null

$publicUrl = $null
for ($i = 0; $i -lt 40; $i++) {
    Start-Sleep -Seconds 1
    $content = ""
    if (Test-Path $TunnelOut) { $content += Get-Content $TunnelOut -Raw -ErrorAction SilentlyContinue }
    if (Test-Path $TunnelErr) { $content += "`n" + (Get-Content $TunnelErr -Raw -ErrorAction SilentlyContinue) }
    $match = [regex]::Match($content, "https://[a-zA-Z0-9-]+\.trycloudflare\.com")
    if ($match.Success) {
        $publicUrl = $match.Value
        break
    }
}

if (-not $publicUrl) {
    Write-Error "Public URL was not created. Check cloudflared.err.log."
}

$publicUrl | Set-Content -Path $PublicUrlFile -Encoding UTF8

$status = [ordered]@{
    public_url = $publicUrl
    local_url = "http://127.0.0.1:$Port"
    created_at = (Get-Date).ToString("s")
    note = "trycloudflare quick tunnels are temporary. If this URL returns NXDOMAIN, run scripts/start_public_share.ps1 again and use the new public_url."
}
$status | ConvertTo-Json | Set-Content -Path $StatusFile -Encoding UTF8

Write-Host ""
Write-Host "Public URL:"
Write-Host $publicUrl
Write-Host ""
Write-Host "Saved to:"
Write-Host $PublicUrlFile
Write-Host ""
Write-Host "Keep this PC awake and the background Streamlit/cloudflared processes running while sharing the link."
