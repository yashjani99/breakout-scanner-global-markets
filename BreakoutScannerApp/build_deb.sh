#!/usr/bin/env bash
# Run this ON a Debian/Ubuntu machine (or anything with dpkg-deb).
# cx_Freeze has no built-in .deb target, so this stages the frozen build
# output into a standard /opt install + /usr/bin shim + .desktop entry and
# packs it with dpkg-deb. The end user needs nothing pre-installed - the
# full Python runtime and all dependencies are bundled.
set -e
cd "$(dirname "$0")"

APP_NAME="breakout-scanner-indian-market"
APP_TITLE="Breakout Scanner Global Markets"
VERSION="2.0.1"
MAINTAINER="Yash Jani"
ARCH="amd64"

echo "============================================================"
echo "  ${APP_TITLE} v${VERSION} - Linux DEB Build"
echo "============================================================"

if ! command -v python3 >/dev/null 2>&1; then
    echo "python3 not found. Install it first (e.g. sudo apt install python3 python3-pip)."
    exit 1
fi

if ! command -v dpkg-deb >/dev/null 2>&1; then
    echo "dpkg-deb not found. Install it first: sudo apt install dpkg-dev"
    exit 1
fi

echo
echo "[1/4] Installing runtime dependencies..."
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt

echo
echo "[2/4] Installing cx_Freeze..."
python3 -m pip install cx_Freeze

echo
echo "[3/4] Freezing the application..."
rm -rf build
python3 setup_freeze.py build_exe

FROZEN_DIR=$(find build -maxdepth 1 -type d -name "exe.linux-*" | head -n1)
if [ -z "$FROZEN_DIR" ]; then
    echo "Could not find frozen build output under build/exe.linux-*"
    exit 1
fi

echo
echo "[4/4] Assembling .deb package..."
STAGE="dist/deb_stage"
rm -rf "$STAGE"
INSTALL_DIR="$STAGE/opt/${APP_NAME}"
mkdir -p "$INSTALL_DIR"
cp -r "$FROZEN_DIR"/* "$INSTALL_DIR"/

mkdir -p "$STAGE/usr/bin"
cat > "$STAGE/usr/bin/${APP_NAME}" <<EOF
#!/bin/sh
exec /opt/${APP_NAME}/BreakoutScannerIndianMarket "\$@"
EOF
chmod +x "$STAGE/usr/bin/${APP_NAME}"
chmod +x "$INSTALL_DIR/BreakoutScannerIndianMarket"

mkdir -p "$STAGE/usr/share/applications"
cat > "$STAGE/usr/share/applications/${APP_NAME}.desktop" <<EOF
[Desktop Entry]
Type=Application
Name=${APP_TITLE}
Comment=Multi-market breakout scanner (NSE, TSX, NYSE, LSE and more)
Exec=/usr/bin/${APP_NAME}
Icon=${APP_NAME}
Terminal=false
Categories=Office;Finance;
EOF

SIZE_KB=$(du -sk "$STAGE" | cut -f1)

mkdir -p "$STAGE/DEBIAN"
cat > "$STAGE/DEBIAN/control" <<EOF
Package: ${APP_NAME}
Version: ${VERSION}
Section: office
Priority: optional
Architecture: ${ARCH}
Installed-Size: ${SIZE_KB}
Maintainer: ${MAINTAINER}
Description: ${APP_TITLE}
 Multi-market NSE/TSX/NYSE/LSE/... breakout scanner with SL/T1/T2/T3
 targets, a live results table, and Excel/PDF export.
 All dependencies (Python runtime, PyQt5, pandas, yfinance, reportlab)
 are bundled - nothing else needs to be installed.
EOF

dpkg-deb --build --root-owner-group "$STAGE" "dist/${APP_NAME}_${VERSION}_${ARCH}.deb"

echo
echo "============================================================"
echo "  BUILD COMPLETE - dist/${APP_NAME}_${VERSION}_${ARCH}.deb"
echo "============================================================"
