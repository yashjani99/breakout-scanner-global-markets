#!/usr/bin/env bash
set -e
cd "$(dirname "$0")"

echo "============================================================"
echo "  Breakout Scanner Global Markets - Linux RPM Build"
echo "============================================================"

if ! command -v python3 >/dev/null 2>&1; then
    echo "python3 not found. Install it first."
    exit 1
fi

if ! command -v rpmbuild >/dev/null 2>&1; then
    echo "rpmbuild not found. Install it first:"
    echo "  Fedora/RHEL   : sudo dnf install rpm-build"
    echo "  openSUSE      : sudo zypper install rpm-build"
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
echo "[4/4] Fixing spec file to exclude bundled library dependencies..."
SPEC_FILE=$(find dist -name "*.spec" -type f | head -1)
if [ -n "$SPEC_FILE" ]; then
    # Add directive to NOT scan bundled libraries for dependencies
    sed -i '/^%files/i %global __requires_exclude_from ^/opt/.*\.so.*$\n%global __requires_exclude libQt5Bodymovin|libcrypto|libssl|libjpeg|libpng|libtiff|libgfortran|liblzma|libquadmath|libuuid' "$SPEC_FILE"
    echo "  ✓ Spec file updated to exclude bundled libraries"
fi

echo
echo "============================================================"
echo "  BUILD COMPLETE - see dist/*.rpm"
echo "============================================================"
