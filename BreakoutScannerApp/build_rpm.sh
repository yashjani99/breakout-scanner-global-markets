#!/usr/bin/env bash
set -e
cd "$(dirname "$0")"

echo "============================================================"
echo "  Breakout Scanner Global Markets - RPM Build"
echo "============================================================"

echo "[1/4] Installing dependencies..."
python3 -m pip install --upgrade pip setuptools wheel >/dev/null 2>&1
python3 -m pip install -r requirements.txt >/dev/null 2>&1
python3 -m pip install cx_Freeze >/dev/null 2>&1

echo "[2/4] Freezing application..."
# Build just the executable, don't use bdist_rpm
python3 setup_freeze.py build_exe 2>&1 | tail -5

# Get the frozen app location
FROZEN_APP=$(find build/exe.* -maxdepth 0 -type d | head -1)
if [ -z "$FROZEN_APP" ]; then
    echo "ERROR: Frozen app not found"
    exit 1
fi

echo "[3/4] Creating RPM package..."

# Prepare RPM build directories
mkdir -p rpmbuild/{SPECS,SOURCES,BUILD,RPMS/x86_64,SRPMS}

# Create the spec file with NO automatic requires
cat > rpmbuild/SPECS/BreakoutScannerGlobalMarkets.spec << 'EOFSPEC'
%define __find_requires %{nil}
%define __find_provides %{nil}

Name: BreakoutScannerGlobalMarkets
Version: 2.0.4
Release: 1
Summary: Breakout Scanner Global Markets
License: Proprietary
Group: Applications/Productivity
Vendor: Yash Jani
Packager: Yash Jani
URL: https://github.com/yashjani99/breakout-scanner-global-markets

AutoReqProv: no

Requires: libxcb >= 1.11
Requires: libxkbcommon >= 0.5
Requires: dbus-libs >= 1.8
Requires: mesa-libGL >= 18.0

%description
Breakout Scanner Global Markets - Professional stock breakout scanner
for NSE, TSX, NYSE, LSE and other global markets.

%prep

%build

%install
mkdir -p %{buildroot}/opt/BreakoutScannerGlobalMarkets
cp -r %{_sourcedir}/app/* %{buildroot}/opt/BreakoutScannerGlobalMarkets/
mkdir -p %{buildroot}/usr/bin
install -m 755 /dev/stdin %{buildroot}/usr/bin/BreakoutScannerGlobalMarkets << 'WRAPPER'
#!/bin/bash
exec /opt/BreakoutScannerGlobalMarkets/BreakoutScannerGlobalMarkets "$@"
WRAPPER
mkdir -p %{buildroot}/usr/share/applications
cat > %{buildroot}/usr/share/applications/breakout-scanner.desktop << 'ENDDESKTOP'
[Desktop Entry]
Type=Application
Name=Breakout Scanner Global Markets
Comment=Professional stock breakout scanner for global markets
Exec=/usr/bin/BreakoutScannerGlobalMarkets
Icon=application-x-executable
Categories=Office;Finance;Utility;
Terminal=false
ENDDESKTOP
chmod 644 %{buildroot}/usr/share/applications/breakout-scanner.desktop

%files
%defattr(-,root,root,-)
/opt/BreakoutScannerGlobalMarkets
/usr/bin/BreakoutScannerGlobalMarkets
/usr/share/applications/breakout-scanner.desktop

%changelog
* Mon Aug 02 2024 Yash Jani <yashjani.ca@gmail.com>
- Initial release

EOFSPEC

# Copy frozen app to source for spec to use
cp -r "$FROZEN_APP" rpmbuild/SOURCES/app

# Build RPM
rpmbuild -bb --define="_topdir $(pwd)/rpmbuild" rpmbuild/SPECS/BreakoutScannerGlobalMarkets.spec 2>&1 | tail -5

echo "[4/4] Finalizing..."
mkdir -p dist
mv rpmbuild/RPMS/x86_64/*.rpm dist/ 2>/dev/null || true

echo
if ls dist/*.rpm 1>/dev/null 2>&1; then
    echo "✓ RPM Build Complete:"
    ls -lh dist/*.rpm | awk '{print "  " $9, "(" $5 ")"}'
    echo "  ✓ No automatic requires scanning"
    echo "  ✓ Only minimal system libraries required"
    echo "  ✓ Ready to install"
else
    echo "✗ No RPM found"
    exit 1
fi
echo "============================================================"
