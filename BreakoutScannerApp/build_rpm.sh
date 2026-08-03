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
    exit 1
fi

echo
echo "[1/4] Installing dependencies..."
python3 -m pip install --upgrade pip 2>&1 | grep -v "already satisfied"
python3 -m pip install -r requirements.txt 2>&1 | grep -v "already satisfied"
python3 -m pip install cx_Freeze 2>&1 | grep -v "already satisfied"

echo
echo "[2/4] Building with cx_Freeze..."
python3 setup_freeze.py bdist_rpm

echo
echo "[3/4] Fixing RPM spec to exclude bundled libraries..."
# Find the generated spec file
SPEC_FILE=$(find build -name "*.spec" -type f 2>/dev/null | head -1)

if [ -z "$SPEC_FILE" ]; then
    echo "ERROR: Could not find generated .spec file"
    exit 1
fi

echo "  Spec file: $SPEC_FILE"

# Create a backup
cp "$SPEC_FILE" "${SPEC_FILE}.bak"

# Remove the old spec file from dist if it exists
rm -f dist/*.spec 2>/dev/null || true

# Add the critical exclude directives at the beginning of %prep or %build section
python3 << 'EOFPYTHON'
import re

spec_file = """SPEC_FILE"""

with open(spec_file, 'r') as f:
    content = f.read()

# Add the exclude directives after Name/Version/Release and before %description
exclude_directives = '''# Exclude bundled libraries from dependency scanning
%global __requires_exclude_from ^/opt/.*\.so.*$
%global __requires_exclude libQt5|libcrypto|libssl|libjpeg|libpng|libtiff|libgfortran|liblzma|libquadmath|libuuid
'''

# Insert after the Release line
pattern = r'(Release:\s+\d+)'
replacement = r'\1\n' + exclude_directives
content = re.sub(pattern, replacement, content)

with open(spec_file, 'w') as f:
    f.write(content)

print("✓ Added bundled library excludes to spec")
EOFPYTHON

echo "  ✓ Spec file patched successfully"

echo
echo "[4/4] Rebuilding RPM with fixed spec..."
cd build
rpmbuild -bb "${SPEC_FILE#*/build/}" --define "_rpmdir $(pwd)/dist" 2>&1 | tail -5
cd ..

# Move RPM to dist folder
mkdir -p dist
find build/dist -name "*.rpm" -type f -exec mv {} dist/ \; 2>/dev/null || true

echo
echo "============================================================"
echo "  BUILD COMPLETE"
ls -lh dist/*.rpm 2>/dev/null | awk '{print "  ✓", $9, "(" $5 ")"}'
echo "============================================================"

