#!/usr/bin/env bash
set -e
cd "$(dirname "$0")"

echo "============================================================"
echo "  Breakout Scanner Global Markets - RPM Build"
echo "============================================================"

# Check prerequisites
command -v python3 >/dev/null || { echo "python3 required"; exit 1; }
command -v rpmbuild >/dev/null || { echo "rpmbuild required"; exit 1; }

echo "[1/3] Installing dependencies..."
python3 -m pip install --upgrade pip >/dev/null 2>&1
python3 -m pip install -r requirements.txt >/dev/null 2>&1
python3 -m pip install cx_Freeze >/dev/null 2>&1

echo "[2/3] Building executable with cx_Freeze..."
python3 -m PyInstaller --onefile --windowed \
  --name BreakoutScannerGlobalMarkets \
  --hidden-import=yfinance --hidden-import=pandas \
  --hidden-import=pytz --hidden-import=requests \
  breakout_scanner_app.py

echo "[3/3] Creating RPM..."
mkdir -p rpmbuild/{SPECS,SOURCES,RPMS}

# Create clean spec file
cat > rpmbuild/SPECS/breakout-scanner.spec << 'EOFSPEC'
Name: BreakoutScannerGlobalMarkets
Version: 2.0.1
Release: 1
Summary: Breakout Scanner - Multi-market stock scanner
License: Proprietary
URL: https://github.com/yashjani99/breakout-scanner-global-markets

%description
Professional stock breakout scanner for NSE, TSX, NYSE, LSE markets.
Bundles Python runtime and all dependencies. No installation required.

Requires: libxcb >= 1.11, libxkbcommon >= 0.5, libxkbcommon-x11 >= 0.5
Requires: dbus-libs >= 1.8, mesa-libGL >= 18.0, mesa-libEGL >= 18.0

%global __requires_exclude_from ^/opt/.*\.so.*$
%global __requires_exclude libQt5|libcrypto|libssl|libjpeg|libpng|libtiff

%prep
%setup -q -n BreakoutScannerGlobalMarkets

%build

%install
mkdir -p %{buildroot}/opt/BreakoutScannerGlobalMarkets
mkdir -p %{buildroot}/usr/bin
mkdir -p %{buildroot}/usr/share/applications
mkdir -p %{buildroot}/usr/share/pixmaps

cp -r dist/BreakoutScannerGlobalMarkets/* %{buildroot}/opt/BreakoutScannerGlobalMarkets/
chmod +x %{buildroot}/opt/BreakoutScannerGlobalMarkets/BreakoutScannerGlobalMarkets

cat > %{buildroot}/usr/bin/BreakoutScannerGlobalMarkets << 'EOF'
#!/bin/bash
exec /opt/BreakoutScannerGlobalMarkets/BreakoutScannerGlobalMarkets "$@"
EOF
chmod +x %{buildroot}/usr/bin/BreakoutScannerGlobalMarkets

%files
/opt/BreakoutScannerGlobalMarkets/
/usr/bin/BreakoutScannerGlobalMarkets

%post
chmod +x /usr/bin/BreakoutScannerGlobalMarkets

%postun
rm -rf /opt/BreakoutScannerGlobalMarkets 2>/dev/null || true

%changelog
* Fri Aug 02 2026 Yash Jani <yash@example.com> - 2.0.1-1
- Fix RPM dependency scanning for bundled libraries
EOFSPEC

# Copy dist to rpmbuild
cp -r dist rpmbuild/SOURCES/BreakoutScannerGlobalMarkets-2.0.1

# Build RPM
cd rpmbuild
rpmbuild -bb SPECS/breakout-scanner.spec \
  --define "_topdir $(pwd)" \
  --define "_builddir $(pwd)/SOURCES" \
  2>&1 | tail -20

cd ..
mkdir -p dist
mv rpmbuild/RPMS/x86_64/*.rpm dist/ 2>/dev/null || true

echo "============================================================"
echo "  Build Complete"
ls -lh dist/*.rpm 2>/dev/null || echo "  ✗ No RPM generated - check errors above"
echo "============================================================"

