Name: BreakoutScannerGlobalMarkets
Version: 2.0.1
Release: 1
Summary: Breakout Scanner Global Markets - multi-market stock scanner
License: Proprietary
URL: https://github.com/yashjani99/breakout-scanner-global-markets

%description
Breakout Scanner Global Markets - Professional multi-market NSE/TSX/NYSE/LSE stock breakout scanner
with automated stop loss and target calculations. Bundles Python runtime and all dependencies.

# Only require actual system libraries, NOT bundled ones
Requires: libxcb >= 1.11, libxkbcommon >= 0.5, libxkbcommon-x11 >= 0.5
Requires: dbus-libs >= 1.8, mesa-libGL >= 18.0, mesa-libEGL >= 18.0

# Tell rpm to NOT scan bundled libraries for dependencies
%global __requires_exclude_from ^/opt/.*\.so.*$

%files
/opt/BreakoutScannerGlobalMarkets/
/usr/bin/BreakoutScannerGlobalMarkets
/usr/share/applications/BreakoutScannerGlobalMarkets.desktop
/usr/share/pixmaps/BreakoutScannerGlobalMarkets.png

%post
chmod +x /opt/BreakoutScannerGlobalMarkets/BreakoutScannerGlobalMarkets
ln -sf /opt/BreakoutScannerGlobalMarkets/BreakoutScannerGlobalMarkets /usr/bin/BreakoutScannerGlobalMarkets 2>/dev/null || true

%preun
rm -f /usr/bin/BreakoutScannerGlobalMarkets 2>/dev/null || true

%postun
rm -rf /opt/BreakoutScannerGlobalMarkets 2>/dev/null || true

