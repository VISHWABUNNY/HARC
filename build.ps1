# H.A.R.C. System - Windows PowerShell Build Launcher
# Wrapper for the cross-platform manage.js

Write-Host "🔨 Building H.A.R.C. System Release" -ForegroundColor Green
Write-Host "==================================="

node manage.js build

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Build failed." -ForegroundColor Red
    Pause
} else {
    Write-Host "✅ Build complete!" -ForegroundColor Green
}
