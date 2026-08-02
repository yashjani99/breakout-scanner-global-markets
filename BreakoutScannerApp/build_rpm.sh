#!/usr/bin/env bash
# Run this ON a Linux machine (Fedora/RHEL/openSUSE, or any distro with
# rpmbuild installed). Produces a self-contained .rpm - the end user needs
# nothing pre-installed, everything (Python runtime, PyQt5, pandas,
# yfinance, reportlab) is bundled by cx_Freeze.
set -e
cd "$(dirname "$0")"

echo "============================================================"
echo "  Breakout Scanner Global Markets - Linux RPM Build"
echo "============================================================"

if ! command -v python3 >/dev/null 2>&1; then
    echo "python3 not found. Install it first (e.g. sudo dnf install python3 python3-pip)."
    exit 1
fi

if ! command -v rpmbuild >/dev/null 2>&1; then
    echo "rpmbuild not found. Install it first:"
    echo "  Fedora/RHEL   : sudo dnf install rpm-build"
    echo "  openSUSE      : sudo zypper install rpm-build"
    echo "  Debian/Ubuntu : sudo apt install rpm"
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
echo "[3/3] Building RPM package..."
python3 setup_freeze.py bdist_rpm

echo
echo "============================================================"
echo "  BUILD COMPLETE - see dist/*.rpm"
echo "============================================================"
