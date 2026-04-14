# H.A.R.C. System - Windows PowerShell Startup Launcher
# Wrapper for the cross-platform manage.js

Write-Host "🚀 H.A.R.C. System - Windows Initialization" -ForegroundColor Cyan
Write-Host "==========================================="

# Check for Node.js
if (!(Get-Command node -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Node.js not found. Please install Node.js from https://nodejs.org/" -ForegroundColor Red
    Pause
    exit
}

node manage.js start

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Application failed to start." -ForegroundColor Red
    Pause
}
