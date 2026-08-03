#!/usr/bin/env bash
set -e
cd "$(dirname "$0")"

echo "============================================================"
echo "  Breakout Scanner Global Markets - RPM Build"
echo "============================================================"

# Install build deps
echo "[1/4] Installing dependencies..."
python3 -m pip install --upgrade pip setuptools wheel >/dev/null 2>&1
python3 -m pip install -r requirements.txt >/dev/null 2>&1
python3 -m pip install cx_Freeze >/dev/null 2>&1

# Build with cx_Freeze bdist_rpm
echo "[2/4] Building with cx_Freeze..."
python3 setup_freeze.py bdist_rpm 2>&1 | tail -15

# Find the generated spec file
SPEC_FILE=$(find build -name "*.spec" -type f 2>/dev/null | head -1)
if [ -z "$SPEC_FILE" ]; then
    echo "ERROR: No spec file found"
    exit 1
fi

echo "[3/4] Disabling automatic requires..."

# Use sed to add the directives at the very top of the spec
# This ensures rpmbuild sees them before it scans anything
sed -i '1i%define __find_requires %{nil}\n%define __find_provides %{nil}\nAutoReqProv: no' "$SPEC_FILE"

# Remove all the bundled library requires using sed
# Match lines starting with Requires: and containing versioned .so names or Qt5 libraries
sed -i '/^Requires:.*\(libQt5\|libcrypto\|libssl\|libjpeg\|libpng\|libtiff\|libgfortran\|liblzma\|libquadmath\|libuuid\|\.so\|[(]64bit[)]\|[(]OPENSSL\|[(]GFORTRAN\|[(]LIBJPEG\|[(]XZ_\|[(]PNG\|[(]QUADMATH\|[(]LIBTIFF\|[(]UUID_\|[(]Qt_\)/d' "$SPEC_FILE"

# Add minimal requires after the Name: field
sed -i '/^Name:/a\
\
Requires: libxcb >= 1.11\
Requires: libxkbcommon >= 0.5\
Requires: dbus-libs >= 1.8\
Requires: mesa-libGL >= 18.0' "$SPEC_FILE"

echo "  ✓ Spec: auto requires disabled"
echo "  ✓ Spec: bundled lib dependencies removed"
echo "  ✓ Spec: minimal system requires added"

# Rebuild using the cleaned spec
echo "[4/4] Building RPM..."
RPM_DIR=$(dirname "$SPEC_FILE")
cd "$RPM_DIR"
rpmbuild -bb --define="_topdir $(pwd)" --noprov "$(basename $SPEC_FILE)" 2>&1 | tail -3
cd ../..

# Move RPM to dist
mkdir -p dist
find build -name "*.rpm" -type f -exec mv {} dist/ \; 2>/dev/null || true

echo
if ls dist/*.rpm 1>/dev/null 2>&1; then
    echo "✓ RPM Build Complete:"
    ls -lh dist/*.rpm | awk '{print "  " $9, "(" $5 ")"}'
else
    echo "✗ No RPM found"
    exit 1
fi
echo "============================================================"

