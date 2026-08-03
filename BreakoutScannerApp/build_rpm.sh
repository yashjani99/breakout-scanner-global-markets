#!/usr/bin/env bash
set -e
cd "$(dirname "$0")"

echo "============================================================"
echo "  Breakout Scanner Global Markets - RPM Build"
echo "============================================================"

# Check prerequisites
command -v python3 >/dev/null || { echo "python3 required"; exit 1; }
command -v rpmbuild >/dev/null || { echo "rpmbuild required"; exit 1; }

echo "[1/4] Installing pip and build tools..."
python3 -m pip install --upgrade pip setuptools wheel

echo "[2/4] Installing cx_Freeze and dependencies..."
python3 -m pip install cx_Freeze

echo "[3/4] Building executable..."
python3 setup_freeze.py bdist_rpm

echo "[4/4] Creating clean RPM..."
mkdir -p rpmbuild/{SPECS,SOURCES,RPMS,BUILD}

# Create spec file
cat > rpmbuild/SPECS/breakout-scanner.spec << 'EOFSPEC'
Name: BreakoutScannerGlobalMarkets
Version: 2.0.1
Release: 1
Summary: Breakout Scanner - Multi-market stock scanner
License: Proprietary
URL: https://github.com/yashjani99/breakout-scanner-global-markets

%description
Professional stock breakout scanner.
Bundles Python runtime and all dependencies.

Requires: libxcb >= 1.11, libxkbcommon >= 0.5, libxkbcommon-x11 >= 0.5
Requires: dbus-libs >= 1.8, mesa-libGL >= 18.0, mesa-libEGL >= 18.0

%global __requires_exclude_from ^/opt/.*\.so.*$
%global __requires_exclude libQt5|libcrypto|libssl|libjpeg|libpng|libtiff

%prep
%setup -q

%build

%install
mkdir -p %{buildroot}/opt/BreakoutScannerGlobalMarkets
mkdir -p %{buildroot}/usr/bin

find . -name "BreakoutScannerGlobalMarkets" -type f -executable 2>/dev/null | head -1 | xargs -I {} cp {} %{buildroot}/opt/BreakoutScannerGlobalMarkets/ || true

find . -name "lib" -type d 2>/dev/null | head -1 | xargs -I {} cp -r {} %{buildroot}/opt/BreakoutScannerGlobalMarkets/ || true

chmod +x %{buildroot}/opt/BreakoutScannerGlobalMarkets/BreakoutScannerGlobalMarkets 2>/dev/null || true

cat > %{buildroot}/usr/bin/BreakoutScannerGlobalMarkets << 'EOF'
#!/bin/bash
exec /opt/BreakoutScannerGlobalMarkets/BreakoutScannerGlobalMarkets "$@"
EOF
chmod +x %{buildroot}/usr/bin/BreakoutScannerGlobalMarkets

%files
/opt/BreakoutScannerGlobalMarkets/
/usr/bin/BreakoutScannerGlobalMarkets

%post
chmod +x /usr/bin/BreakoutScannerGlobalMarkets 2>/dev/null || true

%postun
rm -rf /opt/BreakoutScannerGlobalMarkets 2>/dev/null || true

%changelog
* Fri Aug 02 2026 Yash Jani <yash@example.com> - 2.0.1-1
- Fix RPM dependency scanning
EOFSPEC

# Use the RPM spec that cx_Freeze generated if available, otherwise use ours
SPEC_FILE=$(find build -name "*.spec" -type f 2>/dev/null | head -1)

if [ -z "$SPEC_FILE" ]; then
    echo "  Using custom spec file"
    SPEC_FILE="rpmbuild/SPECS/breakout-scanner.spec"
    cp dist/* rpmbuild/SOURCES/ 2>/dev/null || true
else
    echo "  Found cx_Freeze spec: $SPEC_FILE"
    # Patch it to exclude bundled libraries
    sed -i '/%global/!b; /requires_exclude/!b; a %global __requires_exclude_from ^/opt/.*\.so.*$' "$SPEC_FILE"
fi

# Build RPM
rpmbuild -bb "$SPEC_FILE" \
  --define "_topdir $(pwd)/rpmbuild" \
  --define "_builddir $(pwd)/build" \
  --define "_sourcedir $(pwd)/dist" 2>&1 | tail -30

# Move RPM to dist
mkdir -p dist
find rpmbuild/RPMS -name "*.rpm" -type f -exec mv {} dist/ \; 2>/dev/null || true

echo
echo "============================================================"
echo "  Build Complete"
ls -lh dist/*.rpm 2>/dev/null && echo "  ✓ RPM ready" || echo "  ✗ Build failed - check output above"
echo "============================================================"

