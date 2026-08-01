@echo off
REM ============================================================
REM BREAKOUT SCANNER - BUILD EXE ON WINDOWS
REM ============================================================
REM Run this file on Windows to build the EXE automatically

echo.
echo ========================================
echo   BREAKOUT SCANNER EXE BUILDER
echo ========================================
echo.

REM Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python not found!
    echo Install Python from: https://www.python.org/
    echo Important: Check "Add Python to PATH" during setup
    pause
    exit /b 1
)

echo [1/4] Python found!
echo.

REM Install dependencies
echo [2/4] Installing dependencies...
pip install PyQt5 yfinance pandas openpyxl pyinstaller -q
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install dependencies
    pause
    exit /b 1
)

echo [3/4] Dependencies installed!
echo.

REM Build EXE
echo [4/4] Building EXE file (takes 3-5 minutes)...
pyinstaller --onefile --windowed --name="BreakoutScanner" breakout_scanner_gui.py

if %errorlevel% neq 0 (
    echo [ERROR] Build failed!
    pause
    exit /b 1
)

echo.
echo ========================================
echo   BUILD SUCCESSFUL!
echo ========================================
echo.
echo Your executable is ready!
echo Location: dist\BreakoutScanner.exe
echo.
echo You can now:
echo  1. Double-click dist\BreakoutScanner.exe to run
echo  2. Create a desktop shortcut
echo  3. Share with others
echo.
pause
