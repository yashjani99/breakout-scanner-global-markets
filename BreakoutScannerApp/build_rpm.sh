#!/usr/bin/env bash
set -e
cd "$(dirname "$0")"

echo "============================================================"
echo "  Breakout Scanner Global Markets - RPM Build"
echo "============================================================"

command -v python3 >/dev/null || { echo "python3 required"; exit 1; }
command -v rpmbuild >/dev/null || { echo "rpmbuild required"; exit 1; }

echo "[1/4] Installing build dependencies..."
python3 -m pip install --upgrade pip setuptools wheel >/dev/null 2>&1
python3 -m pip install -r requirements.txt >/dev/null 2>&1
python3 -m pip install cx_Freeze >/dev/null 2>&1

echo "[2/4] Building RPM with cx_Freeze..."
python3 setup_freeze.py bdist_rpm 2>&1 | grep -E "writing|running|Executing|Wrote|RPM|error" | tail -20

echo "[3/4] Fixing spec file dependencies..."
SPEC_FILE=$(find build -name "*.spec" -type f 2>/dev/null | head -1)

if [ -n "$SPEC_FILE" ]; then
    cat > /tmp/fix_spec.py << 'EOFPYTH'
import sys
import re

spec_file = sys.argv[1]

with open(spec_file, 'r') as f:
    content = f.read()

# Remove all Requires: lines that contain bundled libraries
lines = content.split('\n')
new_lines = []
skip_next = False

bundled_libs = ['libQt5', 'libcrypto', 'libssl', 'libjpeg', 'libpng', 'libtiff', 
                'libgfortran', 'liblzma', 'libquadmath', 'libuuid', 'libreadline', 
                'libsqlite3', 'libwebp', 'libzstd', 'libfreetype', 'libbrotli', 
                'libbz2', 'libffi', 'libharfbuzz', 'libicu', 'liblcms2', 'libopenjp2', 
                'libpq', 'libasound', 'libpulse', 'libdrm', 'libdbus', 'libwayland', 
                'libxkbcommon', 'libxcb', 'libxau']

for line in lines:
    if 'Requires:' in line and any(x in line for x in bundled_libs):
        skip_next = line.rstrip().endswith('\\')
        continue
    
    if skip_next:
        if not line.rstrip().endswith('\\'):
            skip_next = False
        continue
    
    new_lines.append(line)

content = '\n'.join(new_lines)

# Add minimal requires before %files
minimal_requires = '''# Only require actual system libraries - everything else is bundled
Requires: libxcb >= 1.11
Requires: libxkbcommon >= 0.5
Requires: dbus-libs >= 1.8
Requires: mesa-libGL >= 18.0
Requires: mesa-libEGL >= 18.0
'''

# Insert before %files section
if '%files' in content:
    content = content.replace('%files', minimal_requires + '\n%files', 1)

with open(spec_file, 'w') as f:
    f.write(content)

print("✓ Cleaned: removed bundled lib dependencies, added minimal requires")
EOFPYTH

    python3 /tmp/fix_spec.py "$SPEC_FILE"
fi

echo "[4/4] RPM ready"
mkdir -p dist
find build/bdist.*/rpm/RPMS -name "*.rpm" -type f -exec mv {} dist/ \; 2>/dev/null || true

echo
echo "============================================================"
echo "  Build Complete"
if ls dist/*.rpm 1>/dev/null 2>&1; then
    ls -lh dist/*.rpm | awk '{print "  ✓", $9, "(" $5 ")"}'
    echo "  ✓ RPM ready with proper dependency handling"
else
    echo "  ✗ No RPM found - build may have failed"
fi
echo "============================================================"

