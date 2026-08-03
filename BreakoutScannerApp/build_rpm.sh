#!/usr/bin/env bash
set -e
cd "$(dirname "$0")"

echo "============================================================"
echo "  Breakout Scanner Global Markets - RPM Build"
echo "============================================================"

command -v python3 >/dev/null || { echo "python3 required"; exit 1; }
command -v rpmbuild >/dev/null || { echo "rpmbuild required"; exit 1; }

echo "[1/3] Installing build dependencies..."
python3 -m pip install --upgrade pip setuptools wheel
python3 -m pip install -r requirements.txt
python3 -m pip install cx_Freeze

echo "[2/3] Building RPM with cx_Freeze..."
python3 setup_freeze.py bdist_rpm

echo "[3/3] Patching spec to exclude bundled libraries..."
SPEC_FILE=$(find build -name "*.spec" -type f 2>/dev/null | head -1)

if [ -n "$SPEC_FILE" ]; then
    # Insert %global directives right after Release line using sed
    sed -i '/^Release:/a %global __requires_exclude_from ^/opt/.*\\.so.*$\n%global __requires_exclude libQt5|libcrypto|libssl|libjpeg|libpng|libtiff|libgfortran|liblzma|libquadmath|libuuid|libreadline|libsqlite3|libwebp|libzstd|libXau|libfreetype|libbrotli|libbz2|libffi|libharfbuzz|libicu|liblcms2|libopenjp2|libpq|libasound|libpulse|libdrm|libdbus|libwayland|libxkbcommon|libxcb' "$SPEC_FILE"
    
    # Rebuild RPM with patched spec
    echo "  Rebuilding with patched spec..."
    rpmbuild -bb "$SPEC_FILE" \
      --define "_topdir $(dirname $SPEC_FILE)/.." \
      --define "_builddir $(dirname $SPEC_FILE)/../../BUILD" 2>&1 | tail -10
fi

mkdir -p dist
find build/bdist.*/rpm/RPMS -name "*.rpm" -type f -exec mv {} dist/ \; 2>/dev/null || true

echo
echo "============================================================"
ls -lh dist/*.rpm 2>/dev/null && echo "✓ RPM ready" || echo "✗ No RPM found"
echo "============================================================"

