@echo off
REM Windows Batch script to run Django development server
REM Usage: Double-click this file or run: run_server.bat

echo ========================================
echo   Malamal Weekly - Django Server
echo ========================================
echo.

REM Check if virtual environment exists
if not exist "venv\Scripts\python.exe" (
    echo ERROR: Virtual environment not found!
    echo Please create a virtual environment first:
    echo   python -m venv venv
    pause
    exit /b 1
)

echo [OK] Virtual environment found
echo [OK] Using: venv\Scripts\python.exe
echo.

REM Stop any running Python processes (optional)
echo Checking for running Django servers...
taskkill /F /IM python.exe >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] Stopped existing server
    timeout /t 2 /nobreak >nul
) else (
    echo [OK] No running servers found
)

echo.
echo Starting Django development server...
echo Server will be available at: http://127.0.0.1:8000/
echo Press CTRL+C to stop the server
echo.
echo ========================================
echo.

REM Run Django server using virtual environment Python
venv\Scripts\python.exe manage.py runserver

pause
