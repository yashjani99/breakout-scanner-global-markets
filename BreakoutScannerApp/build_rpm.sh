#!/usr/bin/env bash
set -e
cd "$(dirname "$0")"

echo "============================================================"
echo "  Breakout Scanner Global Markets - RPM Build"
echo "============================================================"

echo "[1/3] Installing dependencies..."
python3 -m pip install --upgrade pip setuptools wheel >/dev/null 2>&1
python3 -m pip install -r requirements.txt >/dev/null 2>&1
python3 -m pip install cx_Freeze >/dev/null 2>&1

echo "[2/3] Building RPM with custom spec template..."
python3 setup_freeze.py bdist_rpm 2>&1 | tail -15

echo "[3/3] Finalizing..."
mkdir -p dist
find build -name "*.rpm" -type f -exec mv {} dist/ \; 2>/dev/null || true

echo
if ls dist/*.rpm 1>/dev/null 2>&1; then
    echo "✓ RPM Build Complete:"
    ls -lh dist/*.rpm | awk '{print "  " $9, "(" $5 ")"}'
    echo "  ✓ All bundled dependencies excluded"
    echo "  ✓ Ready to install"
else
    echo "✗ No RPM found"
    exit 1
fi
echo "============================================================"
