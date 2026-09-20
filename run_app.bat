@echo off
TITLE TrendMaster AI - Gold and Stock Prediction SaaS
COLOR 06

echo ================================================================
echo               TRENDMASTER AI - SAAS WEB APP
echo      Gold and Stock Price Forecasting (USA and India)
echo ================================================================
echo.

cd /d "%~dp0"

IF NOT EXIST "venv\Scripts\python.exe" (
    echo [ERROR] Virtual environment not found at: %~dp0venv
    echo Please ensure the venv folder exists in this directory.
    pause
    exit /b 1
)

echo [1/3] Checking database migrations...
venv\Scripts\python.exe manage.py migrate --noinput
IF %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Migration failed.
    pause
    exit /b 1
)

echo.
echo [2/3] Initializing demo accounts and asset universe...
venv\Scripts\python.exe manage.py create_demo_trader
echo.

echo [3/3] Opening browser at http://127.0.0.1:8000 ...
start "" http://127.0.0.1:8000

echo.
echo ================================================================
echo   Django Server is starting...
echo   URL: http://127.0.0.1:8000
echo.
echo   Demo Login Credentials:
echo     [Pro Trader] Email: trader@trendmaster.ai  Password: GoldTrader2026!
echo     [Admin User] Email: admin@trendmaster.ai   Password: AdminMaster2026!
echo.
echo   Keep this window OPEN while using the application.
echo   Press CTRL+C in this window to stop the server.
echo ================================================================
echo.

venv\Scripts\python.exe manage.py runserver 127.0.0.1:8000

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [SERVER STOPPED OR FAILED TO START]
    pause
)
