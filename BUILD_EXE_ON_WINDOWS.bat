@echo off
echo.
echo =====================================================================
echo          Stock Scanner Pro - Building Standalone EXE
echo =====================================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH!
    echo Please install Python 3.8+ from python.org
    pause
    exit /b 1
)

echo [1/4] Installing PyInstaller...
python -m pip install pyinstaller -q
if errorlevel 1 (
    echo ERROR: Failed to install PyInstaller
    pause
    exit /b 1
)

echo [2/4] Installing required dependencies...
python -m pip install yfinance pandas PyQt5 -q
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

echo [3/4] Building EXE (this may take 1-2 minutes)...
python -m pyinstaller ^
    --onefile ^
    --windowed ^
    --name "Stock_Scanner_Pro" ^
    --add-data "." ^
    --hidden-import=yfinance ^
    --hidden-import=pandas ^
    --hidden-import=pytz ^
    --hidden-import=requests ^
    --collect-all=yfinance ^
    --collect-all=pandas ^
    stock_scanner_exe.py

if errorlevel 1 (
    echo ERROR: Build failed!
    pause
    exit /b 1
)

echo.
echo =====================================================================
echo                        BUILD SUCCESSFUL!
echo =====================================================================
echo.
echo Your EXE file is ready at:
echo     dist\Stock_Scanner_Pro.exe
echo.
echo To use it:
echo   1. Copy dist\Stock_Scanner_Pro.exe to any folder
echo   2. Double-click to run (NO dependencies needed!)
echo   3. Click "Start Scanning" to begin
echo.
echo You can delete the "build" and "__pycache__" folders if you want
echo =====================================================================
echo.
pause
