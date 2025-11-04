# PowerShell script to run Django development server with virtual environment
# Usage: .\run_server.ps1

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Malamal Weekly - Django Server" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if virtual environment exists
if (-Not (Test-Path ".\venv\Scripts\python.exe")) {
    Write-Host "ERROR: Virtual environment not found!" -ForegroundColor Red
    Write-Host "Please create a virtual environment first:" -ForegroundColor Yellow
    Write-Host "  python -m venv venv" -ForegroundColor White
    exit 1
}

Write-Host "✓ Virtual environment found" -ForegroundColor Green
Write-Host "✓ Using: .\venv\Scripts\python.exe" -ForegroundColor Green
Write-Host ""

# Stop any running Python processes
Write-Host "Stopping any running Django servers..." -ForegroundColor Yellow
$pythonProcesses = Get-Process python -ErrorAction SilentlyContinue
if ($pythonProcesses) {
    $pythonProcesses | Stop-Process -Force
    Write-Host "✓ Stopped existing server" -ForegroundColor Green
    Start-Sleep -Seconds 2
} else {
    Write-Host "✓ No running servers found" -ForegroundColor Green
}

Write-Host ""
Write-Host "Starting Django development server..." -ForegroundColor Yellow
Write-Host "Server will be available at: http://127.0.0.1:8000/" -ForegroundColor Cyan
Write-Host "Press CTRL+C to stop the server" -ForegroundColor Gray
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Run Django server using virtual environment Python
.\venv\Scripts\python.exe manage.py runserver
