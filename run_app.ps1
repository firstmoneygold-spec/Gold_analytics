# TrendMaster AI PowerShell Launcher
$Host.UI.RawUI.WindowTitle = "TrendMaster AI - Gold & Stock Prediction SaaS"
Write-Host "================================================================" -ForegroundColor Yellow
Write-Host "              TRENDMASTER AI - SAAS WEB APP" -ForegroundColor Yellow
Write-Host "     Gold & Stock Price Forecasting (USA & India Markets)" -ForegroundColor Yellow
Write-Host "================================================================" -ForegroundColor Yellow
Write-Host ""

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptDir

if (-not (Test-Path "$ScriptDir\venv\Scripts\python.exe")) {
    Write-Host "[ERROR] Virtual environment not found at $ScriptDir\venv" -ForegroundColor Red
    Pause
    Exit
}

Write-Host "[1/3] Applying database migrations..." -ForegroundColor Cyan
& "$ScriptDir\venv\Scripts\python.exe" manage.py migrate --noinput

Write-Host "`n[2/3] Ensuring demo accounts & asset universe are ready..." -ForegroundColor Cyan
& "$ScriptDir\venv\Scripts\python.exe" manage.py create_demo_trader

Write-Host "`n[3/3] Launching web browser at http://127.0.0.1:8000 ..." -ForegroundColor Green
Start-Process "http://127.0.0.1:8000"

Write-Host "`n================================================================" -ForegroundColor Yellow
Write-Host "  Django Server is running at http://127.0.0.1:8000" -ForegroundColor Green
Write-Host ""
Write-Host "  Demo Login:" -ForegroundColor White
Write-Host "    Pro Trader -> Email: trader@trendmaster.ai | Pass: GoldTrader2026!" -ForegroundColor White
Write-Host "    Admin User -> Email: admin@trendmaster.ai  | Pass: AdminMaster2026!" -ForegroundColor White
Write-Host ""
Write-Host "  Press CTRL+C to stop the server anytime." -ForegroundColor DarkGray
Write-Host "================================================================" -ForegroundColor Yellow
Write-Host ""

& "$ScriptDir\venv\Scripts\python.exe" manage.py runserver 127.0.0.1:8000
