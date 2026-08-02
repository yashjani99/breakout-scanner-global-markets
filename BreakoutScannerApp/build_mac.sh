#!/usr/bin/env bash
# Run this ON a Mac. cx_Freeze's bdist_dmg builds a .app bundle and wraps
# it into a drag-to-Applications .dmg installer. The end user needs
# nothing pre-installed - the full Python runtime and all dependencies
# (PyQt5, pandas, yfinance, reportlab) are bundled inside the .app.
set -e
cd "$(dirname "$0")"

echo "============================================================"
echo "  Breakout Scanner Global Markets - macOS DMG Build"
echo "============================================================"

if ! command -v python3 >/dev/null 2>&1; then
    echo "python3 not found. Install it first: https://www.python.org/downloads/macos/"
    echo "(or 'brew install python@3.12' if you use Homebrew)"
    exit 1
fi

echo
echo "[1/3] Installing runtime dependencies..."
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt

echo
echo "[2/3] Installing cx_Freeze..."
python3 -m pip install cx_Freeze

echo
echo "[3/3] Building .app and .dmg..."
python3 setup_freeze.py bdist_dmg

# cx_Freeze's bdist_dmg stages everything under build/dist/... rather than
# the top-level dist/ that bdist_msi and bdist_rpm use, so locate whatever
# .dmg it produced and copy it into dist/ ourselves.
mkdir -p dist
DMG_FILE=$(find build -iname "*.dmg" | head -n1)
if [ -z "$DMG_FILE" ]; then
    echo "ERROR: bdist_dmg reported success but no .dmg file was found under build/"
    exit 1
fi
cp "$DMG_FILE" dist/
echo "Copied: $DMG_FILE -> dist/$(basename "$DMG_FILE")"

echo
echo "============================================================"
echo "  BUILD COMPLETE - see dist/*.dmg"
echo "============================================================"
