@echo off
REM ============================================================
REM Breakout Scanner - Automated EXE Build Script
REM ============================================================

echo.
echo ========================================
echo   BREAKOUT SCANNER EXE BUILDER
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://www.python.org/
    pause
    exit /b 1
)

echo [1/5] Python found! Checking dependencies...
echo.

REM Install required packages
echo [2/5] Installing dependencies...
pip install PyQt5 yfinance pandas openpyxl pyinstaller --quiet
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install dependencies
    pause
    exit /b 1
)

echo [3/5] Dependencies installed successfully!
echo.

REM Build EXE
echo [4/5] Building EXE file (this may take 2-3 minutes)...
pyinstaller --onefile --windowed --name="BreakoutScanner" ^
    --icon=scanner_icon.ico --add-data "." ^
    breakout_scanner_gui.py 2>nul

if %errorlevel% neq 0 (
    echo [ERROR] Failed to build EXE
    echo Building without icon...
    pyinstaller --onefile --windowed --name="BreakoutScanner" breakout_scanner_gui.py
)

echo [5/5] Build complete!
echo.
echo ========================================
echo   BUILD SUCCESSFUL!
echo ========================================
echo.
echo Executable location: dist\BreakoutScanner.exe
echo.
echo You can now:
echo  1. Run: dist\BreakoutScanner.exe
echo  2. Create desktop shortcut
echo  3. Share with others
echo.
pause
