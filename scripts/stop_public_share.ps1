$ErrorActionPreference = "SilentlyContinue"

Get-Process cloudflared | Stop-Process -Force

Write-Host "Public Cloudflare tunnel stopped."
Write-Host "Streamlit was left running so local development is not interrupted."
