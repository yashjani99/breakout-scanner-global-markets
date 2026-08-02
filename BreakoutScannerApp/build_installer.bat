@echo off
setlocal
cd /d "%~dp0"

echo ============================================================
echo   Breakout Scanner Indian Market v2.0 - Windows Build
echo ============================================================

where python >nul 2>nul
if errorlevel 1 (
    echo.
    echo Python was not found on PATH.
    echo Install Python 3.10 - 3.12 (64-bit^) from https://www.python.org/downloads/
    echo and make sure "Add python.exe to PATH" is checked during install.
    echo.
    pause
    exit /b 1
)

echo.
echo [1/4] Installing runtime dependencies...
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
if errorlevel 1 goto :error

echo.
echo [2/4] Installing build tools (cx_Freeze, PyInstaller)...
python -m pip install cx_Freeze pyinstaller
if errorlevel 1 goto :error

echo.
echo [3/4] Building standalone EXE with PyInstaller...
python -m PyInstaller --onefile --windowed --name BreakoutScannerGlobalMarkets ^
    --hidden-import=yfinance --hidden-import=pandas --hidden-import=pytz ^
    --hidden-import=requests --hidden-import=reportlab breakout_scanner_app.py
if errorlevel 1 goto :error

echo.
echo [4/4] Building MSI installer with cx_Freeze...
python setup_freeze.py bdist_msi
if errorlevel 1 goto :error

echo.
echo ============================================================
echo   BUILD COMPLETE
echo   - Standalone EXE : dist\BreakoutScannerGlobalMarkets.exe
echo   - MSI Installer  : dist\*.msi
echo ============================================================
pause
exit /b 0

:error
echo.
echo ============================================================
echo   BUILD FAILED - see the error above.
echo ============================================================
pause
exit /b 1
